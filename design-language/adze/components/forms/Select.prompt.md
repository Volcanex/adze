# Select

A native `<select>` with Adze chrome.

Native is deliberate. It gets correct keyboard behaviour, correct screen-reader
semantics, and the platform picker on mobile — all of which a hand-rolled
dropdown must reimplement and usually gets wrong. Only build a custom control
if you need multi-select with search, and then build it as a proper combobox.

```jsx
<Field label="Category">
  {p => <Select {...p} options={['Painting', 'Sculpture', 'Print']} placeholder="Choose one" />}
</Field>

<Field label="Page">
  {p => <Select {...p} options={pages.map(pg => ({ value: pg.slug, label: pg.title }))} />}
</Field>
```

## Rules

- Options accept plain strings or `{value, label}` objects. Use objects
  whenever the stored value differs from what you show.
- `placeholder` renders as a leading empty-value option — pair it with
  `required` so the empty value can't be submitted.
- Over roughly 12 options, a select becomes hard to scan. Consider a search
  input with filtering instead.
- Never put actions in a select. A dropdown that performs something on change
  is a menu, and it needs a button.
