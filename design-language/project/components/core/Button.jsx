import React from "react";

/**
 * Last Place — Button
 * Square-cornered, editorial. Blue fill for the one important action,
 * an inked outline for the rest, and a bare link variant for inline use.
 */
export function Button({
  variant = "primary",
  size = "md",
  href,
  type = "button",
  disabled = false,
  block = false,
  onClick,
  children,
  ...rest
}) {
  const pad = {
    sm: "8px 16px",
    md: "12px 22px",
    lg: "16px 30px",
  }[size] || "12px 22px";

  const fontSize = { sm: 12, md: 13, lg: 14 }[size] || 13;

  const base = {
    display: block ? "flex" : "inline-flex",
    width: block ? "100%" : "auto",
    alignItems: "center",
    justifyContent: "center",
    gap: "10px",
    padding: pad,
    fontFamily: "var(--font-mono)",
    fontSize: fontSize + "px",
    letterSpacing: "0.14em",
    textTransform: "uppercase",
    lineHeight: 1,
    borderRadius: "var(--radius-0)",
    border: "1px solid transparent",
    cursor: disabled ? "not-allowed" : "pointer",
    textDecoration: "none",
    opacity: disabled ? 0.4 : 1,
    transition:
      "background var(--dur-fast) var(--ease-out), color var(--dur-fast) var(--ease-out), border-color var(--dur-fast) var(--ease-out)",
    userSelect: "none",
  };

  const variants = {
    primary: {
      background: "var(--lp-blue)",
      color: "var(--lp-white)",
      borderColor: "var(--lp-blue)",
    },
    secondary: {
      background: "transparent",
      color: "var(--lp-black)",
      borderColor: "var(--lp-black)",
    },
    ghost: {
      background: "transparent",
      color: "var(--lp-black)",
      borderColor: "transparent",
    },
    green: {
      background: "var(--lp-green)",
      color: "var(--lp-white)",
      borderColor: "var(--lp-green)",
    },
    link: {
      background: "transparent",
      color: "var(--lp-blue)",
      borderColor: "transparent",
      padding: "0",
      textTransform: "none",
      letterSpacing: "0",
      fontFamily: "var(--font-serif)",
      fontSize: (fontSize + 5) + "px",
      textDecoration: "underline",
      textUnderlineOffset: "2px",
    },
  };

  const style = { ...base, ...(variants[variant] || variants.primary) };

  const hoverIn = (e) => {
    if (disabled) return;
    const el = e.currentTarget;
    if (variant === "primary") el.style.background = "var(--lp-blue-deep)";
    else if (variant === "green") el.style.background = "var(--lp-green-bright)";
    else if (variant === "secondary") el.style.background = "var(--lp-ink-04)";
    else if (variant === "ghost") el.style.background = "var(--lp-ink-04)";
    else if (variant === "link") el.style.textDecorationColor = "transparent";
  };
  const hoverOut = (e) => {
    const el = e.currentTarget;
    el.style.background = (variants[variant] || variants.primary).background;
    if (variant === "link") el.style.textDecorationColor = "";
  };

  const Tag = href ? "a" : "button";
  const tagProps = href ? { href } : { type, disabled };

  return (
    <Tag
      {...tagProps}
      onClick={onClick}
      onMouseEnter={hoverIn}
      onMouseLeave={hoverOut}
      style={style}
      {...rest}
    >
      {children}
    </Tag>
  );
}
