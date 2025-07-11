import { SignUp } from '@clerk/nextjs'

export default function Page() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-dealverse-navy via-dealverse-navy to-dealverse-dark-gray flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <div className="w-16 h-16 bg-gradient-to-br from-dealverse-blue to-dealverse-green rounded-lg flex items-center justify-center mx-auto mb-4">
            <span className="text-white font-bold text-xl">DV</span>
          </div>
          <h1 className="text-2xl font-bold text-white mb-2">Join DealVerse OS</h1>
          <p className="text-dealverse-light-gray">Create your account to get started</p>
        </div>
        <SignUp
          appearance={{
            elements: {
              formButtonPrimary: 'bg-dealverse-blue hover:bg-dealverse-blue/90',
              card: 'bg-dealverse-navy/50 border-dealverse-blue/20',
              headerTitle: 'text-white',
              headerSubtitle: 'text-dealverse-light-gray',
              socialButtonsBlockButton: 'border-dealverse-blue/20 text-white hover:bg-dealverse-blue/10',
              formFieldLabel: 'text-white',
              formFieldInput: 'bg-dealverse-dark-gray/50 border-dealverse-blue/20 text-white',
              footerActionLink: 'text-dealverse-blue hover:text-dealverse-blue/80'
            }
          }}
        />
      </div>
    </div>
  )
}