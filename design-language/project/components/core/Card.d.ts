import * as React from "react";

/**
 * Last Place — Card
 * A restrained content surface with optional media, used for work / project tiles.
 *
 * @startingPoint section="Core" subtitle="Hairline project card with blue media well" viewport="380x420"
 */
export interface CardProps {
  /** Small mono eyebrow label above the title. */
  eyebrow?: React.ReactNode;
  /** Serif title. */
  title?: React.ReactNode;
  /** Mono metadata line at the foot (date, client, etc). */
  meta?: React.ReactNode;
  /** Image src, or any node, shown in the media well. */
  media?: string | React.ReactNode;
  /** Background of the media well (defaults to brand blue). */
  mediaBg?: string;
  /** Make the whole card a link. */
  href?: string;
  /** Body / description copy. */
  children?: React.ReactNode;
}

export function Card(props: CardProps): JSX.Element;
