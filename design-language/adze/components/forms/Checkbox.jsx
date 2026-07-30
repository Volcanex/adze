/* Checkbox — a boolean that is part of a set, or an opt-in.
 *
 * Checkbox vs Switch is a real distinction, not a style choice:
 *
 *   Checkbox — the change takes effect when the form is SAVED.
 *              "Show this work on the homepage" inside an edit form.
 *   Switch   — the change takes effect IMMEDIATELY.
 *              "Site is live" in a settings panel.
 *
 * Using a switch for a deferred change is the commonest form bug in admin
 * UIs: the user flips it, sees it move, assumes it's saved, and navigates
 * away. Pick by when the change lands.
 */

export function Checkbox({ label, description = null, id, ...rest }) {
    return (
        <label className="adze-check">
            <input type="checkbox" className="adze-check__input" id={id} {...rest} />
            <span className="adze-check__box" aria-hidden="true">
                <i className="ph ph-check" />
            </span>
            <span className="adze-check__text">
                <span className="adze-check__label">{label}</span>
                {description && <span className="adze-check__desc">{description}</span>}
            </span>
        </label>
    );
}

export const css = `
.adze-check {
    display: flex; align-items: flex-start; gap: var(--adze-space-3);
    cursor: pointer;
    padding: var(--adze-space-1) 0;
}

/* The real input stays in the accessibility tree and keeps keyboard
   behaviour; it's the visual box that's swapped. Never use display:none —
   that removes it from tab order entirely. */
.adze-check__input {
    position: absolute; opacity: 0;
    width: 18px; height: 18px; margin: 0;
    cursor: pointer;
}

.adze-check__box {
    flex: 0 0 auto;
    display: grid; place-items: center;
    width: 18px; height: 18px; margin-top: 1px;
    background: var(--adze-surface);
    border: 1.5px solid var(--adze-border-strong);
    border-radius: var(--adze-radius-sm);
    color: transparent;
    font-size: 12px;
    transition: background-color var(--adze-dur-fast) var(--adze-ease-out),
                border-color     var(--adze-dur-fast) var(--adze-ease-out),
                color            var(--adze-dur-fast) var(--adze-ease-out),
                transform        var(--adze-dur-fast) var(--adze-ease-spring);
}
.adze-check:hover .adze-check__box { border-color: var(--adze-text-faint); }

.adze-check__input:checked + .adze-check__box {
    background: var(--adze-accent);
    border-color: var(--adze-accent);
    color: var(--adze-accent-text);
    /* Spring easing gives the tick a tiny overshoot — the one place a bit of
       bounce is warranted, because it confirms a discrete action. */
    transform: scale(1.06);
}
.adze-check__input:focus-visible + .adze-check__box { box-shadow: var(--adze-focus-ring); }
.adze-check__input:disabled ~ * { opacity: 0.5; cursor: not-allowed; }

.adze-check__text { display: flex; flex-direction: column; gap: 2px; min-width: 0; }
.adze-check__label { font-size: var(--adze-text-sm); }
.adze-check__desc { font-size: var(--adze-text-xs); color: var(--adze-text-muted); }
`;
