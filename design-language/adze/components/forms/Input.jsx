/* Input — single-line text, and the textarea variant.
 *
 * Always inside a <Field>. The Field supplies id, aria-describedby and
 * aria-invalid via its render prop; spread them.
 */

export function Input({
    multiline = false,
    size = 'md',
    prefix = null,     // static text inside the control, e.g. "https://"
    icon = null,
    ...rest            // includes the props handed down by Field
}) {
    if (multiline) {
        return <textarea className={`adze-input adze-input--textarea adze-input--${size}`} {...rest} />;
    }
    if (prefix || icon) {
        return (
            <div className={`adze-input-group adze-input-group--${size}`}>
                {icon && <i className={`ph ph-${icon}`} aria-hidden="true" />}
                {prefix && <span className="adze-input-group__prefix">{prefix}</span>}
                <input className="adze-input adze-input--bare" {...rest} />
            </div>
        );
    }
    return <input className={`adze-input adze-input--${size}`} {...rest} />;
}

export const css = `
.adze-input {
    width: 100%;
    height: var(--adze-control-md);
    padding: 0 var(--adze-space-3);
    background: var(--adze-surface);
    color: var(--adze-text);
    border: 1px solid var(--adze-border-strong);
    border-radius: var(--adze-radius-md);
    font-family: var(--adze-font-ui);
    font-size: var(--adze-text-sm);
    transition: border-color var(--adze-dur-instant) var(--adze-ease-out),
                box-shadow   var(--adze-dur-fast)    var(--adze-ease-out);
}
.adze-input--sm { height: var(--adze-control-sm); font-size: var(--adze-text-xs); }
.adze-input--lg { height: var(--adze-control-lg); font-size: var(--adze-text-md); }

.adze-input--textarea {
    height: auto; min-height: 96px;
    padding: var(--adze-space-3);
    line-height: var(--adze-leading-normal);
    resize: vertical;
}

.adze-input::placeholder { color: var(--adze-text-faint); }
.adze-input:hover:not(:disabled) { border-color: var(--adze-text-faint); }
.adze-input:focus {
    outline: none;
    border-color: var(--adze-accent);
    box-shadow: var(--adze-focus-ring);
}
.adze-input:disabled { opacity: 0.55; cursor: not-allowed; background: var(--adze-bg-sunken); }

/* The error border is reinforced by the icon + text in Field — colour alone
   never carries the message. */
.adze-field--error .adze-input { border-color: var(--adze-danger); }
.adze-field--error .adze-input:focus {
    box-shadow: 0 0 0 3px color-mix(in srgb, var(--adze-danger) 26%, transparent);
}

/* Prefixed / icon inputs: the wrapper carries the chrome, the input goes bare. */
.adze-input-group {
    display: flex; align-items: center; gap: var(--adze-space-2);
    height: var(--adze-control-md);
    padding: 0 var(--adze-space-3);
    background: var(--adze-surface);
    border: 1px solid var(--adze-border-strong);
    border-radius: var(--adze-radius-md);
    transition: border-color var(--adze-dur-instant) var(--adze-ease-out),
                box-shadow   var(--adze-dur-fast)    var(--adze-ease-out);
}
.adze-input-group:focus-within { border-color: var(--adze-accent); box-shadow: var(--adze-focus-ring); }
.adze-input-group i { color: var(--adze-text-faint); font-size: 1.15em; }
.adze-input-group__prefix {
    font-family: var(--adze-font-mono);
    font-size: var(--adze-text-xs);
    color: var(--adze-text-faint);
    white-space: nowrap;
}
.adze-input--bare {
    border: 0; background: transparent; padding: 0; height: 100%;
    flex: 1; min-width: 0;
}
.adze-input--bare:focus { box-shadow: none; }
`;
