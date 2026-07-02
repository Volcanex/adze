import React from "react";

/**
 * Last Place — Tag
 * A small monospace, tracked, uppercase label. Two looks: bare (default)
 * and outlined. Blue or ink or forest tone.
 */
export function Tag({
  tone = "ink",
  outline = false,
  children,
  ...rest
}) {
  const color = {
    ink: "var(--lp-black)",
    blue: "var(--lp-blue)",
    green: "var(--lp-green)",
    muted: "var(--lp-ink-55)",
  }[tone] || "var(--lp-black)";

  const style = {
    display: "inline-flex",
    alignItems: "center",
    fontFamily: "var(--font-mono)",
    fontSize: "11px",
    letterSpacing: "0.18em",
    textTransform: "uppercase",
    lineHeight: 1,
    color,
    padding: outline ? "6px 10px" : "0",
    border: outline ? "1px solid currentColor" : "none",
    borderRadius: "var(--radius-0)",
    whiteSpace: "nowrap",
  };
  return (
    <span style={style} {...rest}>
      {children}
    </span>
  );
}
