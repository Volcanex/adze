An editorial text input set as an underline — mono label, serif input, a hairline rule that turns hyperlink-blue on focus.

```jsx
<Field label="Your name" placeholder="Jane Appleseed" value={name} onChange={e => setName(e.target.value)} />
<Field label="Tell us about the project" multiline hint="A sentence or two is plenty." />
```

Props: `label`, `hint`, `error` (turns the rule forest green), `multiline`, `type`, plus standard input props.
