import type { InputHTMLAttributes } from 'react';

export interface SwitchProps extends InputHTMLAttributes<HTMLInputElement> {
  label: string;
  description?: string | null;
  /** Write in flight — pulses the track and locks the control. */
  pending?: boolean;
}
/** For booleans that take effect IMMEDIATELY. See Checkbox. */
export declare function Switch(props: SwitchProps): JSX.Element;
export declare const css: string;
