# Checkbox

## Checkbox vs Switch

This is a real distinction, not a style choice:

| | Takes effect | Example |
|---|---|---|
| **Checkbox** | When the form is **saved** | "Show this work on the homepage", inside an edit form |
| **Switch** | **Immediately** | "Site is live", in a settings panel |

Using a Switch for a deferred change is the commonest form bug in admin UIs:
the user flips it, watches it move, assumes it saved, and navigates away.
Pick by *when the change lands*, not by which looks nicer.

```jsx
<Checkbox
  label="Feature on homepage"
  description="Shows this work in the top row of your gallery."
  checked={featured}
  onChange={e => setFeatured(e.target.checked)}
/>
```

## Rules

- The label is clickable — it wraps the input. Don't add your own `htmlFor`.
- Label with the positive state. "Hide from search" inverts the user's
  reasoning; prefer "Show in search results".
- `description` is one clarifying sentence. Longer belongs in `Field`'s help.
- For a group of related checkboxes, wrap them in a `<fieldset>` with a
  `<legend>` — the group needs a name too.
- Never `display: none` the underlying input; it removes it from tab order.
  The component hides it with opacity and keeps it focusable.
