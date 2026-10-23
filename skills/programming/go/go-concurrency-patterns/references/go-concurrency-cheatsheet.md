# Go Concurrency & Primitives Cheat Sheet

## 1. Channel Rules of Thumb
- **The Sender Closes the Channel:** Never close a channel from the receiver side.
- **Never Close a Nil Channel:** Panics at runtime.
- **Reading from a Closed Channel:** Returns the zero value and `ok = false`.
- **Writing to a Closed Channel:** Panics at runtime.

## 2. Worker Pool Pattern with Context
```go
func Worker(ctx context.Context, jobs <-chan int, results chan<- int) {
    for {
        select {
        case <-ctx.Done():
            return
        case j, ok := <-jobs:
            if !ok {
                return
            }
            results <- j * 2
        }
    }
}
```

## 3. Atomic Operations
For simple counters, prefer `sync/atomic` over mutex locks:
```go
import "sync/atomic"

var requestCount atomic.Uint64
requestCount.Add(1)
```

