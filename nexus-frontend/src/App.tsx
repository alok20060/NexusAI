import { useState } from 'react'
import Navbar from './components/Navbar'
import HeroSection from './components/HeroSection'
import ApplicationForm from './components/ApplicationForm'
import UploadPanel from './components/UploadPanel'
import PipelineView from './components/PipelineView'
import ResultsDashboard from './components/ResultsDashboard'
import { BACKEND, DEMO_CASES } from './constants'
import type { Screen, FormData, ApiResult } from './types'

export default function App() {
  const [screen, setScreen] = useState<Screen>('home')
  const [formData, setFormData] = useState<FormData>({ biz:'', owner:'', amount:'', revenue:'', years:'5', industry:'', purpose:'' })
  const [applicationId, setApplicationId] = useState('')
  const [requiredDocs, setRequiredDocs] = useState<string[]>([])
  const [pipelineStage, setPipelineStage] = useState(0)
  const [apiData, setApiData] = useState<ApiResult | null>(null)
  const [elapsed, setElapsed] = useState(0)

  const handleFormNext = (form: FormData, appId: string, docs: string[]) => {
    setFormData(form)
    setApplicationId(appId)
    setRequiredDocs(docs)
    setScreen('upload')
  }

  const handleSubmitAnalysis = async (appId: string) => {
    setScreen('pipeline')
    setPipelineStage(0)
    const t0 = Date.now()

    // Animate stages
    const runAgents = async () => {
      for (let i = 0; i < 7; i++) {
        setPipelineStage(i)
        await new Promise(r => setTimeout(r, 650))
      }
    }
    runAgents()

    try {
      const res = await fetch(BACKEND + '/analyze-loan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          business_name: formData.biz,
          owner_name: formData.owner,
          loan_amount: +formData.amount,
          monthly_revenue: +formData.revenue || 0,
          years_in_business: +formData.years || 5,
          industry: formData.industry || 'General Trade',
          loan_purpose: formData.purpose || 'Working capital',
          application_id: appId
        })
      })
      if (!res.ok) throw new Error('API error ' + res.status)
      const data: ApiResult = await res.json()
      setPipelineStage(7)
      await new Promise(r => setTimeout(r, 600))
      setApiData(data)
      setElapsed(Date.now() - t0)
      setScreen('results')
    } catch (e) {
      alert('Analysis failed: ' + (e as Error).message)
      setScreen('upload')
    }
  }

  const handleReset = () => {
    setScreen('home')
    setApiData(null)
    setPipelineStage(0)
    setElapsed(0)
    setApplicationId('')
    setRequiredDocs([])
  }

  const isDemo = DEMO_CASES.some(d => d.name === formData.biz)

  return (
    <div className="bg-black min-h-screen text-white">
      <Navbar onLaunch={() => setScreen('form')} />

      {screen === 'home' && (
        <HeroSection onStart={() => setScreen('form')} />
      )}
      {screen === 'form' && (
        <ApplicationForm onNext={handleFormNext} />
      )}
      {screen === 'upload' && (
        <UploadPanel
          applicationId={applicationId}
          requiredDocs={requiredDocs}
          onSubmit={handleSubmitAnalysis}
          onBack={() => setScreen('form')}
        />
      )}
      {screen === 'pipeline' && (
        <PipelineView stage={pipelineStage} />
      )}
      {screen === 'results' && apiData && (
        <ResultsDashboard
          data={apiData}
          form={formData}
          elapsed={elapsed}
          onReset={handleReset}
          isDemo={isDemo}
        />
      )}
    </div>
  )
}
