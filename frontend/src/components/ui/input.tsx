"use client";

import * as React from "react";
import { cn } from "@/lib/utils";

export interface InputProps
  extends React.InputHTMLAttributes<HTMLInputElement> {}

const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ className, type, ...props }, ref) => {
    return (
      <input
        type={type}
        className={cn(
          "flex h-11 w-full rounded-input border border-border bg-bg-base px-4 py-3 text-body-m text-text-primary placeholder:text-text-muted transition-colors",
          "focus:outline-none focus:border-border-active focus:ring-2 focus:ring-primary-glow",
          "disabled:cursor-not-allowed disabled:opacity-50",
          "aria-[invalid=true]:border-error",
          className
        )}
        ref={ref}
        {...props}
      />
    );
  }
);
Input.displayName = "Input";

export { Input };
