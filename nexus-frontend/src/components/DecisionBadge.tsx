
interface Props {
  decision: string
}

export default function DecisionBadge({ decision }: Props) {
  const isApproved = /approve/i.test(decision)
  const isRejected = /reject/i.test(decision)

  const color = isApproved ? '#22c55e' : isRejected ? '#ef4444' : '#f59e0b'
  const label = isApproved ? 'APPROVED ✓' : isRejected ? 'REJECTED ✕' : 'MANUAL REVIEW ◈'

  return (
    <div
      className="rounded-2xl p-6 flex flex-col items-center justify-center text-center"
      style={{
        background: `${color}10`,
        border: `1px solid ${color}30`,
        boxShadow: `0 0 40px ${color}20`,
      }}
    >
      <div className="text-xs text-gray-400 uppercase tracking-widest mb-3">Final Decision</div>
      <div className="text-3xl font-semibold" style={{ color }}>{label}</div>
    </div>
  )
}
