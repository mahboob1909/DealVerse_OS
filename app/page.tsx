import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import {
  DynamicSignInButton,
  DynamicSignUpButton,
  DynamicSignedIn,
  DynamicSignedOut,
  DynamicUserButton
} from '@/components/dynamic-auth'
// Temporarily disabled for static export
// import { PricingCard } from "@/components/pricing-card"
import {
  Search,
  FileText,
  Calculator,
  Shield,
  Presentation,
  BarChart4,
  TrendingUp,
  Users,
  CheckCircle,
  ArrowRight,
  Brain,
  Target,
  Zap,
  Star,
  Mail,
  Phone,
  MapPin
} from "lucide-react"

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-dealverse-navy via-dealverse-navy to-dealverse-dark-gray relative overflow-hidden">
      {/* Animated Background */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-dealverse-blue/10 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-dealverse-green/10 rounded-full blur-3xl animate-pulse delay-1000"></div>
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-dealverse-blue/5 rounded-full blur-3xl animate-pulse delay-500"></div>
      </div>

      {/* Navigation */}
      <nav className="relative z-10 border-b border-dealverse-navy/20 bg-dealverse-navy/95 backdrop-blur-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-gradient-to-br from-dealverse-blue to-dealverse-green rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-sm">DV</span>
              </div>
              <h1 className="font-bold text-xl text-white">DealVerse OS</h1>
            </div>
            <div className="flex items-center space-x-4">
              <DynamicSignedOut>
                <DynamicSignInButton>
                  <Button variant="ghost" className="text-white hover:bg-dealverse-blue/10">
                    Sign In
                  </Button>
                </DynamicSignInButton>
                <DynamicSignUpButton>
                  <Button className="bg-dealverse-blue hover:bg-dealverse-blue/90 text-white">
                    Get Started
                    <ArrowRight className="ml-2 h-4 w-4" />
                  </Button>
                </DynamicSignUpButton>
              </DynamicSignedOut>
              <DynamicSignedIn>
                <DynamicUserButton />
              </DynamicSignedIn>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative z-10 py-24 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center">
            <div className="mb-8 animate-fade-in">
              <div className="inline-flex items-center px-4 py-2 bg-dealverse-blue/10 border border-dealverse-blue/20 rounded-full text-dealverse-blue text-sm font-medium mb-6">
                <Zap className="w-4 h-4 mr-2" />
                AI-Powered Investment Banking Platform
              </div>
            </div>
            <h1 className="text-5xl md:text-7xl font-bold text-white mb-8 leading-tight animate-fade-in-up">
              The Future of
              <span className="bg-gradient-to-r from-dealverse-blue via-dealverse-green to-dealverse-blue bg-clip-text text-transparent block animate-gradient">
                Investment Banking
              </span>
            </h1>
            <p className="text-xl md:text-2xl text-dealverse-light-gray mb-12 max-w-4xl mx-auto leading-relaxed animate-fade-in-up delay-200">
              DealVerse OS revolutionizes investment banking with AI-powered deal sourcing,
              automated due diligence, advanced valuation modeling, and comprehensive compliance management.
            </p>
            <div className="flex flex-col sm:flex-row gap-6 justify-center animate-fade-in-up delay-400">
              <DynamicSignedOut>
                <DynamicSignUpButton>
                  <Button size="lg" className="bg-dealverse-blue hover:bg-dealverse-blue/90 text-white px-10 py-6 text-lg font-semibold shadow-lg hover:shadow-xl transition-all duration-300 transform hover:scale-105">
                    Start Free Trial
                    <ArrowRight className="ml-2 h-5 w-5" />
                  </Button>
                </DynamicSignUpButton>
              </DynamicSignedOut>
              <DynamicSignedIn>
                <Link href="/dashboard">
                  <Button size="lg" className="bg-dealverse-blue hover:bg-dealverse-blue/90 text-white px-10 py-6 text-lg font-semibold shadow-lg hover:shadow-xl transition-all duration-300 transform hover:scale-105">
                    Go to Dashboard
                    <ArrowRight className="ml-2 h-5 w-5" />
                  </Button>
                </Link>
              </DynamicSignedIn>
              <Button size="lg" variant="outline" className="border-2 border-dealverse-blue text-dealverse-blue hover:bg-dealverse-blue/10 px-10 py-6 text-lg font-semibold backdrop-blur-sm transition-all duration-300 transform hover:scale-105">
                Watch Demo
              </Button>
            </div>

            {/* Stats Section */}
            <div className="mt-20 grid grid-cols-1 md:grid-cols-3 gap-8 animate-fade-in-up delay-600">
              <div className="text-center">
                <div className="text-3xl md:text-4xl font-bold text-white mb-2">500+</div>
                <div className="text-dealverse-light-gray">Deals Processed</div>
              </div>
              <div className="text-center">
                <div className="text-3xl md:text-4xl font-bold text-white mb-2">$2.5B+</div>
                <div className="text-dealverse-light-gray">Transaction Value</div>
              </div>
              <div className="text-center">
                <div className="text-3xl md:text-4xl font-bold text-white mb-2">98%</div>
                <div className="text-dealverse-light-gray">Client Satisfaction</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Core Modules Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 bg-dealverse-dark-gray/30">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
              Five Integrated Modules
            </h2>
            <p className="text-xl text-dealverse-light-gray max-w-2xl mx-auto">
              Everything you need for modern investment banking, powered by artificial intelligence
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {/* Prospect AI */}
            <Card className="bg-dealverse-navy/50 border-dealverse-blue/20 hover:border-dealverse-blue/40 transition-all duration-300 group">
              <CardHeader>
                <div className="w-12 h-12 bg-gradient-to-br from-dealverse-blue/20 to-dealverse-blue/30 rounded-lg flex items-center justify-center mb-4 group-hover:scale-110 transition-transform duration-300">
                  <Search className="h-6 w-6 text-dealverse-blue" />
                </div>
                <CardTitle className="text-xl text-white">Prospect AI</CardTitle>
                <CardDescription className="text-dealverse-light-gray">
                  AI-powered deal sourcing and opportunity management with market intelligence
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2 text-sm text-dealverse-light-gray">
                  <li className="flex items-center">
                    <CheckCircle className="h-4 w-4 text-dealverse-green mr-2" />
                    Automated prospect identification
                  </li>
                  <li className="flex items-center">
                    <CheckCircle className="h-4 w-4 text-dealverse-green mr-2" />
                    AI confidence scoring
                  </li>
                  <li className="flex items-center">
                    <CheckCircle className="h-4 w-4 text-dealverse-green mr-2" />
                    Market trend analysis
                  </li>
                </ul>
              </CardContent>
            </Card>

            {/* Diligence Navigator */}
            <Card className="bg-dealverse-navy/50 border-dealverse-blue/20 hover:border-dealverse-blue/40 transition-all duration-300 group">
              <CardHeader>
                <div className="w-12 h-12 bg-gradient-to-br from-dealverse-blue/20 to-dealverse-blue/30 rounded-lg flex items-center justify-center mb-4 group-hover:scale-110 transition-transform duration-300">
                  <FileText className="h-6 w-6 text-dealverse-blue" />
                </div>
                <CardTitle className="text-xl text-white">Diligence Navigator</CardTitle>
                <CardDescription className="text-dealverse-light-gray">
                  Streamlined due diligence with automated document analysis and risk assessment
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2 text-sm text-dealverse-light-gray">
                  <li className="flex items-center">
                    <CheckCircle className="h-4 w-4 text-dealverse-green mr-2" />
                    Document tree organization
                  </li>
                  <li className="flex items-center">
                    <CheckCircle className="h-4 w-4 text-dealverse-green mr-2" />
                    AI risk flagging
                  </li>
                  <li className="flex items-center">
                    <CheckCircle className="h-4 w-4 text-dealverse-green mr-2" />
                    Missing document alerts
                  </li>
                </ul>
              </CardContent>
            </Card>

            {/* Valuation & Modeling Hub */}
            <Card className="bg-dealverse-navy/50 border-dealverse-blue/20 hover:border-dealverse-blue/40 transition-all duration-300 group">
              <CardHeader>
                <div className="w-12 h-12 bg-gradient-to-br from-dealverse-blue/20 to-dealverse-blue/30 rounded-lg flex items-center justify-center mb-4 group-hover:scale-110 transition-transform duration-300">
                  <Calculator className="h-6 w-6 text-dealverse-blue" />
                </div>
                <CardTitle className="text-xl text-white">Valuation & Modeling Hub</CardTitle>
                <CardDescription className="text-dealverse-light-gray">
                  Advanced financial modeling with collaborative features and scenario analysis
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2 text-sm text-dealverse-light-gray">
                  <li className="flex items-center">
                    <CheckCircle className="h-4 w-4 text-dealverse-green mr-2" />
                    Collaborative modeling
                  </li>
                  <li className="flex items-center">
                    <CheckCircle className="h-4 w-4 text-dealverse-green mr-2" />
                    Scenario comparison
                  </li>
                  <li className="flex items-center">
                    <CheckCircle className="h-4 w-4 text-dealverse-green mr-2" />
                    Automated visualizations
                  </li>
                </ul>
              </CardContent>
            </Card>

            {/* Compliance Guardian */}
            <Card className="bg-dealverse-navy/50 border-dealverse-blue/20 hover:border-dealverse-blue/40 transition-all duration-300 group">
              <CardHeader>
                <div className="w-12 h-12 bg-gradient-to-br from-dealverse-blue/20 to-dealverse-blue/30 rounded-lg flex items-center justify-center mb-4 group-hover:scale-110 transition-transform duration-300">
                  <Shield className="h-6 w-6 text-dealverse-blue" />
                </div>
                <CardTitle className="text-xl text-white">Compliance Guardian</CardTitle>
                <CardDescription className="text-dealverse-light-gray">
                  Comprehensive compliance management with automated monitoring and reporting
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2 text-sm text-dealverse-light-gray">
                  <li className="flex items-center">
                    <CheckCircle className="h-4 w-4 text-dealverse-green mr-2" />
                    Traffic light system
                  </li>
                  <li className="flex items-center">
                    <CheckCircle className="h-4 w-4 text-dealverse-green mr-2" />
                    Audit trail timeline
                  </li>
                  <li className="flex items-center">
                    <CheckCircle className="h-4 w-4 text-dealverse-green mr-2" />
                    Regulatory updates
                  </li>
                </ul>
              </CardContent>
            </Card>

            {/* PitchCraft Suite */}
            <Card className="bg-dealverse-navy/50 border-dealverse-blue/20 hover:border-dealverse-blue/40 transition-all duration-300 group md:col-span-2 lg:col-span-1">
              <CardHeader>
                <div className="w-12 h-12 bg-gradient-to-br from-dealverse-blue/20 to-dealverse-blue/30 rounded-lg flex items-center justify-center mb-4 group-hover:scale-110 transition-transform duration-300">
                  <Presentation className="h-6 w-6 text-dealverse-blue" />
                </div>
                <CardTitle className="text-xl text-white">PitchCraft Suite</CardTitle>
                <CardDescription className="text-dealverse-light-gray">
                  Professional presentation builder with templates and real-time collaboration
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2 text-sm text-dealverse-light-gray">
                  <li className="flex items-center">
                    <CheckCircle className="h-4 w-4 text-dealverse-green mr-2" />
                    Drag-and-drop builder
                  </li>
                  <li className="flex items-center">
                    <CheckCircle className="h-4 w-4 text-dealverse-green mr-2" />
                    Template gallery
                  </li>
                  <li className="flex items-center">
                    <CheckCircle className="h-4 w-4 text-dealverse-green mr-2" />
                    Real-time collaboration
                  </li>
                </ul>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section className="relative z-10 py-20 px-4 sm:px-6 lg:px-8 bg-dealverse-dark-gray/50">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
              Simple, Transparent Pricing
            </h2>
            <p className="text-xl text-dealverse-light-gray max-w-2xl mx-auto">
              Choose the plan that fits your investment banking needs
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
            {/* Temporarily disabled for static export */}
            <div className="text-center text-white col-span-3">
              <p>Pricing cards will be available after deployment</p>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="relative z-10 bg-dealverse-navy border-t border-dealverse-navy/20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            {/* Company Info */}
            <div className="col-span-1 md:col-span-2">
              <div className="flex items-center space-x-3 mb-4">
                <div className="w-10 h-10 bg-gradient-to-br from-dealverse-blue to-dealverse-green rounded-lg flex items-center justify-center">
                  <span className="text-white font-bold text-lg">DV</span>
                </div>
                <h3 className="font-bold text-xl text-white">DealVerse OS</h3>
              </div>
              <p className="text-dealverse-light-gray mb-6 max-w-md">
                Revolutionizing investment banking with AI-powered tools for deal sourcing,
                due diligence, valuation modeling, and compliance management.
              </p>
              <div className="flex space-x-4">
                {/* Temporarily disabled for static export */}
                <Button className="bg-dealverse-blue hover:bg-dealverse-blue/90 text-white">
                  Start Free Trial
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Button>
              </div>
            </div>

            {/* Quick Links */}
            <div>
              <h4 className="font-semibold text-white mb-4">Product</h4>
              <ul className="space-y-2 text-dealverse-light-gray">
                <li><Link href="#features" className="hover:text-dealverse-blue transition-colors">Features</Link></li>
                <li><Link href="#pricing" className="hover:text-dealverse-blue transition-colors">Pricing</Link></li>
                <li><Link href="/dashboard" className="hover:text-dealverse-blue transition-colors">Dashboard</Link></li>
                <li><Link href="#demo" className="hover:text-dealverse-blue transition-colors">Demo</Link></li>
              </ul>
            </div>

            {/* Company Links */}
            <div>
              <h4 className="font-semibold text-white mb-4">Company</h4>
              <ul className="space-y-2 text-dealverse-light-gray">
                <li><Link href="/about" className="hover:text-dealverse-blue transition-colors">About</Link></li>
                <li><Link href="/contact" className="hover:text-dealverse-blue transition-colors">Contact</Link></li>
                <li><Link href="/terms" className="hover:text-dealverse-blue transition-colors">Terms of Service</Link></li>
                <li><Link href="/privacy" className="hover:text-dealverse-blue transition-colors">Privacy Policy</Link></li>
              </ul>
            </div>
          </div>

          {/* Contact Info */}
          <div className="border-t border-dealverse-navy/20 mt-8 pt-8">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
              <div className="flex items-center space-x-3 text-dealverse-light-gray">
                <Mail className="h-5 w-5 text-dealverse-blue" />
                <span>contact@dealverse.com</span>
              </div>
              <div className="flex items-center space-x-3 text-dealverse-light-gray">
                <Phone className="h-5 w-5 text-dealverse-blue" />
                <span>+1 (555) 123-4567</span>
              </div>
              <div className="flex items-center space-x-3 text-dealverse-light-gray">
                <MapPin className="h-5 w-5 text-dealverse-blue" />
                <span>New York, NY</span>
              </div>
            </div>

            {/* Bottom Bar */}
            <div className="flex flex-col md:flex-row justify-between items-center pt-8 border-t border-dealverse-navy/20">
              <p className="text-dealverse-light-gray text-sm">
                © 2024 DealVerse OS. All rights reserved.
              </p>
              <div className="flex items-center space-x-6 mt-4 md:mt-0">
                <div className="flex items-center space-x-2 text-dealverse-light-gray text-sm">
                  <Star className="h-4 w-4 text-dealverse-green" />
                  <span>Trusted by 500+ investment professionals</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
}
