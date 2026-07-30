/* Select — native <select> with Adze chrome.
 *
 * Deliberately native rather than a custom listbox. A native select gets
 * correct keyboard behaviour, correct screen-reader semantics, and the
 * platform picker on mobile — all of which a hand-rolled dropdown has to
 * reimplement and usually gets wrong. Only build a custom one if you need
 * multi-select with search, and then build it properly with a combobox
 * pattern.
 *
 * The chevron is a background SVG so it can't be clicked separately from the
 * control.
 */

export function Select({ options = [], placeholder = null, size = 'md', ...rest }) {
    return (
        <div className="adze-select-wrap">
            <select className={`adze-input adze-select adze-input--${size}`} {...rest}>
                {placeholder && <option value="">{placeholder}</option>}
                {options.map(opt => {
                    const value = typeof opt === 'string' ? opt : opt.value;
                    const label = typeof opt === 'string' ? opt : opt.label;
                    return <option key={value} value={value}>{label}</option>;
                })}
            </select>
            <i className="ph ph-caret-down adze-select__caret" aria-hidden="true" />
        </div>
    );
}

export const css = `
.adze-select-wrap { position: relative; display: block; }
.adze-select {
    appearance: none;
    padding-right: var(--adze-space-8);
    cursor: pointer;
}
.adze-select__caret {
    position: absolute; right: var(--adze-space-3); top: 50%;
    transform: translateY(-50%);
    pointer-events: none;
    color: var(--adze-text-faint);
    font-size: 0.9em;
    transition: color var(--adze-dur-instant) var(--adze-ease-out);
}
.adze-select-wrap:hover .adze-select__caret { color: var(--adze-text-muted); }
`;
