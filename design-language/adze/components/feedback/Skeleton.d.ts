export interface SkeletonProps {
  variant?: 'text' | 'title' | 'block' | 'circle' | 'thumb';
  /** CSS length. Defaults per variant. */
  width?: string | null;
  height?: string | null;
  /** Only meaningful for variant="text". Last line renders short. */
  lines?: number;
}
export declare function Skeleton(props: SkeletonProps): JSX.Element;

export interface SkeletonRowsProps {
  /** Number of placeholder rows. Default 4. */
  count?: number;
}
/** Pre-composed loading state matching the content-admin list row geometry. */
export declare function SkeletonRows(props: SkeletonRowsProps): JSX.Element;
export declare const css: string;
