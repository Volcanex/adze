# Input

Single-line text plus a `multiline` textarea variant. Always inside a `Field` —
spread the render-prop props onto it so id and ARIA wiring come along.

```jsx
<Field label="Title">{p => <Input {...p} />}</Field>
<Field label="Notes">{p => <Input {...p} multiline />}</Field>
<Field label="Domain">{p => <Input {...p} prefix="https://" />}</Field>
<Field label="Search">{p => <Input {...p} icon="magnifying-glass" />}</Field>
```

## Rules

- Set `type` honestly (`email`, `url`, `tel`, `number`). It selects the right
  mobile keyboard, which matters — artists use the admin on phones.
- Placeholders are examples, never labels. A placeholder disappears on focus
  and is invisible to some assistive tech; the Field label is the label.
- `multiline` resizes vertically only. Never `resize: both` — horizontal
  resize breaks the layout around it.
- Don't set a fixed width. Inputs fill their container; constrain the
  container with `--adze-width-form`.
- For a character-limited field, pass the count to `Field`'s `hint`.
