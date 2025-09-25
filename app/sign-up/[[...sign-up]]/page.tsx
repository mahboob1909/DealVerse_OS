// Required for static export
export async function generateStaticParams() {
  return [{ 'sign-up': [] }]
}

export default function Page() {
  // Temporarily show placeholder for static export
  return (
    <div className="min-h-screen bg-gradient-to-br from-dealverse-navy via-dealverse-navy to-dealverse-dark-gray flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <div className="w-16 h-16 bg-gradient-to-br from-dealverse-blue to-dealverse-green rounded-lg flex items-center justify-center mx-auto mb-4">
            <span className="text-white font-bold text-xl">DV</span>
          </div>
          <h1 className="text-2xl font-bold text-white mb-2">Join DealVerse OS</h1>
          <p className="text-dealverse-light-gray">Authentication will be available after deployment</p>
        </div>
        <div className="bg-dealverse-navy/50 border border-dealverse-blue/20 rounded-lg p-8 text-center">
          <p className="text-white mb-4">Sign up functionality will be enabled in production</p>
          <a href="/" className="text-dealverse-blue hover:text-dealverse-blue/80">← Back to Home</a>
        </div>
      </div>
    </div>
  )
}