import * as React from "react"
import { cn } from "../../lib/utils"

const Progress = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement> & {
    value?: number
    max?: number
  }
>(({ className, value = 0, max = 100, ...props }, ref) => (
  <div
    ref={ref}
    role="progressbar"
    aria-valuemin={0}
    aria-valuenow={value}
    aria-valuemax={max}
    className={cn(
      "relative h-2 w-full overflow-hidden rounded-full bg-primary/20",
      className
    )}
    {...props}
  >
    <div
      className="h-full rounded-full bg-primary transition-all duration-300 ease-in-out"
      style={{ width: `${Math.min((value / max) * 100, 100)}%` }}
    />
  </div>
))
Progress.displayName = "Progress"

export { Progress }
