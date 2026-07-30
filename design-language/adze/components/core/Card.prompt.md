# Card

A bounded surface holding one coherent thing. The main structural unit of the
Adze admin.

## The one-subject rule

One card, one subject. If you're putting a divider through the middle of a
card, you have two cards. Nested cards are always wrong — use spacing or a
plain section instead.

## interactive

Set `interactive` only when the ENTIRE card navigates somewhere: a site in the
"your sites" list, an item in a gallery grid.

Never set it on a card containing its own buttons or links. Nested interactive
targets are ambiguous for both pointer and keyboard users, and the inner
control's click will fight the outer one.

```jsx
// Right — whole card is one target
<Card interactive as="a" href={`/sites/${site.slug}`} title={site.name} subtitle={site.domain} />

// Wrong — card has its own controls
<Card interactive title="Gallery" action={<Button>Edit</Button>} />
```

## Rules

- `padding="md"` is the default and is right almost always. Use `none` when
  the card contains a full-bleed list or image.
- The `action` slot takes one control, normally a ghost Button. Two or more
  means the card is doing too much.
- Don't add your own box-shadow. Elevation is `--adze-shadow-*` and cards
  already carry `sm`.
