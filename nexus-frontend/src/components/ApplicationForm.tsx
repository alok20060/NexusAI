import { useState, type ChangeEvent } from 'react'
import { DEMO_CASES, INDUSTRIES, BACKEND } from '../constants'
import type { FormData } from '../types'

interface Props {
  onNext: (formData: FormData, appId: string, requiredDocs: string[]) => void
}

export default function ApplicationForm({ onNext }: Props) {
  const [form, setForm] = useState<FormData>({ biz:'', owner:'', amount:'', revenue:'', years:'5', industry:'', purpose:'' })
  const [errors, setErrors] = useState<Record<string, string>>({})
  const [loading, setLoading] = useState(false)
  const [showDemos, setShowDemos] = useState(false)

  const upd = (k: keyof FormData) => (e: ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) =>
    setForm(f => ({ ...f, [k]: e.target.value }))

  const loadDemo = (i: number) => {
    const c = DEMO_CASES[i]
    setForm({ biz: c.name, owner: c.owner, amount: String(c.amount), revenue: String(c.revenue), years: String(c.years), industry: c.industry, purpose: c.purpose })
    setErrors({})
  }

  const validate = () => {
    const e: Record<string, string> = {}
    if (!form.biz.trim()) e.biz = 'Required'
    if (!form.owner.trim()) e.owner = 'Required'
    if (!form.amount || isNaN(+form.amount) || +form.amount < 1000) e.amount = 'Min 1,000'
    if (!form.years || isNaN(+form.years)) e.years = 'Required'
    setErrors(e)
    return Object.keys(e).length === 0
  }

  const submit = async () => {
    if (!validate()) return
    setLoading(true)
    try {
      const res = await fetch(BACKEND + '/initialize-application', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          business_name: form.biz,
          owner_name: form.owner,
          loan_amount: +form.amount,
          monthly_revenue: +form.revenue || 0,
          years_in_business: +form.years || 5,
          industry: form.industry || 'General Trade',
          loan_purpose: form.purpose || 'Working capital'
        })
      })
      if (!res.ok) throw new Error('Init failed ' + res.status)
      const data = await res.json()
      onNext(form, data.application_id, data.required_documents)
    } catch (err) {
      alert('Initialization failed: ' + (err as Error).message)
    } finally {
      setLoading(false)
    }
  }

  const fmt = (n: string) => n ? '$' + Number(n).toLocaleString() : ''

  return (
    <div className="min-h-screen bg-black flex items-center justify-center px-6 py-24">
      <div className="w-full max-w-2xl">
        <div className="mb-10">
          <h2 className="text-3xl font-light text-white mb-2">New Application</h2>
          <p className="text-gray-400 text-sm">Step 1 of 4 — Business & Loan Details</p>
        </div>

        {/* Demo cases */}
        <div className="mb-8">
          <button
            onClick={() => setShowDemos(s => !s)}
            className="text-sm text-gray-400 hover:text-white transition-colors flex items-center gap-2"
          >
            <span className="text-xs">◈</span>
            {showDemos ? 'Hide demo cases' : 'Load a hackathon demo case'}
          </button>
          {showDemos && (
            <div className="mt-4 grid grid-cols-1 md:grid-cols-3 gap-3">
              {DEMO_CASES.map((c, i) => (
                <button
                  key={c.id}
                  onClick={() => loadDemo(i)}
                  className="liquid-glass rounded-xl p-4 text-left hover:bg-white/10 transition-all"
                >
                  <div className="text-sm font-medium text-white mb-1">{c.label}</div>
                  <div className="text-xs text-gray-400">{c.name}</div>
                  <div className="text-xs text-gray-500 mt-1">{c.note}</div>
                </button>
              ))}
            </div>
          )}
        </div>

        <div className="liquid-glass rounded-2xl p-8 flex flex-col gap-5">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            <div>
              <label className="block text-xs text-gray-400 mb-2 uppercase tracking-wider">Business Name *</label>
              <input className={`input-glass ${errors.biz ? 'border-red-500/50' : ''}`} value={form.biz} onChange={upd('biz')} placeholder="ABC Trading Co." />
              {errors.biz && <p className="text-red-400 text-xs mt-1">{errors.biz}</p>}
            </div>
            <div>
              <label className="block text-xs text-gray-400 mb-2 uppercase tracking-wider">Owner Name *</label>
              <input className={`input-glass ${errors.owner ? 'border-red-500/50' : ''}`} value={form.owner} onChange={upd('owner')} placeholder="Jane Smith" />
              {errors.owner && <p className="text-red-400 text-xs mt-1">{errors.owner}</p>}
            </div>
            <div>
              <label className="block text-xs text-gray-400 mb-2 uppercase tracking-wider">Loan Amount *</label>
              <input className={`input-glass ${errors.amount ? 'border-red-500/50' : ''}`} type="number" value={form.amount} onChange={upd('amount')} placeholder="500000" />
              {form.amount && <p className="text-xs text-gray-500 mt-1">{fmt(form.amount)}</p>}
              {errors.amount && <p className="text-red-400 text-xs mt-1">{errors.amount}</p>}
            </div>
            <div>
              <label className="block text-xs text-gray-400 mb-2 uppercase tracking-wider">Monthly Revenue</label>
              <input className="input-glass" type="number" value={form.revenue} onChange={upd('revenue')} placeholder="100000" />
              {form.revenue && <p className="text-xs text-gray-500 mt-1">{fmt(form.revenue)}/mo</p>}
            </div>
            <div>
              <label className="block text-xs text-gray-400 mb-2 uppercase tracking-wider">Years in Business *</label>
              <input className={`input-glass ${errors.years ? 'border-red-500/50' : ''}`} type="number" min="0" value={form.years} onChange={upd('years')} placeholder="5" />
              {errors.years && <p className="text-red-400 text-xs mt-1">{errors.years}</p>}
            </div>
            <div>
              <label className="block text-xs text-gray-400 mb-2 uppercase tracking-wider">Industry</label>
              <select className="input-glass" value={form.industry} onChange={upd('industry')}>
                <option value="">Select industry…</option>
                {INDUSTRIES.map(ind => <option key={ind} value={ind}>{ind}</option>)}
              </select>
            </div>
          </div>
          <div>
            <label className="block text-xs text-gray-400 mb-2 uppercase tracking-wider">Loan Purpose</label>
            <textarea className="input-glass resize-none" rows={2} value={form.purpose} onChange={upd('purpose')} placeholder="Working capital, expansion, equipment…" />
          </div>

          <div className="flex justify-end pt-2">
            <button onClick={submit} disabled={loading} className="btn-white px-10 py-3">
              {loading ? 'Initializing…' : 'Continue →'}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
