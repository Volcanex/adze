import * as React from "react";

/**
 * Last Place — Field
 * Editorial underline text input (or textarea).
 *
 * @startingPoint section="Forms" subtitle="Underline-style input with mono label" viewport="420x120"
 */
export interface FieldProps {
  /** Mono uppercase label above the field. */
  label?: React.ReactNode;
  /** Quiet helper line below. */
  hint?: React.ReactNode;
  /** Error message; turns the rule and hint to forest green. */
  error?: React.ReactNode;
  type?: string;
  /** Render a multi-line textarea. */
  multiline?: boolean;
  value?: string;
  onChange?: (e: React.ChangeEvent) => void;
  placeholder?: string;
  id?: string;
}

export function Field(props: FieldProps): JSX.Element;
