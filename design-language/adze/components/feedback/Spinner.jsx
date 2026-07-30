/* Spinner — indeterminate activity for a small, bounded area.
 *
 * Reach order for loading states, strictly:
 *   1. Skeleton     — you know the shape of what's coming. Best.
 *   2. ProgressBar  — you know how far along you are.
 *   3. Spinner      — you know neither. Last resort.
 *
 * A full-page spinner is almost always the wrong answer; it tells the user
 * nothing except that they should wait. Use one inside a button while a save
 * is in flight, or beside an inline action. If the whole screen is loading,
 * use SkeletonRows instead.
 *
 * `delay` exists because a spinner that flashes for 80ms and vanishes reads
 * as a glitch. Below ~400ms, showing nothing feels faster than showing
 * feedback. Default is 300ms.
 */

export function Spinner({
    size = 'md',        // 'sm' | 'md' | 'lg'
    tone = 'current',   // 'current' (inherits colour) | 'accent' | 'muted'
    label = 'Loading',  // screen-reader text
    delay = 300,        // ms before appearing; 0 to show immediately
}) {
    return (
        <span
            className={[
                'adze-spinner',
                `adze-spinner--${size}`,
                `adze-spinner--${tone}`,
                delay > 0 && 'adze-spinner--delayed',
            ].filter(Boolean).join(' ')}
            style={delay > 0 ? { animationDelay: `0s, ${delay}ms` } : undefined}
            role="status"
            aria-label={label}
        />
    );
}

export const css = `
.adze-spinner {
    display: inline-block;
    flex: 0 0 auto;
    border-radius: var(--adze-radius-pill);
    /* A 3/4 arc rather than a full ring — the gap is what makes rotation
       legible. A full ring appears static however fast it spins. */
    border: 2px solid color-mix(in srgb, currentColor 20%, transparent);
    border-top-color: currentColor;
    animation: adze-spin 0.7s linear infinite;
    vertical-align: -0.125em;
}

.adze-spinner--sm { width: 12px; height: 12px; border-width: 1.5px; }
.adze-spinner--md { width: 16px; height: 16px; }
.adze-spinner--lg { width: 24px; height: 24px; border-width: 3px; }

.adze-spinner--accent { color: var(--adze-accent); }
.adze-spinner--muted  { color: var(--adze-text-faint); }

/* Two animations: the spin, plus a one-shot fade that holds the spinner
   invisible until the delay elapses. Cheaper and more reliable than a
   setTimeout in every call site. */
.adze-spinner--delayed {
    animation: adze-spin 0.7s linear infinite, adze-fade-in 1ms linear forwards;
    opacity: 0;
}
`;
