# OpenTelemetry Semantic Conventions Cheat Sheet

## 1. HTTP Server Spans
- **Span Name:** Must be low-cardinality route template (e.g. `GET /v1/users/{userId}`, NOT `GET /v1/users/12345`).
- **Required Attributes:**
  - `http.method`: `GET`, `POST`, `PUT`, `DELETE`
  - `http.status_code`: `200`, `404`, `500`
  - `http.route`: Target route template
  - `http.target`: Raw URI path

## 2. Database Spans
- **Span Name:** Operation + Table (e.g. `SELECT users`, `UPDATE orders`).
- **Required Attributes:**
  - `db.system`: `postgresql`, `mysql`, `redis`, `mongodb`
  - `db.name`: Database name
  - `db.statement`: Parameterized query (strip literals/PII)

## 3. RPC / gRPC Spans
- **Span Name:** Package + Service / Method (e.g. `billing.v1.PaymentService/ProcessPayment`).
- **Required Attributes:**
  - `rpc.system`: `grpc`
  - `rpc.service`: `billing.v1.PaymentService`
  - `rpc.method`: `ProcessPayment`
  - `rpc.grpc.status_code`: `0` (OK), `14` (UNAVAILABLE)

