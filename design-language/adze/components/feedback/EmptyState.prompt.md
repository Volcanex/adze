# EmptyState

What a list looks like before there's anything in it — and what it looks like
when loading failed.

This is a first-impression surface. An artist opening their content admin for
the first time sees an empty state by definition. The old shell rendered a
grey italic "no items" and nothing else: a dead end exactly where the user
needs a next step.

## The three required parts

- **title** — what's not here, phrased plainly. "No works yet", not "Empty".
- **body** — one sentence on what this section is for.
- **action** — the button that fixes it.

If you can't name an action, question whether the section should exist.

## Usage

```jsx
<EmptyState
  icon="images"
  title="No works yet"
  body="Add your first piece and it'll appear on your gallery page."
  action={<Button onClick={onAdd}>Add a work</Button>}
/>

<EmptyState
  variant="error"
  icon="warning"
  title="Couldn't load your works"
  body="The connection dropped. Your work is safe."
  action={<Button variant="secondary" onClick={retry}>Try again</Button>}
/>
```

## Rules

- Write the body in second person and keep it to one sentence.
- On `variant="error"`, say what happened AND reassure about data where
  that's true. "Your work is safe" is worth more than an error code.
- Never surface a raw exception string to an artist. Log it; show this.
- The component sets `role="status"` (or `role="alert"` for errors) — don't
  add another live region around it.
