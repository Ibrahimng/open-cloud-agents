---
name: go-concurrency-patterns
description: Write safe, high-throughput Go concurrent code using goroutines, channels, context cancellation, sync.WaitGroup, and errgroup.Group without goroutine leaks.
---

# Go Concurrency & Worker Pool Patterns

## 1. Structured Concurrency with `golang.org/x/sync/errgroup`
Always bound goroutine lifecycles and propagate the first encountered error:

```go
package main

import (
	"context"
	"fmt"
	"golang.org/x/sync/errgroup"
	"time"
)

func FetchAllUserData(ctx context.Context, userIDs []string) error {
	// Cancel sibling operations immediately if any one fails
	g, ctx := errgroup.WithContext(ctx)
	g.SetLimit(10) // Bounded concurrency limit

	for _, id := range userIDs {
		userID := id // Pin loop variable (prior to Go 1.22)
		g.Go(func() error {
			return fetchProfile(ctx, userID)
		})
	}

	return g.Wait()
}

func fetchProfile(ctx context.Context, id string) error {
	select {
	case <-ctx.Done():
		return ctx.Err()
	case <-time.After(100 * time.Millisecond):
		fmt.Printf("Fetched user %s\n", id)
		return nil
	}
}
```

## 2. Goroutine Leak Prevention
- Never launch a goroutine without knowing how and when it terminates.
- Always check `ctx.Done()` when reading/writing unbuffered channels or waiting on IO.
- Always run the race detector in tests: `go test -race ./...`.

