import * as React from "react";

/**
 * Last Place — Button
 *
 * @startingPoint section="Core" subtitle="Square editorial buttons — blue, outline, ghost, link" viewport="700x160"
 */
export interface ButtonProps {
  /** Visual style. `primary` = blue fill (one per view), `secondary` = inked outline, `ghost` = bare, `green` = rare forest accent, `link` = inline serif hyperlink. */
  variant?: "primary" | "secondary" | "ghost" | "green" | "link";
  /** Size of the control. */
  size?: "sm" | "md" | "lg";
  /** Render as an anchor with this href instead of a button. */
  href?: string;
  /** Native button type when not a link. */
  type?: "button" | "submit" | "reset";
  /** Disable interaction and dim the control. */
  disabled?: boolean;
  /** Stretch to fill the container width. */
  block?: boolean;
  onClick?: (e: React.MouseEvent) => void;
  children?: React.ReactNode;
}

export function Button(props: ButtonProps): JSX.Element;
