/* EmptyState — what a list looks like before there's anything in it.
 *
 * This matters more than it sounds. An artist's first view of their content
 * admin is, by definition, empty. The old shell rendered a grey italic
 * "no items" and nothing else — a dead end at the exact moment the user needs
 * a next step.
 *
 * Every empty state needs three things:
 *   title   — what's not here, phrased plainly ("No works yet")
 *   body    — one sentence on what this section is for
 *   action  — the button that fixes it
 *
 * If you can't name an action, ask whether the section should exist.
 *
 * `variant="error"` reuses the same frame for failure. Deliberate: an error
 * is an empty state with a cause, and giving them one shape means users
 * recognise "nothing here + here's your move" instantly in either case.
 */

export function EmptyState({
    icon = null,          // Phosphor icon name, e.g. 'images'
    title,
    body = null,
    action = null,        // <Button> or similar
    variant = 'empty',    // 'empty' | 'error'
}) {
    return (
        <div className={`adze-empty adze-empty--${variant}`} role={variant === 'error' ? 'alert' : 'status'}>
            {icon && (
                <div className="adze-empty__icon" aria-hidden="true">
                    <i className={`ph ph-${icon}`} />
                </div>
            )}
            <h3 className="adze-empty__title">{title}</h3>
            {body && <p className="adze-empty__body">{body}</p>}
            {action && <div className="adze-empty__action">{action}</div>}
        </div>
    );
}

export const css = `
.adze-empty {
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
    padding: var(--adze-space-12) var(--adze-space-6);
    /* Rises in rather than appearing — this is usually the first thing an
       artist sees after a load, so it should feel arrived-at, not flashed. */
    animation: adze-rise-in var(--adze-dur-slow) var(--adze-ease-out) both;
}

.adze-empty__icon {
    display: grid; place-items: center;
    width: 48px; height: 48px;
    margin-bottom: var(--adze-space-4);
    border-radius: var(--adze-radius-pill);
    background: var(--adze-bg-sunken);
    color: var(--adze-text-faint);
    font-size: 22px;
}
.adze-empty--error .adze-empty__icon {
    background: var(--adze-danger-soft);
    color: var(--adze-danger);
}

.adze-empty__title {
    font-size: var(--adze-text-md);
    font-weight: var(--adze-weight-semibold);
    margin-bottom: var(--adze-space-2);
}

.adze-empty__body {
    font-size: var(--adze-text-sm);
    color: var(--adze-text-muted);
    max-width: 42ch;
    margin-bottom: 0;
}

.adze-empty__action { margin-top: var(--adze-space-6); }
`;
