import React from "react";

/**
 * Last Place — TextLink
 * The signature inline hyperlink. Blue, underlined, the underline lifts on
 * hover. An optional arrow variant for "↳ go" affordances.
 */
export function TextLink({
  href = "#",
  arrow = false,
  muted = false,
  children,
  ...rest
}) {
  const [hover, setHover] = React.useState(false);
  const style = {
    color: muted ? "var(--lp-black)" : "var(--lp-blue)",
    fontFamily: "inherit",
    textDecoration: "underline",
    textDecorationThickness: "1px",
    textUnderlineOffset: "2px",
    textDecorationColor: hover ? "transparent" : "currentColor",
    cursor: "pointer",
    transition: "text-decoration-color var(--dur-fast) var(--ease-out)",
  };
  return (
    <a
      href={href}
      style={style}
      onMouseEnter={() => setHover(true)}
      onMouseLeave={() => setHover(false)}
      {...rest}
    >
      {arrow && <span aria-hidden="true" style={{ marginRight: "0.4em" }}>↳</span>}
      {children}
    </a>
  );
}
