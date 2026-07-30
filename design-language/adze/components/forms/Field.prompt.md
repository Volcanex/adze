# Field

Every form control in Adze is wrapped in a Field. It owns four things that
were being reimplemented differently at each call site in the old shell:

1. the mono uppercase label
2. `id` ↔ `htmlFor` wiring
3. `aria-describedby` pointing at both help and error text
4. the error slot

Number 3 is why this component exists. In the old admin, validation errors
rendered as a red `<div>` beside the input with no programmatic association —
a screen-reader user tabbing through a failed form heard nothing about why it
failed.

## Usage

Field uses a render prop. Spread what it gives you onto the control.

```jsx
<Field label="Title" required error={errors.title}>
  {p => <Input {...p} value={title} onChange={e => setTitle(e.target.value)} />}
</Field>

<Field label="Website" help="Include https://">
  {p => <Input {...p} prefix="https://" placeholder="yoursite.com" />}
</Field>

<Field label="Bio" hint={`${bio.length}/280`}>
  {p => <Input {...p} multiline value={bio} />}
</Field>
```

## Rules

- Never write a bare `<label>` next to a control. Always use Field.
- `error` is a sentence for a person, not a validator code: "Add a title so
  this work can be found", not "title: required".
- `help` disappears when `error` is set — don't rely on the user seeing both.
- `hint` is for counts and optionality only. Anything longer goes in `help`.
- Mark optional fields rather than required ones when most are required; the
  asterisk should be the exception on the screen, not the rule.
