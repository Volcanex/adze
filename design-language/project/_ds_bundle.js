/* @ds-bundle: {"format":3,"namespace":"LastPlaceDesignSystem_2f29fe","components":[{"name":"Button","sourcePath":"components/core/Button.jsx"},{"name":"Card","sourcePath":"components/core/Card.jsx"},{"name":"Tag","sourcePath":"components/core/Tag.jsx"},{"name":"TextLink","sourcePath":"components/core/TextLink.jsx"},{"name":"Checkbox","sourcePath":"components/forms/Checkbox.jsx"},{"name":"Field","sourcePath":"components/forms/Field.jsx"},{"name":"Switch","sourcePath":"components/forms/Switch.jsx"}],"sourceHashes":{"components/core/Button.jsx":"91357bfd0945","components/core/Card.jsx":"ebe55eae5a5f","components/core/Tag.jsx":"c507fad8848f","components/core/TextLink.jsx":"82c4f48c48bd","components/forms/Checkbox.jsx":"1d97f4616295","components/forms/Field.jsx":"67a307e40642","components/forms/Switch.jsx":"99cdd3e6cf3a","ui_kits/studio-site/ContactScreen.jsx":"951666408c71","ui_kits/studio-site/Footer.jsx":"de9fa195e542","ui_kits/studio-site/Header.jsx":"01875f03d99a","ui_kits/studio-site/HomeScreen.jsx":"19a4775804a0","ui_kits/studio-site/StudioScreen.jsx":"487ce8446795","ui_kits/studio-site/WorkScreen.jsx":"e5658a03e5ab","ui_kits/studio-site/projects.js":"95d76faf6a72"},"inlinedExternals":[],"unexposedExports":[]} */

(() => {

const __ds_ns = (window.LastPlaceDesignSystem_2f29fe = window.LastPlaceDesignSystem_2f29fe || {});

const __ds_scope = {};

(__ds_ns.__errors = __ds_ns.__errors || []);

// components/core/Button.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
/**
 * Last Place — Button
 * Square-cornered, editorial. Blue fill for the one important action,
 * an inked outline for the rest, and a bare link variant for inline use.
 */
function Button({
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
    lg: "16px 30px"
  }[size] || "12px 22px";
  const fontSize = {
    sm: 12,
    md: 13,
    lg: 14
  }[size] || 13;
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
    transition: "background var(--dur-fast) var(--ease-out), color var(--dur-fast) var(--ease-out), border-color var(--dur-fast) var(--ease-out)",
    userSelect: "none"
  };
  const variants = {
    primary: {
      background: "var(--lp-blue)",
      color: "var(--lp-white)",
      borderColor: "var(--lp-blue)"
    },
    secondary: {
      background: "transparent",
      color: "var(--lp-black)",
      borderColor: "var(--lp-black)"
    },
    ghost: {
      background: "transparent",
      color: "var(--lp-black)",
      borderColor: "transparent"
    },
    green: {
      background: "var(--lp-green)",
      color: "var(--lp-white)",
      borderColor: "var(--lp-green)"
    },
    link: {
      background: "transparent",
      color: "var(--lp-blue)",
      borderColor: "transparent",
      padding: "0",
      textTransform: "none",
      letterSpacing: "0",
      fontFamily: "var(--font-serif)",
      fontSize: fontSize + 5 + "px",
      textDecoration: "underline",
      textUnderlineOffset: "2px"
    }
  };
  const style = {
    ...base,
    ...(variants[variant] || variants.primary)
  };
  const hoverIn = e => {
    if (disabled) return;
    const el = e.currentTarget;
    if (variant === "primary") el.style.background = "var(--lp-blue-deep)";else if (variant === "green") el.style.background = "var(--lp-green-bright)";else if (variant === "secondary") el.style.background = "var(--lp-ink-04)";else if (variant === "ghost") el.style.background = "var(--lp-ink-04)";else if (variant === "link") el.style.textDecorationColor = "transparent";
  };
  const hoverOut = e => {
    const el = e.currentTarget;
    el.style.background = (variants[variant] || variants.primary).background;
    if (variant === "link") el.style.textDecorationColor = "";
  };
  const Tag = href ? "a" : "button";
  const tagProps = href ? {
    href
  } : {
    type,
    disabled
  };
  return /*#__PURE__*/React.createElement(Tag, _extends({}, tagProps, {
    onClick: onClick,
    onMouseEnter: hoverIn,
    onMouseLeave: hoverOut,
    style: style
  }, rest), children);
}
Object.assign(__ds_scope, { Button });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/core/Button.jsx", error: String((e && e.message) || e) }); }

// components/core/Card.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
/**
 * Last Place — Card
 * A restrained surface: hairline border, square corners, lots of inner air.
 * Use `media` for a project thumbnail; `eyebrow` for a mono label.
 */
function Card({
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
    cursor: href ? "pointer" : "default"
  };
  return /*#__PURE__*/React.createElement(Tag, _extends({
    href: href,
    style: style,
    onMouseEnter: () => setHover(true),
    onMouseLeave: () => setHover(false)
  }, rest), media && /*#__PURE__*/React.createElement("div", {
    style: {
      background: mediaBg,
      aspectRatio: "4 / 3",
      overflow: "hidden",
      display: "flex",
      alignItems: "center",
      justifyContent: "center"
    }
  }, typeof media === "string" ? /*#__PURE__*/React.createElement("img", {
    src: media,
    alt: title || "",
    style: {
      width: "100%",
      height: "100%",
      objectFit: "cover",
      transition: "transform var(--dur-slow) var(--ease-out)",
      transform: hover && href ? "scale(1.03)" : "scale(1)"
    }
  }) : media), /*#__PURE__*/React.createElement("div", {
    style: {
      padding: "var(--space-5)"
    }
  }, eyebrow && /*#__PURE__*/React.createElement("div", {
    style: {
      fontFamily: "var(--font-mono)",
      fontSize: "11px",
      letterSpacing: "0.18em",
      textTransform: "uppercase",
      color: "var(--text-muted)",
      marginBottom: "10px"
    }
  }, eyebrow), title && /*#__PURE__*/React.createElement("div", {
    style: {
      fontFamily: "var(--font-serif)",
      fontSize: "26px",
      lineHeight: 1.1,
      letterSpacing: "-0.01em"
    }
  }, title), children && /*#__PURE__*/React.createElement("div", {
    style: {
      marginTop: "10px",
      fontFamily: "var(--font-serif)",
      fontSize: "16px",
      lineHeight: 1.5,
      color: "var(--text-muted)"
    }
  }, children), meta && /*#__PURE__*/React.createElement("div", {
    style: {
      fontFamily: "var(--font-mono)",
      fontSize: "12px",
      color: "var(--text-faint)",
      marginTop: "16px"
    }
  }, meta)));
}
Object.assign(__ds_scope, { Card });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/core/Card.jsx", error: String((e && e.message) || e) }); }

// components/core/Tag.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
/**
 * Last Place — Tag
 * A small monospace, tracked, uppercase label. Two looks: bare (default)
 * and outlined. Blue or ink or forest tone.
 */
function Tag({
  tone = "ink",
  outline = false,
  children,
  ...rest
}) {
  const color = {
    ink: "var(--lp-black)",
    blue: "var(--lp-blue)",
    green: "var(--lp-green)",
    muted: "var(--lp-ink-55)"
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
    whiteSpace: "nowrap"
  };
  return /*#__PURE__*/React.createElement("span", _extends({
    style: style
  }, rest), children);
}
Object.assign(__ds_scope, { Tag });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/core/Tag.jsx", error: String((e && e.message) || e) }); }

// components/core/TextLink.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
/**
 * Last Place — TextLink
 * The signature inline hyperlink. Blue, underlined, the underline lifts on
 * hover. An optional arrow variant for "↳ go" affordances.
 */
function TextLink({
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
    transition: "text-decoration-color var(--dur-fast) var(--ease-out)"
  };
  return /*#__PURE__*/React.createElement("a", _extends({
    href: href,
    style: style,
    onMouseEnter: () => setHover(true),
    onMouseLeave: () => setHover(false)
  }, rest), arrow && /*#__PURE__*/React.createElement("span", {
    "aria-hidden": "true",
    style: {
      marginRight: "0.4em"
    }
  }, "\u21B3"), children);
}
Object.assign(__ds_scope, { TextLink });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/core/TextLink.jsx", error: String((e && e.message) || e) }); }

// components/forms/Checkbox.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
/**
 * Last Place — Checkbox
 * A square checkbox (the brand never rounds). Blue fill when checked,
 * a serif label alongside.
 */
function Checkbox({
  checked = false,
  onChange,
  label,
  disabled = false,
  ...rest
}) {
  return /*#__PURE__*/React.createElement("label", _extends({
    style: {
      display: "inline-flex",
      alignItems: "center",
      gap: "12px",
      cursor: disabled ? "not-allowed" : "pointer",
      opacity: disabled ? 0.4 : 1,
      fontFamily: "var(--font-serif)",
      fontSize: "18px",
      color: "var(--text-body)"
    }
  }, rest), /*#__PURE__*/React.createElement("span", {
    onClick: () => !disabled && onChange && onChange(!checked),
    style: {
      width: "20px",
      height: "20px",
      flex: "none",
      border: "1px solid",
      borderColor: checked ? "var(--lp-blue)" : "var(--lp-black)",
      background: checked ? "var(--lp-blue)" : "transparent",
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      transition: "background var(--dur-fast) var(--ease-out), border-color var(--dur-fast) var(--ease-out)"
    }
  }, checked && /*#__PURE__*/React.createElement("svg", {
    width: "12",
    height: "12",
    viewBox: "0 0 12 12",
    fill: "none",
    "aria-hidden": "true"
  }, /*#__PURE__*/React.createElement("path", {
    d: "M2 6.5L5 9.5L10 3",
    stroke: "#fff",
    strokeWidth: "1.6",
    strokeLinecap: "square"
  }))), label);
}
Object.assign(__ds_scope, { Checkbox });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/forms/Checkbox.jsx", error: String((e && e.message) || e) }); }

// components/forms/Field.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
/**
 * Last Place — Field
 * A text input set as an editorial underline: mono label, serif input,
 * hairline rule that turns blue on focus. Supports textarea and hint/error.
 */
function Field({
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
    resize: multiline ? "vertical" : undefined
  };
  const Tag = multiline ? "textarea" : "input";
  return /*#__PURE__*/React.createElement("div", {
    style: {
      display: "flex",
      flexDirection: "column",
      gap: "6px"
    }
  }, label && /*#__PURE__*/React.createElement("label", {
    htmlFor: fieldId,
    style: {
      fontFamily: "var(--font-mono)",
      fontSize: "11px",
      letterSpacing: "0.18em",
      textTransform: "uppercase",
      color: "var(--text-muted)"
    }
  }, label), /*#__PURE__*/React.createElement(Tag, _extends({
    id: fieldId,
    type: multiline ? undefined : type,
    value: value,
    onChange: onChange,
    placeholder: placeholder,
    rows: multiline ? 3 : undefined,
    onFocus: () => setFocus(true),
    onBlur: () => setFocus(false),
    style: inputStyle
  }, rest)), (hint || error) && /*#__PURE__*/React.createElement("span", {
    style: {
      fontFamily: "var(--font-mono)",
      fontSize: "12px",
      color: error ? "var(--lp-green-bright)" : "var(--text-faint)"
    }
  }, error || hint));
}
Object.assign(__ds_scope, { Field });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/forms/Field.jsx", error: String((e && e.message) || e) }); }

// components/forms/Switch.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
/**
 * Last Place — Switch
 * A flat, square-cornered toggle. Track fills blue when on. No drop shadow,
 * no bounce — just a clean slide.
 */
function Switch({
  checked = false,
  onChange,
  label,
  disabled = false,
  ...rest
}) {
  return /*#__PURE__*/React.createElement("label", _extends({
    style: {
      display: "inline-flex",
      alignItems: "center",
      gap: "14px",
      cursor: disabled ? "not-allowed" : "pointer",
      opacity: disabled ? 0.4 : 1,
      fontFamily: "var(--font-serif)",
      fontSize: "18px",
      color: "var(--text-body)"
    }
  }, rest), /*#__PURE__*/React.createElement("span", {
    onClick: () => !disabled && onChange && onChange(!checked),
    style: {
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
      transition: "background var(--dur-base) var(--ease-out), border-color var(--dur-base) var(--ease-out)"
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      width: "18px",
      height: "18px",
      background: checked ? "#fff" : "var(--lp-black)",
      transition: "background var(--dur-base) var(--ease-out)"
    }
  })), label);
}
Object.assign(__ds_scope, { Switch });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/forms/Switch.jsx", error: String((e && e.message) || e) }); }

// ui_kits/studio-site/ContactScreen.jsx
try { (() => {
const contactStyles = {
  wrap: {
    display: "grid",
    gridTemplateColumns: "1fr 1fr",
    gap: "64px",
    padding: "var(--space-9) var(--page-margin) var(--space-10)",
    alignItems: "start"
  },
  eyebrow: {
    fontFamily: "var(--font-mono)",
    fontSize: "11.5px",
    letterSpacing: "0.2em",
    textTransform: "uppercase",
    color: "var(--text-muted)",
    marginBottom: "24px"
  },
  big: {
    fontFamily: "var(--font-serif)",
    fontWeight: 300,
    fontSize: "60px",
    lineHeight: 0.94,
    letterSpacing: "-0.02em",
    margin: "0 0 28px",
    maxWidth: "12ch"
  },
  blue: {
    color: "var(--lp-blue)"
  },
  p: {
    fontFamily: "var(--font-serif)",
    fontSize: "19px",
    lineHeight: 1.6,
    color: "var(--text-muted)",
    maxWidth: "40ch",
    margin: "0 0 32px"
  },
  detail: {
    fontFamily: "var(--font-mono)",
    fontSize: "13px",
    letterSpacing: "0.04em",
    color: "var(--text-body)",
    lineHeight: 2
  },
  form: {
    display: "flex",
    flexDirection: "column",
    gap: "28px"
  },
  budgetRow: {
    display: "flex",
    gap: "10px",
    flexWrap: "wrap"
  },
  chip: on => ({
    fontFamily: "var(--font-mono)",
    fontSize: "12px",
    letterSpacing: "0.1em",
    padding: "8px 14px",
    cursor: "pointer",
    border: "1px solid",
    borderColor: on ? "var(--lp-blue)" : "var(--border-strong)",
    background: on ? "var(--lp-blue)" : "transparent",
    color: on ? "#fff" : "var(--lp-black)",
    transition: "all var(--dur-fast) var(--ease-out)"
  }),
  chipLabel: {
    fontFamily: "var(--font-mono)",
    fontSize: "11px",
    letterSpacing: "0.18em",
    textTransform: "uppercase",
    color: "var(--text-muted)",
    marginBottom: "12px",
    display: "block"
  },
  sent: {
    fontFamily: "var(--font-serif)",
    fontSize: "26px",
    color: "var(--lp-green)",
    lineHeight: 1.4
  }
};
function ContactScreen() {
  const {
    Field,
    Checkbox,
    Button
  } = window.LastPlaceDesignSystem_2f29fe;
  const [budget, setBudget] = React.useState("£5–10k");
  const [keep, setKeep] = React.useState(true);
  const [sent, setSent] = React.useState(false);
  const budgets = ["< £5k", "£5–10k", "£10–25k", "£25k +"];
  return /*#__PURE__*/React.createElement("section", {
    style: contactStyles.wrap
  }, /*#__PURE__*/React.createElement("div", null, /*#__PURE__*/React.createElement("div", {
    style: contactStyles.eyebrow
  }, "Contact"), /*#__PURE__*/React.createElement("h1", {
    style: contactStyles.big
  }, "Let's make something ", /*#__PURE__*/React.createElement("span", {
    style: contactStyles.blue
  }, "quiet"), " and good."), /*#__PURE__*/React.createElement("p", {
    style: contactStyles.p
  }, "Tell us a little about the project. A sentence or two is plenty \u2014 we reply within a day, and there's no harm in just saying hello."), /*#__PURE__*/React.createElement("div", {
    style: contactStyles.detail
  }, "hello@lastplace.co.uk", /*#__PURE__*/React.createElement("br", null), "+44 (0)20 7946 0102", /*#__PURE__*/React.createElement("br", null), "Bradford \xB7 United Kingdom")), /*#__PURE__*/React.createElement("div", null, sent ? /*#__PURE__*/React.createElement("p", {
    style: contactStyles.sent
  }, "Thank you \u2014 that's landed.", /*#__PURE__*/React.createElement("br", null), "We'll be in touch within a day. \u21B3") : /*#__PURE__*/React.createElement("form", {
    style: contactStyles.form,
    onSubmit: e => {
      e.preventDefault();
      setSent(true);
    }
  }, /*#__PURE__*/React.createElement(Field, {
    label: "Your name",
    placeholder: "Jane Appleseed"
  }), /*#__PURE__*/React.createElement(Field, {
    label: "Email",
    type: "email",
    placeholder: "you@studio.com"
  }), /*#__PURE__*/React.createElement("div", null, /*#__PURE__*/React.createElement("span", {
    style: contactStyles.chipLabel
  }, "Budget"), /*#__PURE__*/React.createElement("div", {
    style: contactStyles.budgetRow
  }, budgets.map(b => /*#__PURE__*/React.createElement("span", {
    key: b,
    style: contactStyles.chip(budget === b),
    onClick: () => setBudget(b)
  }, b)))), /*#__PURE__*/React.createElement(Field, {
    label: "Tell us about the project",
    multiline: true,
    placeholder: "A sentence or two is plenty."
  }), /*#__PURE__*/React.createElement(Checkbox, {
    checked: keep,
    onChange: setKeep,
    label: "Keep me posted on studio news"
  }), /*#__PURE__*/React.createElement("div", null, /*#__PURE__*/React.createElement(Button, {
    variant: "primary",
    type: "submit"
  }, "Send it our way")))));
}
window.ContactScreen = ContactScreen;
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/studio-site/ContactScreen.jsx", error: String((e && e.message) || e) }); }

// ui_kits/studio-site/Footer.jsx
try { (() => {
const footerStyles = {
  wrap: {
    borderTop: "1px solid var(--border-hairline)",
    padding: "var(--space-9) var(--page-margin) var(--space-7)",
    display: "grid",
    gridTemplateColumns: "1.5fr 1fr 1fr",
    gap: "40px",
    alignItems: "start"
  },
  big: {
    fontFamily: "var(--font-serif)",
    fontWeight: 300,
    fontSize: "44px",
    lineHeight: 0.92,
    letterSpacing: "-0.015em",
    margin: 0,
    maxWidth: "12ch"
  },
  col: {
    display: "flex",
    flexDirection: "column",
    gap: "10px"
  },
  label: {
    fontFamily: "var(--font-mono)",
    fontSize: "11px",
    letterSpacing: "0.2em",
    textTransform: "uppercase",
    color: "var(--text-faint)",
    marginBottom: "6px"
  },
  line: {
    fontFamily: "var(--font-serif)",
    fontSize: "17px"
  },
  base: {
    gridColumn: "1 / -1",
    display: "flex",
    justifyContent: "space-between",
    borderTop: "1px solid var(--border-hairline)",
    paddingTop: "20px",
    marginTop: "20px",
    fontFamily: "var(--font-mono)",
    fontSize: "11px",
    letterSpacing: "0.12em",
    textTransform: "uppercase",
    color: "var(--text-faint)"
  }
};
function Footer({
  go
}) {
  const {
    TextLink
  } = window.LastPlaceDesignSystem_2f29fe;
  return /*#__PURE__*/React.createElement("footer", {
    style: footerStyles.wrap
  }, /*#__PURE__*/React.createElement("h2", {
    style: footerStyles.big
  }, "Last but not least."), /*#__PURE__*/React.createElement("div", {
    style: footerStyles.col
  }, /*#__PURE__*/React.createElement("span", {
    style: footerStyles.label
  }, "Studio"), /*#__PURE__*/React.createElement("span", {
    style: footerStyles.line
  }, /*#__PURE__*/React.createElement("a", {
    onClick: () => go("work"),
    style: {
      cursor: "pointer"
    }
  }, "Work")), /*#__PURE__*/React.createElement("span", {
    style: footerStyles.line
  }, /*#__PURE__*/React.createElement("a", {
    onClick: () => go("studio"),
    style: {
      cursor: "pointer"
    }
  }, "About")), /*#__PURE__*/React.createElement("span", {
    style: footerStyles.line
  }, /*#__PURE__*/React.createElement("a", {
    onClick: () => go("contact"),
    style: {
      cursor: "pointer"
    }
  }, "Contact"))), /*#__PURE__*/React.createElement("div", {
    style: footerStyles.col
  }, /*#__PURE__*/React.createElement("span", {
    style: footerStyles.label
  }, "Elsewhere"), /*#__PURE__*/React.createElement("span", {
    style: footerStyles.line
  }, /*#__PURE__*/React.createElement(TextLink, {
    href: "#"
  }, "Instagram")), /*#__PURE__*/React.createElement("span", {
    style: footerStyles.line
  }, /*#__PURE__*/React.createElement(TextLink, {
    href: "#"
  }, "Are.na")), /*#__PURE__*/React.createElement("span", {
    style: footerStyles.line
  }, /*#__PURE__*/React.createElement(TextLink, {
    href: "#"
  }, "hello@lastplace.co.uk"))), /*#__PURE__*/React.createElement("div", {
    style: footerStyles.base
  }, /*#__PURE__*/React.createElement("span", null, "\xA9 Last Place ", new Date().getFullYear()), /*#__PURE__*/React.createElement("span", null, "Made last, with care")));
}
window.Footer = Footer;
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/studio-site/Footer.jsx", error: String((e && e.message) || e) }); }

// ui_kits/studio-site/Header.jsx
try { (() => {
const LP = window.LastPlaceDesignSystem_2f29fe;
const headerStyles = {
  bar: {
    position: "sticky",
    top: 0,
    zIndex: 10,
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
    padding: "20px var(--page-margin)",
    background: "rgba(255,255,255,0.86)",
    backdropFilter: "saturate(180%) blur(8px)",
    borderBottom: "1px solid var(--border-hairline)"
  },
  brand: {
    display: "flex",
    alignItems: "center",
    gap: "14px",
    cursor: "pointer"
  },
  mono: {
    width: "34px",
    height: "34px",
    background: "var(--lp-blue)",
    color: "#fff",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    fontFamily: "var(--font-serif)",
    fontWeight: 300,
    fontSize: "20px",
    lineHeight: 1
  },
  word: {
    fontFamily: "var(--font-serif)",
    fontSize: "21px",
    letterSpacing: "0.01em"
  },
  nav: {
    display: "flex",
    gap: "32px",
    alignItems: "center"
  },
  link: active => ({
    fontFamily: "var(--font-mono)",
    fontSize: "11.5px",
    letterSpacing: "0.2em",
    textTransform: "uppercase",
    textDecoration: "none",
    cursor: "pointer",
    color: active ? "var(--lp-blue)" : "var(--lp-black)",
    transition: "color var(--dur-fast) var(--ease-out)"
  })
};
function Header({
  route,
  go
}) {
  const items = [["home", "Index"], ["work", "Work"], ["studio", "Studio"], ["contact", "Contact"]];
  return /*#__PURE__*/React.createElement("header", {
    style: headerStyles.bar
  }, /*#__PURE__*/React.createElement("div", {
    style: headerStyles.brand,
    onClick: () => go("home")
  }, /*#__PURE__*/React.createElement("div", {
    style: headerStyles.word
  }, "Last Place")), /*#__PURE__*/React.createElement("nav", {
    style: headerStyles.nav
  }, items.map(([key, label]) => /*#__PURE__*/React.createElement("a", {
    key: key,
    style: headerStyles.link(route === key),
    onClick: () => go(key),
    onMouseEnter: e => e.currentTarget.style.color = "var(--lp-blue)",
    onMouseLeave: e => e.currentTarget.style.color = route === key ? "var(--lp-blue)" : "var(--lp-black)"
  }, label))));
}
window.Header = Header;
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/studio-site/Header.jsx", error: String((e && e.message) || e) }); }

// ui_kits/studio-site/HomeScreen.jsx
try { (() => {
const homeStyles = {
  hero: {
    display: "grid",
    gridTemplateColumns: "1.25fr 0.75fr",
    gap: "48px",
    alignItems: "center",
    padding: "var(--space-10) var(--page-margin) var(--space-9)"
  },
  eyebrow: {
    fontFamily: "var(--font-mono)",
    fontSize: "11.5px",
    letterSpacing: "0.2em",
    textTransform: "uppercase",
    color: "var(--text-muted)",
    marginBottom: "28px"
  },
  h1: {
    fontFamily: "var(--font-serif)",
    fontWeight: 300,
    fontSize: "92px",
    lineHeight: 0.88,
    letterSpacing: "-0.02em",
    margin: "0 0 28px"
  },
  blue: {
    color: "var(--lp-blue)"
  },
  lede: {
    fontFamily: "var(--font-serif)",
    fontSize: "23px",
    lineHeight: 1.5,
    maxWidth: "40ch",
    color: "var(--text-body)",
    margin: "0 0 36px"
  },
  ctaRow: {
    display: "flex",
    gap: "16px",
    alignItems: "center"
  },
  art: {
    display: "flex",
    justifyContent: "center"
  },
  artImg: {
    width: "100%",
    maxWidth: "360px",
    height: "auto"
  },
  worksHead: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "baseline",
    padding: "0 var(--page-margin)",
    borderTop: "1px solid var(--border-hairline)",
    paddingTop: "var(--space-7)"
  },
  worksTitle: {
    fontFamily: "var(--font-serif)",
    fontWeight: 400,
    fontSize: "32px",
    letterSpacing: "-0.01em"
  },
  grid: {
    display: "grid",
    gridTemplateColumns: "repeat(3, 1fr)",
    gap: "28px",
    padding: "var(--space-6) var(--page-margin) var(--space-10)"
  }
};
function HomeScreen({
  go
}) {
  const {
    Button,
    Tag,
    Card,
    TextLink
  } = window.LastPlaceDesignSystem_2f29fe;
  const projects = window.LP_PROJECTS.slice(0, 3);
  return /*#__PURE__*/React.createElement("div", null, /*#__PURE__*/React.createElement("section", {
    style: homeStyles.hero
  }, /*#__PURE__*/React.createElement("div", null, /*#__PURE__*/React.createElement("div", {
    style: homeStyles.eyebrow
  }, "Web design studio \u2014 est. 2022"), /*#__PURE__*/React.createElement("h1", {
    style: homeStyles.h1
  }, "We are", /*#__PURE__*/React.createElement("br", null), "Last ", /*#__PURE__*/React.createElement("span", {
    style: homeStyles.blue
  }, "Place"), "."), /*#__PURE__*/React.createElement("p", {
    style: homeStyles.lede
  }, "A small studio that likes a lot of white space, a single confident blue, and websites that age well. We come last on purpose."), /*#__PURE__*/React.createElement("div", {
    style: homeStyles.ctaRow
  }, /*#__PURE__*/React.createElement(Button, {
    variant: "primary",
    onClick: () => go("contact")
  }, "Start a project"), /*#__PURE__*/React.createElement(Button, {
    variant: "link",
    onClick: () => go("work")
  }, "see selected work"))), /*#__PURE__*/React.createElement("div", {
    style: homeStyles.art
  }, /*#__PURE__*/React.createElement("img", {
    src: "../../assets/plant-mark-blue-knockout.png",
    alt: "Last Place plant mark",
    style: homeStyles.artImg
  }))), /*#__PURE__*/React.createElement("div", {
    style: homeStyles.worksHead
  }, /*#__PURE__*/React.createElement("span", {
    style: homeStyles.worksTitle
  }, "Selected works"), /*#__PURE__*/React.createElement(TextLink, {
    onClick: () => go("work"),
    arrow: true
  }, "The full index")), /*#__PURE__*/React.createElement("section", {
    style: homeStyles.grid
  }, projects.map(p => /*#__PURE__*/React.createElement(Card, {
    key: p.id,
    href: "#",
    onClick: e => {
      e.preventDefault();
      go("work");
    },
    eyebrow: p.tags.join(" · "),
    title: p.title,
    meta: `${p.year} — ${p.client}`,
    mediaBg: window.LP_WELL(p.well).background,
    media: /*#__PURE__*/React.createElement("div", {
      style: {
        ...window.LP_WELL(p.well),
        width: "100%",
        height: "100%",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        fontFamily: "var(--font-serif)",
        fontWeight: 300,
        fontSize: "72px"
      }
    }, p.initials)
  }, p.blurb))));
}
window.HomeScreen = HomeScreen;
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/studio-site/HomeScreen.jsx", error: String((e && e.message) || e) }); }

// ui_kits/studio-site/StudioScreen.jsx
try { (() => {
const studioStyles = {
  head: {
    padding: "var(--space-9) var(--page-margin) var(--space-7)",
    display: "grid",
    gridTemplateColumns: "1fr 0.7fr",
    gap: "48px",
    alignItems: "end"
  },
  eyebrow: {
    fontFamily: "var(--font-mono)",
    fontSize: "11.5px",
    letterSpacing: "0.2em",
    textTransform: "uppercase",
    color: "var(--text-muted)",
    marginBottom: "24px"
  },
  big: {
    fontFamily: "var(--font-serif)",
    fontWeight: 300,
    fontSize: "64px",
    lineHeight: 0.98,
    letterSpacing: "-0.02em",
    margin: 0,
    maxWidth: "16ch"
  },
  art: {
    display: "flex",
    justifyContent: "flex-end"
  },
  artImg: {
    width: "100%",
    maxWidth: "220px",
    filter: "none"
  },
  body: {
    padding: "var(--space-6) var(--page-margin) var(--space-8)",
    display: "grid",
    gridTemplateColumns: "1fr 1fr",
    gap: "48px"
  },
  p: {
    fontFamily: "var(--font-serif)",
    fontSize: "19px",
    lineHeight: 1.62,
    color: "var(--text-body)",
    margin: "0 0 22px",
    maxWidth: "52ch"
  },
  services: {
    borderTop: "1px solid var(--border-hairline)",
    padding: "var(--space-7) var(--page-margin) var(--space-10)"
  },
  sLabel: {
    fontFamily: "var(--font-mono)",
    fontSize: "11.5px",
    letterSpacing: "0.2em",
    textTransform: "uppercase",
    color: "var(--text-faint)",
    marginBottom: "28px"
  },
  sGrid: {
    display: "grid",
    gridTemplateColumns: "repeat(3, 1fr)",
    gap: "1px",
    background: "var(--border-hairline)",
    border: "1px solid var(--border-hairline)"
  },
  sCell: {
    background: "var(--surface-page)",
    padding: "28px 24px"
  },
  sNum: {
    fontFamily: "var(--font-mono)",
    fontSize: "12px",
    color: "var(--lp-blue)",
    marginBottom: "14px"
  },
  sName: {
    fontFamily: "var(--font-serif)",
    fontSize: "26px",
    marginBottom: "10px"
  },
  sDesc: {
    fontFamily: "var(--font-serif)",
    fontSize: "16px",
    lineHeight: 1.5,
    color: "var(--text-muted)"
  }
};
function StudioScreen() {
  const services = [["Brand identity", "Wordmarks, systems, and the small print that holds them together."], ["Websites", "Hand-built, fast, and quiet. Made to age well, not to trend."], ["Editorial", "Type-led layouts for publications, archives, and reading."], ["Art direction", "A point of view, applied consistently across everything."], ["Lino & print", "We still cut blocks by hand — it keeps the eye honest."], ["Care", "We answer emails, hit dates, and explain ourselves plainly."]];
  return /*#__PURE__*/React.createElement("div", null, /*#__PURE__*/React.createElement("header", {
    style: studioStyles.head
  }, /*#__PURE__*/React.createElement("div", null, /*#__PURE__*/React.createElement("div", {
    style: studioStyles.eyebrow
  }, "Studio \u2014 est. 2022"), /*#__PURE__*/React.createElement("h1", {
    style: studioStyles.big
  }, "A small studio, and proud to come last.")), /*#__PURE__*/React.createElement("div", {
    style: studioStyles.art
  }, /*#__PURE__*/React.createElement("img", {
    src: "../../assets/plant-mark-blue.png",
    alt: "Last Place plant mark",
    style: studioStyles.artImg
  }))), /*#__PURE__*/React.createElement("section", {
    style: studioStyles.body
  }, /*#__PURE__*/React.createElement("div", null, /*#__PURE__*/React.createElement("p", {
    style: studioStyles.p
  }, "Last Place is a two-person web design studio working with arts, culture and third-sector clients across the UK. We believe a website is mostly white space with a few good decisions inside it."), /*#__PURE__*/React.createElement("p", {
    style: studioStyles.p
  }, "We name ourselves after the finish line on purpose. Coming last means we are never in a hurry \u2014 we take the time to draw the thing properly, set the type by hand, and leave room to breathe.")), /*#__PURE__*/React.createElement("div", null, /*#__PURE__*/React.createElement("p", {
    style: studioStyles.p
  }, "Everything starts in blue. We cut lino blocks, print them, and let the rough edge of the press find its way into the digital work. The result is something hand-made and a little imperfect \u2014 which is the point."), /*#__PURE__*/React.createElement("p", {
    style: studioStyles.p
  }, "If your values match ours and you have a project that deserves care, we would love to hear about it."))), /*#__PURE__*/React.createElement("section", {
    style: studioStyles.services
  }, /*#__PURE__*/React.createElement("div", {
    style: studioStyles.sLabel
  }, "What we do"), /*#__PURE__*/React.createElement("div", {
    style: studioStyles.sGrid
  }, services.map(([name, desc], i) => /*#__PURE__*/React.createElement("div", {
    key: name,
    style: studioStyles.sCell
  }, /*#__PURE__*/React.createElement("div", {
    style: studioStyles.sNum
  }, String(i + 1).padStart(2, "0")), /*#__PURE__*/React.createElement("div", {
    style: studioStyles.sName
  }, name), /*#__PURE__*/React.createElement("div", {
    style: studioStyles.sDesc
  }, desc))))));
}
window.StudioScreen = StudioScreen;
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/studio-site/StudioScreen.jsx", error: String((e && e.message) || e) }); }

// ui_kits/studio-site/WorkScreen.jsx
try { (() => {
const workStyles = {
  head: {
    padding: "var(--space-9) var(--page-margin) var(--space-6)"
  },
  eyebrow: {
    fontFamily: "var(--font-mono)",
    fontSize: "11.5px",
    letterSpacing: "0.2em",
    textTransform: "uppercase",
    color: "var(--text-muted)",
    marginBottom: "20px"
  },
  h1: {
    fontFamily: "var(--font-serif)",
    fontWeight: 300,
    fontSize: "72px",
    lineHeight: 0.92,
    letterSpacing: "-0.02em",
    margin: "0 0 18px"
  },
  lede: {
    fontFamily: "var(--font-serif)",
    fontSize: "21px",
    lineHeight: 1.5,
    maxWidth: "46ch",
    color: "var(--text-muted)",
    margin: 0
  },
  list: {
    padding: "0 var(--page-margin) var(--space-10)"
  },
  row: {
    display: "grid",
    gridTemplateColumns: "64px 1fr auto 140px 40px",
    alignItems: "baseline",
    gap: "24px",
    padding: "26px 0",
    borderTop: "1px solid var(--border-hairline)",
    cursor: "pointer",
    textDecoration: "none",
    color: "var(--text-body)",
    transition: "padding-left var(--dur-base) var(--ease-out)"
  },
  num: {
    fontFamily: "var(--font-mono)",
    fontSize: "13px",
    color: "var(--text-faint)"
  },
  title: {
    fontFamily: "var(--font-serif)",
    fontSize: "40px",
    lineHeight: 1,
    letterSpacing: "-0.01em"
  },
  tags: {
    display: "flex",
    gap: "10px"
  },
  year: {
    fontFamily: "var(--font-mono)",
    fontSize: "13px",
    color: "var(--text-muted)",
    textAlign: "right"
  },
  arrow: {
    fontFamily: "var(--font-serif)",
    fontSize: "28px",
    color: "var(--lp-blue)",
    textAlign: "right"
  }
};
function WorkScreen({
  go
}) {
  const {
    Tag
  } = window.LastPlaceDesignSystem_2f29fe;
  const [hover, setHover] = React.useState(null);
  return /*#__PURE__*/React.createElement("div", null, /*#__PURE__*/React.createElement("header", {
    style: workStyles.head
  }, /*#__PURE__*/React.createElement("div", {
    style: workStyles.eyebrow
  }, "Index \u2014 selected works"), /*#__PURE__*/React.createElement("h1", {
    style: workStyles.h1
  }, "Things we have made."), /*#__PURE__*/React.createElement("p", {
    style: workStyles.lede
  }, "Identities and websites for arts, culture, and quietly ambitious businesses. A representative few \u2014 ask us for the rest.")), /*#__PURE__*/React.createElement("div", {
    style: workStyles.list
  }, window.LP_PROJECTS.map((p, i) => /*#__PURE__*/React.createElement("a", {
    key: p.id,
    href: "#",
    onClick: e => {
      e.preventDefault();
      go("contact");
    },
    onMouseEnter: () => setHover(p.id),
    onMouseLeave: () => setHover(null),
    style: {
      ...workStyles.row,
      paddingLeft: hover === p.id ? "16px" : "0",
      borderTopColor: hover === p.id ? "var(--lp-black)" : "var(--border-hairline)"
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: workStyles.num
  }, String(i + 1).padStart(2, "0")), /*#__PURE__*/React.createElement("span", {
    style: {
      ...workStyles.title,
      color: hover === p.id ? "var(--lp-blue)" : "var(--text-body)",
      transition: "color var(--dur-fast) var(--ease-out)"
    }
  }, p.title), /*#__PURE__*/React.createElement("span", {
    style: workStyles.tags
  }, p.tags.map(t => /*#__PURE__*/React.createElement(Tag, {
    key: t,
    tone: "muted"
  }, t))), /*#__PURE__*/React.createElement("span", {
    style: workStyles.year
  }, p.year, " \u2014 ", p.client), /*#__PURE__*/React.createElement("span", {
    style: {
      ...workStyles.arrow,
      opacity: hover === p.id ? 1 : 0.25,
      transition: "opacity var(--dur-fast) var(--ease-out)"
    }
  }, "\u21B3")))));
}
window.WorkScreen = WorkScreen;
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/studio-site/WorkScreen.jsx", error: String((e && e.message) || e) }); }

// ui_kits/studio-site/projects.js
try { (() => {
// Shared fake project data for the Last Place studio site.
window.LP_PROJECTS = [{
  id: "onwards",
  title: "Onwards Norfolk",
  tags: ["Branding", "Web"],
  year: "2025",
  client: "Norfolk BIDs",
  well: "blue",
  initials: "ON",
  blurb: "An events platform and identity for the Norfolk district."
}, {
  id: "marsh",
  title: "Marsh & Co.",
  tags: ["Identity"],
  year: "2025",
  client: "Marsh & Co.",
  well: "ink",
  initials: "M&",
  blurb: "A wordmark and stationery for a coastal architecture practice."
}, {
  id: "behrens",
  title: "Behrens Typography",
  tags: ["Web", "Editorial"],
  year: "2024",
  client: "HSD Düsseldorf",
  well: "paper",
  initials: "BT",
  blurb: "A teaching archive for a design-history workshop series."
}, {
  id: "field",
  title: "Field Recordings",
  tags: ["Web", "Sound"],
  year: "2024",
  client: "Independent",
  well: "blue",
  initials: "FR",
  blurb: "A quiet listening site for a location-sound label."
}, {
  id: "almanac",
  title: "The Slow Almanac",
  tags: ["Editorial"],
  year: "2023",
  client: "Almanac Press",
  well: "ink",
  initials: "SA",
  blurb: "An annual of essays, set entirely in one serif."
}, {
  id: "verge",
  title: "Verge Garden Co.",
  tags: ["Branding", "Web"],
  year: "2023",
  client: "Verge",
  well: "paper",
  initials: "VG",
  blurb: "Identity and shop for a wild-planting nursery."
}];
window.LP_WELL = function (kind) {
  if (kind === "ink") return {
    background: "var(--lp-black)",
    color: "#fff"
  };
  if (kind === "paper") return {
    background: "var(--lp-paper)",
    color: "var(--lp-blue)",
    border: "1px solid var(--border-hairline)"
  };
  return {
    background: "var(--lp-blue)",
    color: "#fff"
  };
};
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/studio-site/projects.js", error: String((e && e.message) || e) }); }

__ds_ns.Button = __ds_scope.Button;

__ds_ns.Card = __ds_scope.Card;

__ds_ns.Tag = __ds_scope.Tag;

__ds_ns.TextLink = __ds_scope.TextLink;

__ds_ns.Checkbox = __ds_scope.Checkbox;

__ds_ns.Field = __ds_scope.Field;

__ds_ns.Switch = __ds_scope.Switch;

})();
