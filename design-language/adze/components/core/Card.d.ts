import type { ReactNode, ElementType } from 'react';

export interface CardProps {
  children?: ReactNode;
  title?: string | null;
  subtitle?: string | null;
  /** Top-right control, usually a ghost Button. */
  action?: ReactNode;
  padding?: 'none' | 'sm' | 'md' | 'lg';
  /** Only when the WHOLE card navigates. Never with nested controls. */
  interactive?: boolean;
  as?: ElementType;
}
export declare function Card(props: CardProps): JSX.Element;
export declare const css: string;
