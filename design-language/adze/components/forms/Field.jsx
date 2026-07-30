/* Field — the label / control / help / error wrapper.
 *
 * Every form control in Adze is wrapped in a Field. It owns the four things
 * that were being reimplemented (differently) at each call site in the old
 * shell:
 *
 *   1. the mono uppercase label
 *   2. the id↔htmlFor wiring
 *   3. aria-describedby pointing at help AND error text
 *   4. the error slot itself
 *
 * That third one is the reason this component exists. In the old admin,
 * validation errors were rendered as a red <div> next to the input with no
 * programmatic association, so a screen-reader user tabbing through a failed
 * form heard nothing at all about why it failed.
 */

import { useId } from 'react';

export function Field({
    children,          // render prop: (inputProps) => node
    label,
    help = null,
    error = null,      // string turns the field into its error state
    required = false,
    hint = null,       // right-aligned mono note, e.g. "optional" or "0/280"
}) {
    const id = useId();
    const helpId = help ? `${id}-help` : null;
    const errorId = error ? `${id}-error` : null;
    const describedBy = [helpId, errorId].filter(Boolean).join(' ') || undefined;

    return (
        <div className={`adze-field ${error ? 'adze-field--error' : ''}`}>
            <div className="adze-field__head">
                <label className="adze-label" htmlFor={id}>
                    {label}
                    {required && <span className="adze-field__req" aria-hidden="true">*</span>}
                </label>
                {hint && <span className="adze-field__hint adze-numeric">{hint}</span>}
            </div>

            {children({
                id,
                'aria-describedby': describedBy,
                'aria-invalid': error ? true : undefined,
                required,
            })}

            {help && !error && (
                <p className="adze-field__help" id={helpId}>{help}</p>
            )}
            {error && (
                /* role="alert" so it's announced the moment it appears, not
                   only when focus happens to reach the field. */
                <p className="adze-field__error" id={errorId} role="alert">
                    <i className="ph ph-warning-circle" aria-hidden="true" />
                    {error}
                </p>
            )}
        </div>
    );
}

export const css = `
.adze-field { display: flex; flex-direction: column; gap: var(--adze-space-2); margin-bottom: var(--adze-space-4); }
.adze-field__head { display: flex; align-items: baseline; justify-content: space-between; gap: var(--adze-space-3); }
.adze-field__req { color: var(--adze-danger); margin-left: 2px; }
.adze-field__hint { font-size: var(--adze-text-2xs); color: var(--adze-text-faint); }
.adze-field__help { margin: 0; font-size: var(--adze-text-xs); color: var(--adze-text-muted); }
.adze-field__error {
    display: flex; align-items: center; gap: var(--adze-space-1);
    margin: 0; font-size: var(--adze-text-xs); color: var(--adze-danger);
    animation: adze-rise-in var(--adze-dur-fast) var(--adze-ease-out) both;
}
`;
