/* Switch — a boolean that takes effect IMMEDIATELY.
 *
 * See Checkbox for the distinction. In short: if the user must press Save
 * afterwards, it is a Checkbox, not a Switch.
 *
 * Because a switch acts at once, it needs to report what happened. Pass
 * `pending` while the write is in flight — the track shows activity and the
 * control locks, so the user can't toggle three times against a slow network
 * and end up in an unknown state.
 */

export function Switch({ label, description = null, pending = false, id, ...rest }) {
    return (
        <label className={`adze-switch ${pending ? 'is-pending' : ''}`}>
            <span className="adze-switch__text">
                <span className="adze-switch__label">{label}</span>
                {description && <span className="adze-switch__desc">{description}</span>}
            </span>
            <input
                type="checkbox"
                role="switch"
                className="adze-switch__input"
                id={id}
                disabled={pending || rest.disabled}
                aria-busy={pending || undefined}
                {...rest}
            />
            <span className="adze-switch__track" aria-hidden="true">
                <span className="adze-switch__thumb" />
            </span>
        </label>
    );
}

export const css = `
.adze-switch {
    display: flex; align-items: center; justify-content: space-between;
    gap: var(--adze-space-4);
    cursor: pointer;
    padding: var(--adze-space-2) 0;
}
.adze-switch__text { display: flex; flex-direction: column; gap: 2px; min-width: 0; }
.adze-switch__label { font-size: var(--adze-text-sm); }
.adze-switch__desc { font-size: var(--adze-text-xs); color: var(--adze-text-muted); }

.adze-switch__input { position: absolute; opacity: 0; width: 44px; height: 26px; margin: 0; cursor: pointer; }

.adze-switch__track {
    position: relative; flex: 0 0 auto;
    width: 44px; height: 26px;
    background: var(--adze-border-strong);
    border-radius: var(--adze-radius-pill);
    transition: background-color var(--adze-dur) var(--adze-ease-out);
}
.adze-switch__thumb {
    position: absolute; top: 3px; left: 3px;
    width: 20px; height: 20px;
    background: #fff;
    border-radius: var(--adze-radius-pill);
    box-shadow: var(--adze-shadow-sm);
    transition: transform var(--adze-dur) var(--adze-ease-spring);
}

.adze-switch__input:checked ~ .adze-switch__track { background: var(--adze-accent); }
.adze-switch__input:checked ~ .adze-switch__track .adze-switch__thumb { transform: translateX(18px); }
.adze-switch__input:focus-visible ~ .adze-switch__track { box-shadow: var(--adze-focus-ring); }
.adze-switch__input:disabled ~ .adze-switch__track { opacity: 0.5; }

/* Pending: the track pulses to show the write is in flight, and the label
   dims so it's clear the displayed state isn't confirmed yet. */
.adze-switch.is-pending { cursor: wait; }
.adze-switch.is-pending .adze-switch__track { animation: adze-pulse 1s var(--adze-ease-in-out) infinite; }
.adze-switch.is-pending .adze-switch__text { opacity: 0.6; }

@keyframes adze-pulse { 50% { opacity: 0.55; } }
`;
