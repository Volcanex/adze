# Button

## Choosing a variant

Pick by importance; the colour follows.

| Variant | Use for | Per view |
|---|---|---|
| `primary` | The one thing this screen exists to do | **Max one** |
| `secondary` | Genuine alternatives | Any number |
| `ghost` | Tertiary, in-place actions — row menus, toolbars | Any number |
| `danger` | Destructive and irreversible | Never autofocused |

Two primary buttons side by side means neither is primary. Decide which one
the user is actually here to press.

## Loading

Always use the `loading` prop rather than hand-rolling a disabled state plus a
spinner. It does both, sets `aria-busy`, and keeps the label mounted so the
button doesn't change width mid-flight.

```jsx
<Button variant="primary" loading={publishing} onClick={publish}>Publish</Button>
```

This matters concretely: the old admin allowed double-submits on Publish
because disabling and spinning were separate call-site decisions.

## Rules

- Label with a verb phrase describing the outcome: "Publish", "Add a work",
  "Save changes". Never "OK", "Submit", or "Yes".
- `danger` needs a confirmation step for anything that can't be undone, and
  the confirm dialog's default focus goes on Cancel.
- Icons are Phosphor names without the `ph-` prefix (`icon="plus"`).
- Icon-only buttons must still carry an `aria-label`.
- Use `fullWidth` on mobile forms and in narrow panels, not in toolbars.
