/* Skeleton — placeholder shape shown while content loads.
 *
 * Use a skeleton when you know the SHAPE of what's arriving (a list of works,
 * a form, a card grid). Use a Spinner only when you don't. A skeleton that
 * matches the real layout makes the arrival feel instant because nothing
 * moves when the data lands — that perceived-speed trick is most of what
 * "slick" means.
 *
 * The cardinal sin is a skeleton whose dimensions differ from the real
 * content: the page jumps on load and it feels worse than a spinner would
 * have. Match the real thing or don't bother.
 */

export function Skeleton({
    variant = 'text',   // 'text' | 'title' | 'block' | 'circle' | 'thumb'
    width = null,       // CSS length; defaults per variant
    height = null,
    lines = 1,          // >1 only meaningful for variant="text"
}) {
    if (variant === 'text' && lines > 1) {
        return (
            <div className="adze-skeleton-stack">
                {Array.from({ length: lines }, (_, i) => (
                    <div
                        key={i}
                        className="adze-skeleton adze-skeleton--text"
                        /* Last line runs short, the way real ragged text does.
                           Uniform-width bars read as a barcode, not a paragraph. */
                        style={{ width: i === lines - 1 ? '62%' : (width || '100%') }}
                    />
                ))}
            </div>
        );
    }

    return (
        <div
            className={`adze-skeleton adze-skeleton--${variant}`}
            style={{ width: width || undefined, height: height || undefined }}
            aria-hidden="true"
        />
    );
}

/* A ready-made skeleton for the content admin's list view — the most common
 * loading state in the product. Mirrors the real .as-row geometry. */
export function SkeletonRows({ count = 4 }) {
    return (
        <div className="adze-skeleton-rows" role="status" aria-label="Loading">
            {Array.from({ length: count }, (_, i) => (
                <div key={i} className="adze-skeleton-row">
                    <Skeleton variant="thumb" />
                    <div className="adze-skeleton-row__text">
                        <Skeleton variant="text" width="42%" />
                        <Skeleton variant="text" width="24%" />
                    </div>
                </div>
            ))}
        </div>
    );
}

export const css = `
.adze-skeleton {
    display: block;
    border-radius: var(--adze-radius-sm);
    background: linear-gradient(
        90deg,
        var(--adze-bg-sunken) 25%,
        color-mix(in srgb, var(--adze-bg-sunken) 60%, var(--adze-surface)) 50%,
        var(--adze-bg-sunken) 75%
    );
    background-size: 200% 100%;
    animation: adze-shimmer 1.6s linear infinite;
}

.adze-skeleton--text   { height: 13px; width: 100%; }
.adze-skeleton--title  { height: 22px; width: 40%; border-radius: var(--adze-radius-sm); }
.adze-skeleton--block  { height: 120px; width: 100%; border-radius: var(--adze-radius-md); }
.adze-skeleton--circle { height: 36px; width: 36px; border-radius: var(--adze-radius-pill); }
.adze-skeleton--thumb  { height: 48px; width: 48px; border-radius: var(--adze-radius-md); flex: 0 0 auto; }

.adze-skeleton-stack { display: flex; flex-direction: column; gap: var(--adze-space-2); }

.adze-skeleton-rows { display: flex; flex-direction: column; }
.adze-skeleton-row {
    display: flex; align-items: center; gap: var(--adze-space-3);
    padding: var(--adze-space-3) 0;
    border-bottom: 1px solid var(--adze-border);
}
.adze-skeleton-row__text {
    display: flex; flex-direction: column; gap: var(--adze-space-2);
    flex: 1;
}
`;
