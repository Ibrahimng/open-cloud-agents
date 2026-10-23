---
name: opentelemetry-instrumentation
description: Instrument distributed microservices with OpenTelemetry (OTel) traces, metrics, and logs, establishing W3C trace context propagation across HTTP, gRPC, and message brokers.
---

# OpenTelemetry Distributed Tracing & Instrumentation

## Core Standards
1. **W3C Trace Context Propagation**:
   - Ensure the `traceparent` and `tracestate` headers are passed along all outbound HTTP/gRPC calls and message queues.
2. **Semantic Conventions**:
   - Standardize span names: use `{http.method} {http.route}` (e.g. `POST /v1/orders`) rather than dynamic URLs (`POST /v1/orders/123`).
   - Tag spans with standard attributes: `service.name`, `service.version`, `deployment.environment`.
3. **No Sensitive PII in Span Attributes**:
   - Never log authorization headers, credit cards, user passwords, or raw request bodies into spans.

## Trace Initialization Boilerplate (TypeScript / Node.js)
```typescript
import { NodeSDK } from '@opentelemetry/sdk-node';
import { getNodeAutoInstrumentations } from '@opentelemetry/auto-instrumentations-node';
import { OTLPTraceExporter } from '@opentelemetry/exporter-trace-otlp-http';
import { Resource } from '@opentelemetry/resources';
import { SemanticResourceAttributes } from '@opentelemetry/semantic-conventions';

const sdk = new NodeSDK({
  resource: new Resource({
    [SemanticResourceAttributes.SERVICE_NAME]: process.env.OTEL_SERVICE_NAME || 'cloud-service',
    [SemanticResourceAttributes.DEPLOYMENT_ENVIRONMENT]: process.env.NODE_ENV || 'production',
  }),
  traceExporter: new OTLPTraceExporter({
    url: process.env.OTEL_EXPORTER_OTLP_ENDPOINT || 'http://otel-collector:4318/v1/traces',
  }),
  instrumentations: [getNodeAutoInstrumentations()],
});

sdk.start();
```
