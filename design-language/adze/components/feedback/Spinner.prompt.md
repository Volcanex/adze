# Spinner

Indeterminate activity for a small, bounded area.

Reach for it only after ruling out `Skeleton` (you know the shape) and
`ProgressBar` (you know the progress). A full-page spinner is nearly always
the wrong answer — it communicates nothing but "wait".

## Usage

```jsx
// Inside a button during save — tone="current" inherits the button's colour
<Button disabled>{saving && <Spinner size="sm" tone="current" />} Save</Button>

// Beside an inline action
<Spinner size="sm" tone="muted" label="Checking domain" />
```

## Rules

- Keep `delay` at its 300ms default. A spinner that flashes for 80ms and
  vanishes reads as a rendering glitch; below ~400ms, no feedback feels
  faster than feedback.
- `tone="current"` inside buttons and links so it picks up the parent colour
  in every state including hover and dark mode.
- Always pass a meaningful `label` — it's the screen-reader text, and
  "Loading" is rarely the most useful thing you could say.
- Don't put a spinner and a skeleton in the same region. Pick one.
