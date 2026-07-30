export interface ProgressBarProps {
  /** 0–100. Pass null/undefined for indeterminate (sweeping band). */
  value?: number | null;
  /** Mono uppercase label above the track. */
  label?: string | null;
  /** Secondary right-aligned text, e.g. "3 of 12". */
  detail?: string | null;
  size?: 'sm' | 'md';
  tone?: 'accent' | 'success' | 'danger';
  /** Render the % readout when determinate. Default true. */
  showValue?: boolean;
}
export declare function ProgressBar(props: ProgressBarProps): JSX.Element;
export declare const css: string;
