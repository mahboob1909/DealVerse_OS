"use client"

import { useState } from 'react'
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { CheckCircle, Loader2 } from "lucide-react"
import { SignInButton, SignUpButton, SignedIn, SignedOut, useUser } from '@clerk/nextjs'
import { openCheckout, FASTSPRING_PRODUCTS, formatPrice } from "@/lib/fastspring"
import Link from "next/link"

interface PricingCardProps {
  planKey: keyof typeof FASTSPRING_PRODUCTS
  title: string
  description: string
  price: number
  period: string
  features: string[]
  isPopular?: boolean
  isEnterprise?: boolean
  className?: string
}

export function PricingCard({
  planKey,
  title,
  description,
  price,
  period,
  features,
  isPopular = false,
  isEnterprise = false,
  className = ""
}: PricingCardProps) {
  const [isLoading, setIsLoading] = useState(false)
  const { user } = useUser()

  const handlePurchase = async () => {
    if (isEnterprise) {
      // Handle enterprise contact sales
      window.location.href = 'mailto:sales@dealverse.com?subject=Enterprise Plan Inquiry'
      return
    }

    try {
      setIsLoading(true)
      await openCheckout(planKey, user?.primaryEmailAddress?.emailAddress)
    } catch (error) {
      console.error('Failed to open checkout:', error)
      // You could show an error toast here
    } finally {
      setIsLoading(false)
    }
  }

  const borderClass = isPopular 
    ? "border-dealverse-green/40 hover:border-dealverse-green/60" 
    : "border-dealverse-blue/20 hover:border-dealverse-blue/40"

  const buttonClass = isPopular
    ? "bg-dealverse-green hover:bg-dealverse-green/90"
    : "bg-dealverse-blue hover:bg-dealverse-blue/90"

  return (
    <Card className={`bg-dealverse-navy/50 ${borderClass} transition-all duration-300 relative ${isPopular ? 'transform scale-105' : ''} ${className}`}>
      {isPopular && (
        <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
          <div className="bg-dealverse-green text-white px-4 py-1 rounded-full text-sm font-medium">
            Most Popular
          </div>
        </div>
      )}
      
      <CardHeader className={`text-center pb-8 ${isPopular ? 'pt-8' : ''}`}>
        <CardTitle className="text-2xl text-white mb-2">{title}</CardTitle>
        <CardDescription className="text-dealverse-light-gray mb-4">
          {description}
        </CardDescription>
        
        <div className="text-4xl font-bold text-white">
          {isEnterprise ? (
            "Custom"
          ) : (
            <>
              {formatPrice(price)}
              <span className="text-lg text-dealverse-light-gray font-normal">/{period}</span>
            </>
          )}
        </div>
        
        {!isEnterprise && (
          <div className="text-sm text-dealverse-light-gray">
            {period === 'month' ? 'per seat' : 'per seat, billed annually'}
          </div>
        )}
        
        {planKey === 'professional-annual' && (
          <div className="text-sm text-dealverse-green font-medium">Save $60 per year</div>
        )}
        
        {isEnterprise && (
          <div className="text-sm text-dealverse-light-gray">Contact for pricing</div>
        )}
      </CardHeader>
      
      <CardContent>
        <ul className="space-y-3 text-dealverse-light-gray mb-8">
          {features.map((feature, index) => (
            <li key={index} className="flex items-center">
              <CheckCircle className="h-5 w-5 text-dealverse-green mr-3 flex-shrink-0" />
              <span>{feature}</span>
            </li>
          ))}
        </ul>
        
        <SignedOut>
          {isEnterprise ? (
            <Button 
              variant="outline" 
              className="w-full border-dealverse-blue text-dealverse-blue hover:bg-dealverse-blue/10"
              onClick={handlePurchase}
              disabled={isLoading}
            >
              {isLoading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Contacting...
                </>
              ) : (
                "Contact Sales"
              )}
            </Button>
          ) : (
            <SignUpButton mode="modal">
              <Button 
                className={`w-full ${buttonClass} text-white`}
                disabled={isLoading}
              >
                {isLoading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Loading...
                  </>
                ) : (
                  "Get Started"
                )}
              </Button>
            </SignUpButton>
          )}
        </SignedOut>
        
        <SignedIn>
          {isEnterprise ? (
            <Button 
              variant="outline" 
              className="w-full border-dealverse-blue text-dealverse-blue hover:bg-dealverse-blue/10"
              onClick={handlePurchase}
              disabled={isLoading}
            >
              {isLoading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Contacting...
                </>
              ) : (
                "Contact Sales"
              )}
            </Button>
          ) : (
            <Button 
              className={`w-full ${buttonClass} text-white`}
              onClick={handlePurchase}
              disabled={isLoading}
            >
              {isLoading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Processing...
                </>
              ) : (
                "Subscribe Now"
              )}
            </Button>
          )}
        </SignedIn>
      </CardContent>
    </Card>
  )
}
