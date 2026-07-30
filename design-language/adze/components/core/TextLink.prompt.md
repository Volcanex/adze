# TextLink

## The underline rule

**Inline links are always underlined.** An accent-coloured word inside a
paragraph with no underline is invisible to anyone with a colour vision
deficiency. Colour alone is never a sufficient signal for interactivity.

**Standalone links** — nav items, row actions, anything whose position already
marks it as interactive — may underline on hover only.

Default is `inline`. Choosing `standalone` is you asserting that position
carries the meaning. Be honest about that.

```jsx
<p>Read the <TextLink href="/docs">setup guide</TextLink> first.</p>

<TextLink variant="standalone" href="/sites" icon="arrow-left">Back to sites</TextLink>

<TextLink variant="quiet" href={site.url} external>{site.domain}</TextLink>
```

## Rules

- `external` sets `target="_blank"`, `rel="noopener noreferrer"`, a trailing
  arrow, and screen-reader text saying it opens in a new tab. Always use it
  rather than setting target by hand — the `rel` is a security requirement.
- Link text must make sense read on its own. "Click here" and "read more" are
  useless in a screen-reader's link list.
- Use `quiet` for links that shouldn't compete with body text — breadcrumbs,
  row-level actions, domain names in a list.
- If it performs an action rather than navigating, it's a `Button` with
  `variant="ghost"`, not a link.
