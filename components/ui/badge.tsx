import * as React from "react"
import { cva, type VariantProps } from "class-variance-authority"

import { cn } from "@/lib/utils"

const badgeVariants = cva(
  "inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2",
  {
    variants: {
      variant: {
        default:
          "border-transparent bg-primary text-primary-foreground hover:bg-primary/80",
        secondary:
          "border-transparent bg-secondary text-secondary-foreground hover:bg-secondary/80",
        destructive:
          "border-transparent bg-destructive text-destructive-foreground hover:bg-destructive/80",
        outline: "text-foreground",
        // DealVerse OS Status Badges
        success:
          "border-transparent bg-dealverse-green text-white hover:bg-dealverse-green/80",
        warning:
          "border-transparent bg-dealverse-amber text-white hover:bg-dealverse-amber/80",
        error:
          "border-transparent bg-dealverse-coral text-white hover:bg-dealverse-coral/80",
        info:
          "border-transparent bg-dealverse-blue text-white hover:bg-dealverse-blue/80",
        // Deal Status Badges
        "deal-active":
          "border-dealverse-green/20 bg-dealverse-green/10 text-dealverse-green hover:bg-dealverse-green/20",
        "deal-pending":
          "border-dealverse-amber/20 bg-dealverse-amber/10 text-dealverse-amber hover:bg-dealverse-amber/20",
        "deal-closed":
          "border-dealverse-navy/20 bg-dealverse-navy/10 text-dealverse-navy hover:bg-dealverse-navy/20",
        "deal-cancelled":
          "border-dealverse-coral/20 bg-dealverse-coral/10 text-dealverse-coral hover:bg-dealverse-coral/20",
        // Risk Level Badges
        "risk-low":
          "border-dealverse-green/20 bg-dealverse-green/10 text-dealverse-green",
        "risk-medium":
          "border-dealverse-amber/20 bg-dealverse-amber/10 text-dealverse-amber",
        "risk-high":
          "border-dealverse-coral/20 bg-dealverse-coral/10 text-dealverse-coral",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  }
)

export interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {}

function Badge({ className, variant, ...props }: BadgeProps) {
  return (
    <div className={cn(badgeVariants({ variant }), className)} {...props} />
  )
}

export { Badge, badgeVariants }
