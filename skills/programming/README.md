# Programming Language Skills Catalog

This directory houses language-specific idiomatic patterns, architectural standards, and testing workflows for software development across **Dart**, **Python**, **TypeScript/JavaScript**, **Go**, and **Java**.

Autonomous agents in **Open Cloud Agents** activate these skills when generating code, refactoring logic, implementing tests, or diagnosing language-specific runtime crashes.

---

## Directory Overview

```text
skills/programming/
├── dart/                       # Dart 3 & Flutter (FFI native assets, CLI apps, test runner)
├── python/                     # Python 3.11+ (FastAPI REST patterns, pytest async suites)
├── javascript/                 # TypeScript & Node.js (Strict type systems, discriminated unions)
├── go/                         # Golang (Structured concurrency, errgroup worker pools)
└── java/                       # Java 21+ & Spring Boot (Virtual threads, clean architecture)
```

---

## Core Standards Across All Languages

1. **Deterministic Static Typing**: Enforce explicit types at public API boundaries; never rely on implicit `any` or untyped dictionaries when schemas can be modeled.
2. **Automated Test Parity**: Every new feature or bug fix must include automated test coverage (unit or integration).
3. **Structured Concurrency**: Prevent goroutine/thread/promise leaks by binding concurrent operations to cancellation contexts (`context.Context`, `asyncio.TaskGroup`, Project Loom scopes).
4. **Zero Hardcoded Secrets**: Secrets and environment configurations must be injected via environment variables or secret managers, never embedded in source code.
