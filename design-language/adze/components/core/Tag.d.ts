import type { ReactNode } from 'react';

export interface TagProps {
  children?: ReactNode;
  /** Status tones are not artist-overridable — meaning must stay constant. */
  tone?: 'neutral' | 'accent' | 'success' | 'warn' | 'danger';
  dot?: boolean;
  size?: 'sm' | 'md';
}
export declare function Tag(props: TagProps): JSX.Element;
export declare const css: string;
