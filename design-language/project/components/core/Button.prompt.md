A square-cornered, monospace-labelled button for Last Place — blue fill for the single primary action, inked outline otherwise.

```jsx
<Button variant="primary" onClick={save}>Start a project</Button>
<Button variant="secondary" size="sm">View work</Button>
<Button variant="link" href="/about">read more</Button>
```

Variants: `primary` (blue), `secondary` (ink outline), `ghost` (bare), `green` (rare forest accent), `link` (inline serif hyperlink). Sizes: `sm` `md` `lg`. Pass `href` to render an `<a>`; `block` to fill width. Use one `primary` per view — restraint is the brand.
