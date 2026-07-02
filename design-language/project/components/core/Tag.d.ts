import * as React from "react";

/**
 * Last Place — Tag
 * Monospace, tracked, uppercase label or chip.
 */
export interface TagProps {
  /** Colour tone. */
  tone?: "ink" | "blue" | "green" | "muted";
  /** Draw a 1px box around it (otherwise bare text). */
  outline?: boolean;
  children?: React.ReactNode;
}

export function Tag(props: TagProps): JSX.Element;
