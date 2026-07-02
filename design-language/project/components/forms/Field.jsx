import React from "react";

/**
 * Last Place — Field
 * A text input set as an editorial underline: mono label, serif input,
 * hairline rule that turns blue on focus. Supports textarea and hint/error.
 */
export function Field({
  label,
  hint,
  error,
  type = "text",
  multiline = false,
  value,
  onChange,
  placeholder,
  id,
  ...rest
}) {
  const [focus, setFocus] = React.useState(false);
  const fieldId = id || (label ? "f-" + String(label).toLowerCase().replace(/\s+/g, "-") : undefined);

  const inputStyle = {
    width: "100%",
    border: "none",
    borderBottom: "1px solid",
    borderColor: error ? "var(--lp-green-bright)" : focus ? "var(--lp-blue)" : "var(--border-hairline)",
    background: "transparent",
    padding: "10px 0",
    fontFamily: "var(--font-serif)",
    fontSize: "19px",
    lineHeight: 1.5,
    color: "var(--text-body)",
    outline: "none",
    borderRadius: 0,
    transition: "border-color var(--dur-base) var(--ease-out)",
    resize: multiline ? "vertical" : undefined,
  };

  const Tag = multiline ? "textarea" : "input";

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "6px" }}>
      {label && (
        <label
          htmlFor={fieldId}
          style={{
            fontFamily: "var(--font-mono)",
            fontSize: "11px",
            letterSpacing: "0.18em",
            textTransform: "uppercase",
            color: "var(--text-muted)",
          }}
        >
          {label}
        </label>
      )}
      <Tag
        id={fieldId}
        type={multiline ? undefined : type}
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        rows={multiline ? 3 : undefined}
        onFocus={() => setFocus(true)}
        onBlur={() => setFocus(false)}
        style={inputStyle}
        {...rest}
      />
      {(hint || error) && (
        <span
          style={{
            fontFamily: "var(--font-mono)",
            fontSize: "12px",
            color: error ? "var(--lp-green-bright)" : "var(--text-faint)",
          }}
        >
          {error || hint}
        </span>
      )}
    </div>
  );
}
