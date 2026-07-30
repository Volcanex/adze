/* Button
 *
 * Four variants, three sizes. The variant encodes IMPORTANCE, not colour —
 * pick by how much you want the user to press it, and the palette follows.
 *
 *   primary   — the one thing this screen is for. Max one per view.
 *   secondary — real alternatives. As many as needed.
 *   ghost     — tertiary, in-place actions (row menus, toolbar buttons).
 *   danger    — destructive and irreversible. Never the default focus.
 *
 * `loading` is built in rather than left to call sites, because the two
 * things that must happen together — disabling the button and showing a
 * spinner — were being done inconsistently in the old admin, so double-submits
 * were possible on Publish.
 */

import { Spinner } from '../feedback/Spinner.jsx';

export function Button({
    children,
    variant = 'secondary',
    size = 'md',            // 'sm' | 'md' | 'lg'
    icon = null,            // Phosphor name, leading
    iconTrailing = null,
    loading = false,
    disabled = false,
    fullWidth = false,
    type = 'button',
    onClick,
    ...rest
}) {
    const isDisabled = disabled || loading;
    return (
        <button
            type={type}
            className={[
                'adze-btn',
                `adze-btn--${variant}`,
                `adze-btn--${size}`,
                fullWidth && 'adze-btn--full',
                loading && 'is-loading',
            ].filter(Boolean).join(' ')}
            disabled={isDisabled}
            aria-busy={loading || undefined}
            onClick={onClick}
            {...rest}
        >
            {loading && <Spinner size="sm" tone="current" delay={0} />}
            {!loading && icon && <i className={`ph ph-${icon}`} aria-hidden="true" />}
            {/* The label stays mounted while loading so the button keeps its
                width — a button that shrinks to a spinner shifts the layout
                around it and looks broken. */}
            <span className="adze-btn__label">{children}</span>
            {iconTrailing && <i className={`ph ph-${iconTrailing}`} aria-hidden="true" />}
        </button>
    );
}

export const css = `
.adze-btn {
    display: inline-flex; align-items: center; justify-content: center;
    gap: var(--adze-space-2);
    height: var(--adze-control-md);
    padding: 0 var(--adze-space-4);
    border: 1px solid transparent;
    border-radius: var(--adze-radius-md);
    font-family: var(--adze-font-ui);
    font-size: var(--adze-text-sm);
    font-weight: var(--adze-weight-medium);
    line-height: 1;
    white-space: nowrap;
    cursor: pointer;
    /* Explicit property list, not \`all\` — transitioning \`all\` also animates
       width/height when content changes, which is what made the old buttons
       feel rubbery. */
    transition: background-color var(--adze-dur-instant) var(--adze-ease-out),
                border-color     var(--adze-dur-instant) var(--adze-ease-out),
                color            var(--adze-dur-instant) var(--adze-ease-out),
                box-shadow       var(--adze-dur-fast)    var(--adze-ease-out),
                transform        var(--adze-dur-fast)    var(--adze-ease-out);
}
.adze-btn i { font-size: 1.15em; }
.adze-btn--sm   { height: var(--adze-control-sm); padding: 0 var(--adze-space-3); font-size: var(--adze-text-xs); }
.adze-btn--lg   { height: var(--adze-control-lg); padding: 0 var(--adze-space-6); font-size: var(--adze-text-md); }
.adze-btn--full { width: 100%; }

/* The press. 0.98 is deliberately subtle — enough to feel mechanical,
   not enough to read as a bounce. This is most of the "slick". */
.adze-btn:active:not(:disabled) { transform: scale(0.98); }
.adze-btn:focus-visible { outline: none; box-shadow: var(--adze-focus-ring); }

.adze-btn--primary { background: var(--adze-accent); color: var(--adze-accent-text); }
.adze-btn--primary:hover:not(:disabled) { background: var(--adze-accent-hover); }

.adze-btn--secondary {
    background: var(--adze-surface); color: var(--adze-text);
    border-color: var(--adze-border-strong);
}
.adze-btn--secondary:hover:not(:disabled) {
    background: var(--adze-surface-hover); border-color: var(--adze-text-faint);
}

.adze-btn--ghost { background: transparent; color: var(--adze-text-muted); }
.adze-btn--ghost:hover:not(:disabled) { background: var(--adze-bg-sunken); color: var(--adze-text); }

.adze-btn--danger { background: var(--adze-danger); color: #fff; }
.adze-btn--danger:hover:not(:disabled) { background: color-mix(in srgb, var(--adze-danger) 86%, #000); }

.adze-btn:disabled { opacity: 0.5; cursor: not-allowed; }
/* While loading the cursor stays 'wait' rather than 'not-allowed' — the
   action isn't forbidden, it's in flight. */
.adze-btn.is-loading { cursor: wait; opacity: 0.8; }
`;
