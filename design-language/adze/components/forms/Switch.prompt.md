# Switch

A boolean that takes effect **immediately**. If the user has to press Save
afterwards, it's a `Checkbox` — see that component for the full distinction.

## pending is not optional

Because a switch acts at once, it must report what happened. Pass `pending`
while the write is in flight: the track pulses, the label dims, and the
control locks so the user can't toggle three times against a slow network and
land in an unknown state.

```jsx
<Switch
  label="Site is live"
  description="Visitors can reach your site at lydialott.co.uk"
  checked={live}
  pending={saving}
  onChange={async e => {
    setSaving(true);
    await setLive(e.target.checked);
    setSaving(false);
  }}
/>
```

## Rules

- Always handle failure. If the write fails, revert the visual state and show
  the reason — a switch that stays flipped after a failed save is a lie about
  the system's state.
- Never use a Switch inside a form with a Save button. Mixing immediate and
  deferred controls in one form is how users lose work.
- Label the thing, not the action: "Site is live", not "Make site live".
- Carries `role="switch"` so assistive tech announces on/off rather than
  checked/unchecked. Don't override it.
