"use client";

import * as React from "react";
import { cn } from "@/lib/utils";

export interface TextareaProps
  extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {}

const Textarea = React.forwardRef<HTMLTextAreaElement, TextareaProps>(
  ({ className, ...props }, ref) => {
    return (
      <textarea
        className={cn(
          "flex min-h-[120px] w-full rounded-input border border-border bg-bg-base px-4 py-3 text-body-m text-text-primary placeholder:text-text-muted transition-colors resize-y",
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
Textarea.displayName = "Textarea";

export { Textarea };
