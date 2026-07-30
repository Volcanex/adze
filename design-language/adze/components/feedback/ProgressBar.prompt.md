# ProgressBar

The Adze loading bar. Use it whenever an operation takes longer than ~400ms.

## Choosing the mode

**Determinate** (`value={0..100}`) whenever you can compute progress at all.
Uploads know their byte count. Publish knows its step count. Batch operations
know their index. Prefer it — a real number is the difference between
"working" and "trust me".

**Indeterminate** (`value={null}`) only when progress is genuinely unknowable,
such as a single request in flight.

Never animate a fake determinate bar on a timer. Users clock the mismatch
immediately and it costs more trust than an honest indeterminate bar.

## Usage

```jsx
// Upload with real progress
<ProgressBar label="Uploading" value={pct} detail={`${done} of ${total}`} />

// Request in flight, no measurable progress
<ProgressBar label="Publishing" value={null} />

// Compact, inside a row
<ProgressBar size="sm" value={pct} showValue={false} />
```

## Rules

- Always pass `label` unless the surrounding context already names the
  operation — the bar alone doesn't say what's happening.
- `tone="danger"` is for a failing/degraded operation, not for a delete.
- Use `.adze-numeric` (already applied to the readout) for any figure that
  counts up, so tabular figures stop the number jittering.
- Don't stack more than one bar on screen. Multiple concurrent operations
  want a single bar with `detail="3 of 12"`.
- When the operation completes, don't snap the bar away — let it reach 100%,
  hold ~200ms, then unmount. Removing a bar at 80% reads as a failure.
