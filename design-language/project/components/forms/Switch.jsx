import React from "react";

/**
 * Last Place — Switch
 * A flat, square-cornered toggle. Track fills blue when on. No drop shadow,
 * no bounce — just a clean slide.
 */
export function Switch({ checked = false, onChange, label, disabled = false, ...rest }) {
  return (
    <label
      style={{
        display: "inline-flex",
        alignItems: "center",
        gap: "14px",
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
          width: "44px",
          height: "24px",
          flex: "none",
          padding: "2px",
          border: "1px solid",
          borderColor: checked ? "var(--lp-blue)" : "var(--lp-black)",
          background: checked ? "var(--lp-blue)" : "transparent",
          display: "flex",
          justifyContent: checked ? "flex-end" : "flex-start",
          alignItems: "center",
          transition: "background var(--dur-base) var(--ease-out), border-color var(--dur-base) var(--ease-out)",
        }}
      >
        <span
          style={{
            width: "18px",
            height: "18px",
            background: checked ? "#fff" : "var(--lp-black)",
            transition: "background var(--dur-base) var(--ease-out)",
          }}
        />
      </span>
      {label}
    </label>
  );
}
