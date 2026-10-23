---
name: spring-boot-architecture
description: Architect and maintain enterprise Spring Boot 3+ microservices utilizing layered domain architecture, virtual threads, and production connection pool tuning based on real-world outage postmortems.
---

# Enterprise Spring Boot Architecture & Resilience

## Purpose & Scope
This skill provides standards for structuring enterprise Spring Boot microservices with Spring Data JPA, Spring Security, and Project Loom virtual threads.

---

## Real-Life Incident Case: The Silent HikariCP Connection Leak

### Background & What Happened
Under sudden peak load (8,000 requests/sec), an enterprise banking transaction service stopped responding. CPU on the JVM was low (< 20%), but HTTP 500 errors surged with:
```text
org.springframework.transaction.CannotCreateTransactionException: Could not open JPA EntityManager for transaction
Caused by: java.sql.SQLTransientConnectionException: HikariPool-1 - Connection is not available, request timed out after 30000ms.
```
Pods failed readiness probes and restarted continuously, worsening the cascading failure.

### Real-Time Live Triage Protocol
The SRE agent executed the following live diagnostic steps:

#### 1. Inspect Thread States via JVM Thread Dump
```bash
# Capture thread dump inside container
jcmd 1 Thread.print > /tmp/threaddump.txt

# Grep for threads blocked on HikariCP borrow
grep -A 10 "HikariPool-1 connection getter" /tmp/threaddump.txt
```
*Result:* 150 worker threads were blocked in `TIMED_WAITING` waiting to borrow a database connection from HikariCP.

#### 2. Inspect Connection Leak Detection Threshold
By default, HikariCP does not log unreturned connections. The agent activated leak detection dynamically via Spring Actuator:
```bash
curl -X POST http://localhost:8080/actuator/env -H 'Content-Type: application/json' \
  -d '{"name":"spring.datasource.hikari.leak-detection-threshold","value":"5000"}'
```
*Root Cause:* A third-party webhook call was invoked inside a `@Transactional` boundary. When the external webhook hung for 25 seconds, the database connection remained locked, draining the pool of all 10 connections.

---

## Production Architecture Standard: Decouple External IO from `@Transactional`

### The Anti-Pattern (Connection Leak)
```java
@Transactional
public void processOrder(OrderRequest request) {
    Order order = orderRepository.save(new Order(request));
    // DANGEROUS: Holding DB connection open while performing slow external HTTP IO
    paymentGatewayClient.charge(order.getAmount()); 
}
```

### The Production Standard (Surgical Isolation)
```java
@Service
public class OrderService {
    private final OrderRepository orderRepository;
    private final PaymentGatewayClient paymentGatewayClient;

    public void processOrder(OrderRequest request) {
        // 1. Database write in short-lived transaction
        Order order = savePendingOrder(request);

        // 2. Slow external network call executed OUTSIDE transaction boundary
        PaymentResult result = paymentGatewayClient.charge(order.getAmount());

        // 3. Second short-lived transaction to update final status
        updateOrderStatus(order.getId(), result.getStatus());
    }

    @Transactional
    public Order savePendingOrder(OrderRequest request) {
        return orderRepository.save(new Order(request));
    }

    @Transactional
    public void updateOrderStatus(Long orderId, String status) {
        orderRepository.updateStatus(orderId, status);
    }
}
```

---

## Continuous Self-Knowledge Enhancement Loop

When the agent triages a connection exhaustion outage:
1. **Isolate Architectural Flaw:** Detect `@Transactional` wrapping external network or messaging calls.
2. **Auto-Generate Static Analysis Rule:** Add an architectural check in [`agents/7-agent-master-suite/devsecops-reviewer.md`](../../../agents/7-agent-master-suite/devsecops-reviewer.md) to flag `@Transactional` on methods calling external REST/gRPC clients.
3. **Update Memory:** Record the HikariCP `leak-detection-threshold` debugging trick in `AGENTS.md` under `## Learned JVM Runtime Facts`.

