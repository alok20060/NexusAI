import type { ApiResult, FormData } from '../types'
import RiskCard from './RiskCard'

interface Props {
  data: ApiResult
  form: FormData
  elapsed: number
  onReset: () => void
  isDemo: boolean
}

export default function ResultsDashboard({ data, form, elapsed, onReset, isDemo }: Props) {
  const fr = data.final_response || {}
  const decision = fr.final_recommendation || ''
  const isApproved = /approve/i.test(decision)
  const isRejected = /reject/i.test(decision)
  const decColor = isApproved ? '#22c55e' : isRejected ? '#ef4444' : '#f59e0b'

  const fraudVal = fr.fraud_score !== undefined
    ? Math.round(fr.fraud_score)
    : (fr.fraud_risk === 'High' ? 85 : fr.fraud_risk === 'Moderate' || fr.fraud_risk === 'Medium' ? 45 : 12)

  const businessVal = Math.round(fr.risk_score || 0)

  const creditVal = fr.repayment_risk === 'High' ? 82 :
    (fr.repayment_risk === 'Moderate' || fr.repayment_risk === 'Medium') ? 50 : 15

  const conf = Math.round((fr.confidence || 0) * 100)

  const reasons: string[] = []
  if (fr.explainability_report) {
    fr.explainability_report.split('\n').forEach(line => {
      const t = line.replace(/^[-•]\s*/, '').trim()
      if (t) reasons.push(t)
    })
  } else if (fr.key_reasons) {
    reasons.push(...fr.key_reasons)
  } else if (fr.decision_explanation) {
    reasons.push(fr.decision_explanation)
  }

  const a3 = data.agent_3_output || {}

  return (
    <div className="min-h-screen bg-black px-6 py-24">
      <div className="max-w-5xl mx-auto">
        {/* Header */}
        <div className="flex items-start justify-between mb-10">
          <div>
            <h2 className="text-3xl font-light text-white mb-1">Risk Assessment Complete</h2>
            <p className="text-gray-400 text-sm">{form.biz} · {(elapsed/1000).toFixed(1)}s · Ref: {fr.reference_id || '—'}</p>
          </div>
          <button onClick={onReset} className="btn-glass liquid-glass text-sm px-5 py-2">
            ← New Application
          </button>
        </div>

        {/* Decision Banner */}
        <div className="liquid-glass rounded-2xl p-6 mb-6 flex items-center justify-between"
          style={{ borderLeft: `4px solid ${decColor}` }}>
          <div>
            <div className="text-xs text-gray-500 uppercase tracking-widest mb-1">Final Decision</div>
            <div className="text-2xl font-semibold" style={{ color: decColor }}>
              {isApproved ? 'APPROVED ✓' : isRejected ? 'REJECTED ✕' : 'MANUAL REVIEW ◈'}
            </div>
          </div>
          <div className="text-right">
            <div className="text-xs text-gray-500 uppercase tracking-widest mb-1">Confidence</div>
            <div className="text-2xl font-light text-white">{conf}%</div>
          </div>
        </div>

        {/* Risk Grid */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          <RiskCard label="Fraud Risk" value={fraudVal} />
          <RiskCard label="Business Risk" value={businessVal} />
          <RiskCard label="Credit Risk" value={creditVal} />
          <div className="risk-card liquid-glass flex flex-col items-center justify-center text-center">
            <div className="text-xs text-gray-400 uppercase tracking-widest mb-3">Trust Score</div>
            <div className="text-4xl font-light text-white mb-1">{fr.trust_score ?? '—'}</div>
            <div className="text-xs text-gray-500">/100</div>
          </div>
        </div>

        {/* Business Info + Fraud */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
          <div className="liquid-glass rounded-2xl p-6">
            <div className="text-xs text-gray-500 uppercase tracking-widest mb-4">Business Summary</div>
            {[
              ['Business', form.biz],
              ['Owner', form.owner],
              ['Loan Amount', '$' + Number(form.amount).toLocaleString()],
              ['Monthly Revenue', '$' + Number(form.revenue).toLocaleString()],
              ['Industry', form.industry || '—'],
            ].map(([l, v]) => (
              <div key={l} className="flex justify-between py-2 border-b border-white/5 last:border-0">
                <span className="text-xs text-gray-500">{l}</span>
                <span className="text-sm text-white">{v}</span>
              </div>
            ))}
          </div>

          <div className="liquid-glass rounded-2xl p-6">
            <div className="text-xs text-gray-500 uppercase tracking-widest mb-4">Fraud Detection</div>
            <div className="flex items-center justify-between py-2 border-b border-white/5">
              <span className="text-xs text-gray-500">Fraud Risk Level</span>
              <span className={`text-sm font-medium ${
                fr.fraud_risk === 'High' ? 'text-red-400' :
                fr.fraud_risk === 'Low' ? 'text-green-400' : 'text-yellow-400'
              }`}>{fr.fraud_risk || '—'}</span>
            </div>
            <div className="flex items-center justify-between py-2 border-b border-white/5">
              <span className="text-xs text-gray-500">DB Match</span>
              <span className={`text-sm ${a3.fraud_match ? 'text-red-400' : 'text-green-400'}`}>
                {a3.fraud_match ? 'MATCH FOUND' : 'CLEAR'}
              </span>
            </div>
            <div className="flex items-center justify-between py-2">
              <span className="text-xs text-gray-500">Repayment Risk</span>
              <span className="text-sm text-white">{fr.repayment_risk || '—'}</span>
            </div>
            {a3.fraud_records_found && a3.fraud_records_found > 0 && (
              <div className="mt-3 p-3 rounded-lg bg-red-500/10 border border-red-500/20">
                <div className="text-xs text-red-400 font-medium mb-1">Fraud Signals Detected</div>
                {(a3.fraud_signals || []).filter(s => s !== 'None').map((s, i) => (
                  <div key={i} className="text-xs text-gray-400">{s}</div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Reasoning */}
        {reasons.length > 0 && (
          <div className="liquid-glass rounded-2xl p-6 mb-6">
            <div className="text-xs text-gray-500 uppercase tracking-widest mb-4">AI Reasoning</div>
            {reasons.slice(0, 8).map((r, i) => (
              <div key={i} className="finding-row">
                <div className="w-1.5 h-1.5 rounded-full mt-2 flex-shrink-0" style={{ background: decColor }} />
                <span className="text-sm text-gray-300 leading-relaxed">{r}</span>
              </div>
            ))}
          </div>
        )}

        {/* Agent Timeline */}
        {fr.timeline && fr.timeline.length > 0 && (
          <div className="liquid-glass rounded-2xl p-6 mb-6">
            <div className="text-xs text-gray-500 uppercase tracking-widest mb-4">Agent Pipeline Execution</div>
            <div className="flex flex-col gap-3">
              {fr.timeline.map((t, i) => (
                <div key={i} className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className={`w-2 h-2 rounded-full ${
                      t.status === 'Completed' ? 'bg-white' :
                      t.status === 'In Progress' ? 'bg-yellow-400' : 'bg-white/15'
                    }`} />
                    <span className={`text-sm ${
                      t.status === 'Completed' ? 'text-white' : 'text-gray-500'
                    }`}>{t.stage}</span>
                  </div>
                  <span className="text-xs text-gray-600 font-mono">
                    {t.timestamp ? new Date(t.timestamp).toLocaleTimeString() : '—'}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Reasoning Trace (non-demo) */}
        {!isDemo && fr.reasoning_trace && fr.reasoning_trace.length > 0 && (
          <div className="liquid-glass rounded-2xl p-6 mb-6">
            <div className="text-xs text-gray-500 uppercase tracking-widest mb-4">Reasoning Trace</div>
            {fr.reasoning_trace.map((t, i) => (
              <div key={i} className="finding-row">
                <span className="badge text-xs px-2 py-0.5 flex-shrink-0" style={{
                  background: 'rgba(255,255,255,0.06)',
                  color: 'rgba(255,255,255,0.5)',
                  border: '1px solid rgba(255,255,255,0.1)'
                }}>{t.agent}</span>
                <span className="text-xs text-gray-400 leading-relaxed">{t.text}</span>
              </div>
            ))}
          </div>
        )}

        {/* Audit log */}
        {fr.audit_log && fr.audit_log.length > 0 && (
          <div className="liquid-glass rounded-2xl p-6">
            <div className="text-xs text-gray-500 uppercase tracking-widest mb-4">Audit Log</div>
            <div className="max-h-48 overflow-y-auto flex flex-col gap-2">
              {fr.audit_log.map((l, i) => (
                <div key={i} className="flex gap-3 text-xs">
                  <span className="text-gray-600 font-mono flex-shrink-0">{l.timestamp}</span>
                  <span className="text-gray-400">{l.message}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
