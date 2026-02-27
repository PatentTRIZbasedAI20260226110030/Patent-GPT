"use client";

import * as React from "react";
import { cn } from "@/lib/utils";

export interface SelectProps
  extends React.SelectHTMLAttributes<HTMLSelectElement> {}

const Select = React.forwardRef<HTMLSelectElement, SelectProps>(
  ({ className, children, ...props }, ref) => {
    return (
      <select
        className={cn(
          "flex h-11 w-full rounded-input border border-border bg-bg-surface px-4 py-3 text-body-m text-text-primary transition-colors cursor-pointer",
          "focus:outline-none focus:border-border-active focus:ring-2 focus:ring-primary-glow",
          "disabled:cursor-not-allowed disabled:opacity-50",
          "aria-[invalid=true]:border-error",
          className
        )}
        ref={ref}
        {...props}
      >
        {children}
      </select>
    );
  }
);
Select.displayName = "Select";

export { Select };
