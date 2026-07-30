import type { InputHTMLAttributes } from 'react';

export interface CheckboxProps extends InputHTMLAttributes<HTMLInputElement> {
  label: string;
  description?: string | null;
}
/** For booleans that take effect when the form is SAVED. See Switch. */
export declare function Checkbox(props: CheckboxProps): JSX.Element;
export declare const css: string;
