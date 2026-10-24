import React from "react";

export interface CornerBoxProps {
  children?: React.ReactNode;
  /** Whether the effect is only visible on group-hover (defaults to false) */
  hoverOnly?: boolean;
  /** Optional dimension tag to show underneath (e.g. "51 x 15") */
  dimension?: string;
  /** Border color of the bounding box */
  borderColor?: string;
  /** Border color of the 4 corner square handles */
  cornerBorderColor?: string;
  /** Background fill color of the 4 corner square handles */
  cornerBgColor?: string;
  /** Additional classes on the border overlay */
  className?: string;
  /** Additional classes on the wrapper when children are passed */
  wrapperClassName?: string;
}

export default function CornerBox({
  children,
  hoverOnly = false,
  dimension,
  borderColor = "border-neutral-400/80",
  cornerBorderColor = "border-[#171717]",
  cornerBgColor = "bg-[#f6f4ef]",
  className = "",
  wrapperClassName = "",
}: CornerBoxProps) {
  const borderOverlay = (
    <span
      aria-hidden="true"
      className={`pointer-events-none absolute inset-0 border ${borderColor} ${
        hoverOnly
          ? "opacity-0 transition-opacity duration-150 group-hover:opacity-100"
          : "opacity-100"
      } ${className}`}
    >
      {/* Four corner rectangle handles */}
      <span
        className={`absolute -top-[3px] -left-[3px] h-[5px] w-[5px] border ${cornerBorderColor} ${cornerBgColor}`}
      />
      <span
        className={`absolute -top-[3px] -right-[3px] h-[5px] w-[5px] border ${cornerBorderColor} ${cornerBgColor}`}
      />
      <span
        className={`absolute -bottom-[3px] -left-[3px] h-[5px] w-[5px] border ${cornerBorderColor} ${cornerBgColor}`}
      />
      <span
        className={`absolute -bottom-[3px] -right-[3px] h-[5px] w-[5px] border ${cornerBorderColor} ${cornerBgColor}`}
      />

      {/* Dimension tag underneath */}
      {dimension && (
        <span className="absolute left-0 -bottom-[18px] whitespace-nowrap rounded-[2px] bg-[#171717] px-1 py-[1.5px] font-mono text-[8px] sm:text-[9px] font-normal leading-none tracking-normal text-[#f6f4ef] shadow-sm">
          {dimension}
        </span>
      )}
    </span>
  );

  if (children !== undefined) {
    return (
      <span
        className={`relative inline-flex items-center justify-center ${wrapperClassName}`}
      >
        {children}
        {borderOverlay}
      </span>
    );
  }

  return borderOverlay;
}
