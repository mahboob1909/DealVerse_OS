export default function TestPage() {
  return (
    <div className="min-h-screen bg-dealverse-navy p-8">
      <h1 className="text-h1 font-bold mb-4 text-white">Tailwind CSS Test</h1>
      <div className="space-y-4">
        <div className="bg-dealverse-blue text-white p-4 rounded-lg">
          Blue Background Test
        </div>
        <div className="bg-dealverse-green text-white p-4 rounded-lg">
          Green Background Test
        </div>
        <div className="bg-dealverse-light-gray text-dealverse-navy p-4 rounded-lg">
          Light Gray Background Test
        </div>
        <div className="text-h2 text-dealverse-blue">
          Typography Test - H2
        </div>
        <div className="text-body text-dealverse-medium-gray">
          Typography Test - Body
        </div>
        <div className="grid grid-cols-3 gap-unit-2">
          <div className="bg-dealverse-amber p-unit-2 rounded">Spacing Test 1</div>
          <div className="bg-dealverse-coral p-unit-3 rounded">Spacing Test 2</div>
          <div className="bg-dealverse-dark-gray p-unit-4 rounded text-white">Spacing Test 3</div>
        </div>
        <div className="mt-8">
          <a
            href="/"
            className="bg-dealverse-blue text-white px-8 py-4 rounded-lg font-bold text-xl hover:bg-dealverse-blue/90"
          >
            Go Back to Home
          </a>
        </div>
      </div>
    </div>
  )
}
