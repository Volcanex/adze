import React from "react";

/**
 * Last Place — Card
 * A restrained surface: hairline border, square corners, lots of inner air.
 * Use `media` for a project thumbnail; `eyebrow` for a mono label.
 */
export function Card({
  eyebrow,
  title,
  meta,
  media,
  mediaBg = "var(--lp-blue)",
  href,
  children,
  ...rest
}) {
  const [hover, setHover] = React.useState(false);
  const Tag = href ? "a" : "div";
  const style = {
    display: "block",
    textDecoration: "none",
    color: "var(--text-body)",
    background: "var(--surface-card)",
    border: "1px solid",
    borderColor: hover && href ? "var(--lp-black)" : "var(--border-hairline)",
    borderRadius: "var(--radius-0)",
    transition: "border-color var(--dur-base) var(--ease-out)",
    cursor: href ? "pointer" : "default",
  };

  return (
    <Tag
      href={href}
      style={style}
      onMouseEnter={() => setHover(true)}
      onMouseLeave={() => setHover(false)}
      {...rest}
    >
      {media && (
        <div
          style={{
            background: mediaBg,
            aspectRatio: "4 / 3",
            overflow: "hidden",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
          }}
        >
          {typeof media === "string" ? (
            <img
              src={media}
              alt={title || ""}
              style={{
                width: "100%",
                height: "100%",
                objectFit: "cover",
                transition: "transform var(--dur-slow) var(--ease-out)",
                transform: hover && href ? "scale(1.03)" : "scale(1)",
              }}
            />
          ) : (
            media
          )}
        </div>
      )}
      <div style={{ padding: "var(--space-5)" }}>
        {eyebrow && (
          <div
            style={{
              fontFamily: "var(--font-mono)",
              fontSize: "11px",
              letterSpacing: "0.18em",
              textTransform: "uppercase",
              color: "var(--text-muted)",
              marginBottom: "10px",
            }}
          >
            {eyebrow}
          </div>
        )}
        {title && (
          <div
            style={{
              fontFamily: "var(--font-serif)",
              fontSize: "26px",
              lineHeight: 1.1,
              letterSpacing: "-0.01em",
            }}
          >
            {title}
          </div>
        )}
        {children && (
          <div style={{ marginTop: "10px", fontFamily: "var(--font-serif)", fontSize: "16px", lineHeight: 1.5, color: "var(--text-muted)" }}>
            {children}
          </div>
        )}
        {meta && (
          <div
            style={{
              fontFamily: "var(--font-mono)",
              fontSize: "12px",
              color: "var(--text-faint)",
              marginTop: "16px",
            }}
          >
            {meta}
          </div>
        )}
      </div>
    </Tag>
  );
}
