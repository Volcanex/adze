export interface SpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  /** 'current' inherits colour from the parent — correct inside a Button. */
  tone?: 'current' | 'accent' | 'muted';
  /** Screen-reader label. Default "Loading". */
  label?: string;
  /** ms to stay invisible before appearing, to avoid a flash. Default 300. */
  delay?: number;
}
export declare function Spinner(props: SpinnerProps): JSX.Element;
export declare const css: string;
