import { useAnimatedValue } from '../hooks/useAnimatedValue'

interface Props {
  label: string
  value: number
  maxValue?: number
}

function getColor(val: number): string {
  if (val >= 70) return '#ef4444'
  if (val >= 35) return '#f59e0b'
  return '#22c55e'
}

function getLabel(val: number): string {
  if (val >= 70) return 'HIGH RISK'
  if (val >= 35) return 'MODERATE'
  return 'LOW RISK'
}

export default function RiskCard({ label, value }: Props) {
  const animated = useAnimatedValue(value, 300)
  const color = getColor(value)
  const riskLabel = getLabel(value)

  return (
    <div
      className="risk-card liquid-glass"
      style={{ borderTop: `2px solid ${color}30` }}
    >
      <div className="flex justify-between items-center mb-4">
        <span className="text-xs text-gray-400 uppercase tracking-widest">{label}</span>
        <span className="text-xs font-mono" style={{ color }}>{riskLabel}</span>
      </div>
      <div className="flex items-end gap-1 mb-4">
        <span className="text-4xl font-light text-white">{animated}</span>
        <span className="text-lg text-gray-600 mb-1">/100</span>
      </div>
      <div className="progress-bar">
        <div
          className="progress-fill"
          style={{ width: `${animated}%`, background: color }}
        />
      </div>
    </div>
  )
}
