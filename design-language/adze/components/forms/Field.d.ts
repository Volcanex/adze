import type { ReactNode } from 'react';

export interface FieldRenderProps {
  id: string;
  'aria-describedby'?: string;
  'aria-invalid'?: true;
  required: boolean;
}

export interface FieldProps {
  /** Render prop — spread the supplied props onto your control. */
  children: (props: FieldRenderProps) => ReactNode;
  label: string;
  help?: string | null;
  /** Non-empty string puts the field into its error state and announces it. */
  error?: string | null;
  required?: boolean;
  /** Right-aligned mono note, e.g. "optional" or "128/280". */
  hint?: string | null;
}
export declare function Field(props: FieldProps): JSX.Element;
export declare const css: string;
