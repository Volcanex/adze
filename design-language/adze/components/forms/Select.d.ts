import type { SelectHTMLAttributes } from 'react';

export type SelectOption = string | { value: string; label: string };

export interface SelectProps extends SelectHTMLAttributes<HTMLSelectElement> {
  options?: SelectOption[];
  /** Rendered as a leading empty-value option. */
  placeholder?: string | null;
  size?: 'sm' | 'md' | 'lg';
}
export declare function Select(props: SelectProps): JSX.Element;
export declare const css: string;
