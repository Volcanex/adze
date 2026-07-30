import type { ReactNode, AnchorHTMLAttributes } from 'react';

export interface TextLinkProps extends AnchorHTMLAttributes<HTMLAnchorElement> {
  children?: ReactNode;
  href: string;
  /** `inline` is always underlined. Only use `standalone` when position
   *  already signals interactivity. */
  variant?: 'inline' | 'standalone' | 'quiet';
  /** Adds target/rel, a trailing arrow, and screen-reader warning text. */
  external?: boolean;
  icon?: string | null;
}
export declare function TextLink(props: TextLinkProps): JSX.Element;
export declare const css: string;
