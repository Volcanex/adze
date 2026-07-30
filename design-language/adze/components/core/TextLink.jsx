/* TextLink — an inline or standalone link.
 *
 * Underline behaviour is the whole design decision here:
 *
 *   inline links (inside a paragraph) are underlined ALWAYS. An accent-
 *   coloured word with no underline is invisible to anyone with a colour
 *   vision deficiency, and colour alone is never a sufficient signal.
 *
 *   standalone links (nav items, row actions, buttons-that-are-links) may
 *   underline on hover only, because their position already marks them as
 *   interactive.
 *
 * Default is `inline`. Choosing `standalone` is an assertion that position
 * carries the meaning.
 */

export function TextLink({
    children,
    href,
    variant = 'inline',   // 'inline' | 'standalone' | 'quiet'
    external = false,
    icon = null,
    ...rest
}) {
    const externalProps = external
        ? { target: '_blank', rel: 'noopener noreferrer' }
        : {};

    return (
        <a
            href={href}
            className={`adze-link adze-link--${variant}`}
            {...externalProps}
            {...rest}
        >
            {icon && <i className={`ph ph-${icon}`} aria-hidden="true" />}
            {children}
            {external && (
                <>
                    <i className="ph ph-arrow-up-right adze-link__ext" aria-hidden="true" />
                    <span className="adze-sr-only">(opens in a new tab)</span>
                </>
            )}
        </a>
    );
}

export const css = `
.adze-link {
    color: var(--adze-accent);
    text-decoration: none;
    text-underline-offset: 2px;
    text-decoration-thickness: 1px;
    border-radius: var(--adze-radius-sm);
    transition: var(--adze-transition-color);
}
.adze-link:hover { color: var(--adze-accent-hover); }
.adze-link:focus-visible { outline: none; box-shadow: var(--adze-focus-ring); }

/* Inline: always underlined. Non-negotiable. */
.adze-link--inline { text-decoration: underline; }

/* Standalone: position signals interactivity, underline on hover. */
.adze-link--standalone {
    display: inline-flex; align-items: center; gap: var(--adze-space-1);
    font-weight: var(--adze-weight-medium);
}
.adze-link--standalone:hover { text-decoration: underline; }

/* Quiet: reads as body text until hovered. Row actions, breadcrumbs. */
.adze-link--quiet { color: var(--adze-text-muted); }
.adze-link--quiet:hover { color: var(--adze-text); text-decoration: underline; }

.adze-link__ext { font-size: 0.85em; opacity: 0.7; }

.adze-sr-only {
    position: absolute; width: 1px; height: 1px;
    padding: 0; margin: -1px; overflow: hidden;
    clip: rect(0, 0, 0, 0); white-space: nowrap; border: 0;
}
`;
