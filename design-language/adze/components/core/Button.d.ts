import type { ReactNode, ButtonHTMLAttributes } from 'react';

export interface ButtonProps extends Omit<ButtonHTMLAttributes<HTMLButtonElement>, 'type'> {
  children?: ReactNode;
  /** Encodes importance, not colour. Max one `primary` per view. */
  variant?: 'primary' | 'secondary' | 'ghost' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  /** Phosphor icon name without the `ph-` prefix. */
  icon?: string | null;
  iconTrailing?: string | null;
  /** Shows a spinner AND disables the button — prevents double-submit. */
  loading?: boolean;
  disabled?: boolean;
  fullWidth?: boolean;
  type?: 'button' | 'submit' | 'reset';
}
export declare function Button(props: ButtonProps): JSX.Element;
export declare const css: string;
