import { useEffect, useState } from 'react'

const AGENTS = [
  { name: 'Intake & Risk Coordinator', tag: 'INTAKE' },
  { name: 'Document Verification', tag: 'DOC-VERIFY' },
  { name: 'Fraud Intelligence', tag: 'FRAUD-INTEL' },
  { name: 'Business Validation', tag: 'BIZ-VALID' },
  { name: 'Risk Scoring', tag: 'RISK-SCORE' },
  { name: 'Explainability Engine', tag: 'EXPLAINER' },
  { name: 'Trust & Compliance', tag: 'COMPLIANCE' },
]

interface Props {
  stage: number
}

export default function PipelineView({ stage }: Props) {
  const [elapsed, setElapsed] = useState(0)
  useEffect(() => {
    const t = setInterval(() => setElapsed(s => s + 1), 1000)
    return () => clearInterval(t)
  }, [])

  return (
    <div className="min-h-screen bg-black flex items-center justify-center px-6 py-24">
      <div className="w-full max-w-lg">
        <div className="text-center mb-10">
          <div className="text-xs text-gray-500 uppercase tracking-widest mb-2">NexusAI Multi-Agent Orchestration</div>
          <h2 className="text-2xl font-light text-white">Running Analysis</h2>
          <p className="text-gray-400 text-sm mt-1">{elapsed}s elapsed</p>
        </div>

        <div className="liquid-glass rounded-2xl p-8">
          {AGENTS.map((agent, i) => {
            const done = i < stage
            const active = i === stage
            const pending = i > stage
            return (
              <div key={agent.tag} className="flex items-center gap-4 mb-6 last:mb-0">
                {/* Status dot */}
                <div className="relative flex-shrink-0">
                  <div className={`w-3 h-3 rounded-full transition-all duration-500 ${
                    done ? 'bg-white' : active ? 'bg-white animate-pulse' : 'bg-white/15'
                  }`} />
                </div>
                <div className="flex-1">
                  <div className={`text-sm transition-colors duration-300 ${
                    done || active ? 'text-white' : 'text-gray-600'
                  }`}>
                    {agent.name}
                  </div>
                  <div className="text-xs text-gray-600 font-mono">{agent.tag}</div>
                </div>
                <div className="text-xs flex-shrink-0">
                  {done && <span className="text-white/60">Complete</span>}
                  {active && <span className="text-white animate-pulse">Running…</span>}
                  {pending && <span className="text-white/20">Queued</span>}
                </div>
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}
