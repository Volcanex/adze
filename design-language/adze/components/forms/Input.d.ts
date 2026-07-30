import type { InputHTMLAttributes } from 'react';

export interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  /** Renders a <textarea> instead. */
  multiline?: boolean;
  size?: 'sm' | 'md' | 'lg';
  /** Static text inside the control, e.g. "https://". */
  prefix?: string | null;
  /** Phosphor icon name without the `ph-` prefix. */
  icon?: string | null;
}
export declare function Input(props: InputProps): JSX.Element;
export declare const css: string;
