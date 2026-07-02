import React from "react";

/**
 * Last Place — Checkbox
 * A square checkbox (the brand never rounds). Blue fill when checked,
 * a serif label alongside.
 */
export function Checkbox({ checked = false, onChange, label, disabled = false, ...rest }) {
  return (
    <label
      style={{
        display: "inline-flex",
        alignItems: "center",
        gap: "12px",
        cursor: disabled ? "not-allowed" : "pointer",
        opacity: disabled ? 0.4 : 1,
        fontFamily: "var(--font-serif)",
        fontSize: "18px",
        color: "var(--text-body)",
      }}
      {...rest}
    >
      <span
        onClick={() => !disabled && onChange && onChange(!checked)}
        style={{
          width: "20px",
          height: "20px",
          flex: "none",
          border: "1px solid",
          borderColor: checked ? "var(--lp-blue)" : "var(--lp-black)",
          background: checked ? "var(--lp-blue)" : "transparent",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          transition: "background var(--dur-fast) var(--ease-out), border-color var(--dur-fast) var(--ease-out)",
        }}
      >
        {checked && (
          <svg width="12" height="12" viewBox="0 0 12 12" fill="none" aria-hidden="true">
            <path d="M2 6.5L5 9.5L10 3" stroke="#fff" strokeWidth="1.6" strokeLinecap="square" />
          </svg>
        )}
      </span>
      {label}
    </label>
  );
}
