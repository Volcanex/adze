/* ProgressBar — the Adze loading bar.
 *
 * Two modes, and picking the right one is the whole job:
 *
 *   determinate   — you know how far along you are (uploads, publish steps,
 *                   batch operations). ALWAYS prefer this. A real percentage
 *                   is the difference between "working" and "trust me".
 *   indeterminate — you genuinely can't know (a request in flight). A band
 *                   sweeps the track. Never fake a determinate bar with a
 *                   timer; users clock it immediately and it reads as a lie.
 *
 * The old admin had no loading feedback at all — zero spinners, zero
 * skeletons. Publishing a site simply froze until it didn't. This component
 * plus Skeleton is the fix.
 */

export function ProgressBar({
    value = null,           // 0–100, or null for indeterminate
    label = null,           // mono label above the track
    detail = null,          // right-aligned secondary text ("3 of 12")
    size = 'md',            // 'sm' | 'md'
    tone = 'accent',        // 'accent' | 'success' | 'danger'
    showValue = true,       // render the % readout when determinate
}) {
    const indeterminate = value === null || value === undefined;
    const pct = indeterminate ? 0 : Math.max(0, Math.min(100, value));

    return (
        <div
            className={[
                'adze-progress',
                `adze-progress--${size}`,
                `adze-progress--${tone}`,
                indeterminate && 'adze-progress--indeterminate',
            ].filter(Boolean).join(' ')}
            role="progressbar"
            aria-valuenow={indeterminate ? undefined : pct}
            aria-valuemin={indeterminate ? undefined : 0}
            aria-valuemax={indeterminate ? undefined : 100}
            aria-label={label || 'Loading'}
        >
            {(label || detail || (showValue && !indeterminate)) && (
                <div className="adze-progress__head">
                    {label && <span className="adze-label">{label}</span>}
                    <span className="adze-progress__meta">
                        {detail && <span className="adze-progress__detail">{detail}</span>}
                        {showValue && !indeterminate && (
                            <span className="adze-numeric adze-progress__value">{Math.round(pct)}%</span>
                        )}
                    </span>
                </div>
            )}
            <div className="adze-progress__track">
                <div
                    className="adze-progress__bar"
                    style={indeterminate ? undefined : { width: `${pct}%` }}
                />
            </div>
        </div>
    );
}

export const css = `
.adze-progress { display: flex; flex-direction: column; gap: var(--adze-space-2); width: 100%; }

.adze-progress__head {
    display: flex; align-items: baseline; justify-content: space-between;
    gap: var(--adze-space-3);
}
.adze-progress__meta {
    display: flex; align-items: baseline; gap: var(--adze-space-2);
    margin-left: auto;
}
.adze-progress__detail {
    font-size: var(--adze-text-xs);
    color: var(--adze-text-faint);
}
.adze-progress__value {
    font-size: var(--adze-text-2xs);
    color: var(--adze-text-muted);
    /* tabular-nums via .adze-numeric — stops the readout jittering as it
       counts up through 9→10→11 */
}

.adze-progress__track {
    position: relative;
    width: 100%;
    height: 6px;
    background: var(--adze-bg-sunken);
    border-radius: var(--adze-radius-pill);
    overflow: hidden;
}
.adze-progress--sm .adze-progress__track { height: 4px; }

.adze-progress__bar {
    height: 100%;
    width: 0;
    background: var(--adze-accent);
    border-radius: var(--adze-radius-pill);
    /* Width, not transform — a transform-scaled bar distorts the rounded cap.
       Width animation is cheap enough at this size. */
    transition: width var(--adze-dur) var(--adze-ease-out);
}
.adze-progress--success .adze-progress__bar { background: var(--adze-success); }
.adze-progress--danger  .adze-progress__bar { background: var(--adze-danger); }

/* Indeterminate: a 40%-wide band sweeps the track on a loop. */
.adze-progress--indeterminate .adze-progress__bar {
    width: 40%;
    transition: none;
    transform-origin: left center;
    animation: adze-sweep 1.4s var(--adze-ease-in-out) infinite;
}
`;
