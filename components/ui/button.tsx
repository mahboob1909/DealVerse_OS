import * as React from "react"
import { Slot } from "@radix-ui/react-slot"
import { cva, type VariantProps } from "class-variance-authority"

import { cn } from "@/lib/utils"

const buttonVariants = cva(
  "inline-flex items-center justify-center whitespace-nowrap rounded-lg text-sm font-medium ring-offset-background transition-all duration-300 ease-in-out focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-dealverse-blue focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 active:scale-95",
  {
    variants: {
      variant: {
        default: "bg-dealverse-blue text-white hover:bg-dealverse-blue/90 hover:shadow-lg hover:shadow-dealverse-blue/25 hover:scale-105",
        destructive:
          "bg-dealverse-coral text-white hover:bg-dealverse-coral/90 hover:shadow-lg hover:shadow-dealverse-coral/25",
        outline:
          "border-2 border-dealverse-blue bg-transparent text-dealverse-blue hover:bg-dealverse-blue hover:text-white hover:shadow-lg",
        secondary:
          "bg-dealverse-navy text-white hover:bg-dealverse-navy/90 hover:shadow-lg",
        ghost: "hover:bg-dealverse-blue/10 hover:text-dealverse-blue",
        link: "text-dealverse-blue underline-offset-4 hover:underline hover:text-dealverse-blue/80",
        success: "bg-dealverse-green text-white hover:bg-dealverse-green/90 hover:shadow-lg hover:shadow-dealverse-green/25",
        warning: "bg-dealverse-amber text-white hover:bg-dealverse-amber/90 hover:shadow-lg hover:shadow-dealverse-amber/25",
      },
      size: {
        default: "h-10 px-4 py-2",
        sm: "h-9 rounded-lg px-3",
        lg: "h-12 rounded-lg px-8 text-base",
        icon: "h-10 w-10",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
)

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, asChild = false, ...props }, ref) => {
    const Comp = asChild ? Slot : "button"
    return (
      <Comp
        className={cn(buttonVariants({ variant, size, className }))}
        ref={ref}
        {...props}
      />
    )
  }
)
Button.displayName = "Button"

export { Button, buttonVariants }
