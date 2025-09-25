import './globals.css'
import type { Metadata } from 'next'
import { Inter, JetBrains_Mono } from 'next/font/google'
import { ThemeProvider } from "@/components/theme-provider"
import { AuthWrapper } from '@/components/auth-wrapper'
// Temporarily disabled for static export
// import { AuthProvider } from '@/lib/auth-context'

const inter = Inter({
  subsets: ['latin'],
  display: 'swap',
  variable: '--font-inter',
})

const jetbrainsMono = JetBrains_Mono({
  subsets: ['latin'],
  display: 'swap',
  variable: '--font-jetbrains-mono',
})

export const metadata: Metadata = {
  title: 'DealVerse OS - Investment Banking Platform',
  description: 'AI-powered investment banking platform with deal sourcing, due diligence, valuation modeling, compliance management, and presentation tools.',
  keywords: 'investment banking, deal sourcing, due diligence, valuation, compliance, AI',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <AuthWrapper>
      <html lang="en" suppressHydrationWarning>
        <body className={`${inter.className} ${inter.variable} ${jetbrainsMono.variable} font-sans antialiased`}>
          <ThemeProvider
            defaultTheme="light"
            enableSystem
            disableTransitionOnChange
          >
            {/* Temporarily disabled for static export */}
            {children}
          </ThemeProvider>
        </body>
      </html>
    </AuthWrapper>
  )
}