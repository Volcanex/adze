# Tag

A small mono chip for status, category or count.

This is where the mono voice earns its keep. Tags are scanned rather than
read, so they take JetBrains Mono at 11px with open tracking — the strongest
carry-over from the old Adze identity, and the main reason the new system
still reads as Adze rather than generic Inter.

## Tones

`neutral` `accent` `success` `warn` `danger`

Status tones are deliberately **not** artist-overridable. "Live" must look
the same on every artist's admin regardless of their accent colour — an
artist whose accent is red should not get a red "saved".

```jsx
<Tag tone="success" dot>Live</Tag>
<Tag tone="warn" dot>Unpublished changes</Tag>
<Tag tone="neutral">Draft</Tag>
```

## Rules

- One or two words. A tag is a label, not a sentence.
- Use `dot` for lifecycle status (live/draft/error), omit it for categories.
- Don't make tags clickable. If it filters, it's a button or a filter chip —
  a different component with a different affordance.
- Text is uppercased by CSS; write it in sentence case in the source so it
  stays readable when the transform is inspected or removed.
