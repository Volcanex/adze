import * as React from "react";

/**
 * Last Place — TextLink
 * The signature hyperlink-blue inline link.
 */
export interface TextLinkProps {
  href?: string;
  /** Prefix with the brand's ↳ arrow affordance. */
  arrow?: boolean;
  /** Render in ink instead of blue (for links inside already-blue contexts). */
  muted?: boolean;
  children?: React.ReactNode;
}

export function TextLink(props: TextLinkProps): JSX.Element;
