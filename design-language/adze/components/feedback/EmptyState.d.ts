import type { ReactNode } from 'react';

export interface EmptyStateProps {
  /** Phosphor icon name without the `ph-` prefix, e.g. 'images'. */
  icon?: string | null;
  /** What isn't here, phrased plainly. Required. */
  title: string;
  /** One sentence on what this section is for. */
  body?: string | null;
  /** The button that resolves the empty state. Strongly recommended. */
  action?: ReactNode;
  variant?: 'empty' | 'error';
}
export declare function EmptyState(props: EmptyStateProps): JSX.Element;
export declare const css: string;
