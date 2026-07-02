import * as React from "react";

/**
 * Last Place — Checkbox
 * Square checkbox with serif label; blue fill when checked.
 */
export interface CheckboxProps {
  checked?: boolean;
  onChange?: (next: boolean) => void;
  label?: React.ReactNode;
  disabled?: boolean;
}

export function Checkbox(props: CheckboxProps): JSX.Element;
