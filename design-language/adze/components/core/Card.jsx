/* Card — a bounded surface holding one coherent thing.
 *
 * Cards are the main structural unit of the Adze admin. One card = one
 * subject. If you find yourself putting a divider through the middle of a
 * card, it's two cards.
 *
 * `interactive` makes the whole card a target. Use it only when the entire
 * card genuinely navigates somewhere — a site in the "your sites" list, an
 * item in a gallery. A card containing several separate controls must NOT be
 * interactive; nested targets are ambiguous for pointer and keyboard alike.
 */

export function Card({
    children,
    title = null,
    subtitle = null,
    action = null,        // top-right control (a ghost Button, usually)
    padding = 'md',       // 'none' | 'sm' | 'md' | 'lg'
    interactive = false,
    as: Tag = 'div',
    ...rest
}) {
    const hasHeader = title || subtitle || action;
    return (
        <Tag
            className={[
                'adze-card',
                `adze-card--pad-${padding}`,
                interactive && 'adze-card--interactive',
            ].filter(Boolean).join(' ')}
            {...rest}
        >
            {hasHeader && (
                <div className="adze-card__head">
                    <div className="adze-card__heading">
                        {title && <h3 className="adze-card__title">{title}</h3>}
                        {subtitle && <p className="adze-card__subtitle">{subtitle}</p>}
                    </div>
                    {action && <div className="adze-card__action">{action}</div>}
                </div>
            )}
            {children}
        </Tag>
    );
}

export const css = `
.adze-card {
    background: var(--adze-surface);
    border: 1px solid var(--adze-border);
    border-radius: var(--adze-radius-md);
    box-shadow: var(--adze-shadow-sm);
    transition: border-color var(--adze-dur-fast) var(--adze-ease-out),
                box-shadow   var(--adze-dur-fast) var(--adze-ease-out),
                transform    var(--adze-dur-fast) var(--adze-ease-out);
}

.adze-card--pad-none { padding: 0; }
.adze-card--pad-sm   { padding: var(--adze-space-3); }
.adze-card--pad-md   { padding: var(--adze-space-6); }
.adze-card--pad-lg   { padding: var(--adze-space-8); }

.adze-card__head {
    display: flex; align-items: flex-start; justify-content: space-between;
    gap: var(--adze-space-4);
    margin-bottom: var(--adze-space-4);
}
.adze-card__heading { min-width: 0; }
.adze-card__title {
    font-size: var(--adze-text-md);
    font-weight: var(--adze-weight-semibold);
    line-height: var(--adze-leading-snug);
}
.adze-card__subtitle {
    margin: var(--adze-space-1) 0 0;
    font-size: var(--adze-text-xs);
    color: var(--adze-text-muted);
}
.adze-card__action { flex: 0 0 auto; margin: -4px -4px 0 0; }

.adze-card--interactive { cursor: pointer; }
/* 1px, not 4px. The lift should register peripherally, not announce itself. */
.adze-card--interactive:hover {
    border-color: var(--adze-accent-line);
    box-shadow: var(--adze-shadow-md);
    transform: translateY(-1px);
}
.adze-card--interactive:active { transform: translateY(0); }
.adze-card--interactive:focus-visible { outline: none; box-shadow: var(--adze-focus-ring); }
`;
