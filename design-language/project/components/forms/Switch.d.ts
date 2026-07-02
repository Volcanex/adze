import * as React from "react";

/**
 * Last Place — Switch
 * Flat, square-cornered toggle; track fills blue when on.
 */
export interface SwitchProps {
  checked?: boolean;
  onChange?: (next: boolean) => void;
  label?: React.ReactNode;
  disabled?: boolean;
}

export function Switch(props: SwitchProps): JSX.Element;
