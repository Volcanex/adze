/* Tag — a small mono chip for status, category or count.
 *
 * This is where the mono voice earns its place. Tags are scanned, not read,
 * so they take JetBrains Mono at 11px with open tracking. It's the strongest
 * carry-over from the old Adze identity and the reason the new system still
 * reads as Adze rather than as generic Inter.
 *
 * Status tones are NOT artist-overridable (see tokens/colors.css) — "live"
 * must look the same on every artist's admin, whatever their accent is.
 */

export function Tag({
    children,
    tone = 'neutral',   // 'neutral' | 'accent' | 'success' | 'warn' | 'danger'
    dot = false,        // leading status dot
    size = 'md',        // 'sm' | 'md'
}) {
    return (
        <span className={`adze-tag adze-tag--${tone} adze-tag--${size}`}>
            {dot && <span className="adze-tag__dot" aria-hidden="true" />}
            {children}
        </span>
    );
}

export const css = `
.adze-tag {
    display: inline-flex; align-items: center; gap: var(--adze-space-1);
    padding: 3px var(--adze-space-2);
    border-radius: var(--adze-radius-sm);
    font-family: var(--adze-font-mono);
    font-size: var(--adze-text-2xs);
    font-weight: var(--adze-weight-medium);
    line-height: 1.4;
    letter-spacing: var(--adze-tracking-label);
    text-transform: uppercase;
    white-space: nowrap;
}
.adze-tag--sm { padding: 1px var(--adze-space-1); font-size: 10px; }

.adze-tag__dot {
    width: 5px; height: 5px; border-radius: var(--adze-radius-pill);
    background: currentColor; flex: 0 0 auto;
}

.adze-tag--neutral { background: var(--adze-bg-sunken);    color: var(--adze-text-muted); }
.adze-tag--accent  { background: var(--adze-accent-soft);  color: var(--adze-accent); }
.adze-tag--success { background: var(--adze-success-soft); color: var(--adze-success); }
.adze-tag--warn    { background: var(--adze-warn-soft);    color: var(--adze-warn); }
.adze-tag--danger  { background: var(--adze-danger-soft);  color: var(--adze-danger); }
`;
