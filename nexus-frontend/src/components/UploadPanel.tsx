import { useState, useEffect, useCallback } from 'react'
import { BACKEND } from '../constants'
import type { ChecklistItem } from '../types'

interface Props {
  applicationId: string
  requiredDocs: string[]
  onSubmit: (appId: string) => void
  onBack: () => void
}

export default function UploadPanel({ applicationId, requiredDocs: _requiredDocs, onSubmit, onBack }: Props) {
  const [checklist, setChecklist] = useState<ChecklistItem[]>([])
  const [uploading, setUploading] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  const fetchChecklist = useCallback(async () => {
    try {
      const res = await fetch(BACKEND + '/application-documents/' + applicationId)
      if (!res.ok) return
      const data: ChecklistItem[] = await res.json()
      setChecklist(data)
    } catch {}
    setLoading(false)
  }, [applicationId])

  useEffect(() => { fetchChecklist() }, [fetchChecklist])

  const uploadFile = async (docType: string, file: File) => {
    setUploading(docType)
    const fd = new FormData()
    fd.append('application_id', applicationId)
    fd.append('document_type', docType)
    fd.append('file', file)
    try {
      const res = await fetch(BACKEND + '/upload-document', { method: 'POST', body: fd })
      if (!res.ok) throw new Error('Upload failed')
      await fetchChecklist()
    } catch (e) {
      alert('Upload error: ' + (e as Error).message)
    }
    setUploading(null)
  }

  const required = checklist.filter(c => c.required)
  const verified = required.filter(c => c.upload_status === 'Verified' || c.upload_status === 'Uploaded')
  const progress = required.length ? Math.round((verified.length / required.length) * 100) : 0
  const canSubmit = verified.length > 0

  return (
    <div className="min-h-screen bg-black px-6 py-24">
      <div className="max-w-2xl mx-auto">
        <div className="mb-8">
          <button onClick={onBack} className="text-sm text-gray-400 hover:text-white mb-4 flex items-center gap-2 transition-colors">
            ← Back
          </button>
          <h2 className="text-3xl font-light text-white mb-2">Document Upload</h2>
          <p className="text-gray-400 text-sm">Step 2 of 4 — Upload required documents</p>
        </div>

        {/* Progress */}
        <div className="liquid-glass rounded-2xl p-6 mb-6">
          <div className="flex justify-between items-center mb-3">
            <span className="text-sm text-gray-300">Upload Progress</span>
            <span className="text-sm font-medium text-white">{verified.length}/{required.length} documents</span>
          </div>
          <div className="progress-bar">
            <div className="progress-fill bg-white" style={{ width: `${progress}%` }} />
          </div>
          <div className="mt-2 text-xs text-gray-500">{progress}% complete</div>
        </div>

        {loading ? (
          <div className="text-center py-12 text-gray-400">Loading checklist…</div>
        ) : (
          <div className="flex flex-col gap-3">
            {checklist.map(doc => {
              const isVerified = doc.upload_status === 'Verified' || doc.upload_status === 'Uploaded'
              const isActive = uploading === doc.document_type
              return (
                <div key={doc.document_type} className="liquid-glass rounded-xl p-4 flex items-center justify-between gap-4">
                  <div className="flex items-center gap-3 flex-1 min-w-0">
                    <div className={`w-2 h-2 rounded-full flex-shrink-0 ${isVerified ? 'bg-green-400' : 'bg-white/20'}`} />
                    <div className="min-w-0">
                      <div className="text-sm text-white truncate">{doc.document_type}</div>
                      {doc.required && <div className="text-xs text-gray-500">Required</div>}
                    </div>
                  </div>
                  <div className="flex items-center gap-3 flex-shrink-0">
                    {isVerified ? (
                      <span className="badge bg-green-400/15 text-green-400 border border-green-400/30">✓ Verified</span>
                    ) : (
                      <label className="cursor-pointer">
                        <input
                          type="file"
                          accept=".pdf,.png,.jpg,.jpeg"
                          className="hidden"
                          disabled={!!uploading}
                          onChange={e => e.target.files?.[0] && uploadFile(doc.document_type, e.target.files[0])}
                        />
                        <span className={`btn-glass text-xs px-4 py-2 liquid-glass ${isActive ? 'opacity-50' : ''}`}>
                          {isActive ? 'Uploading…' : 'Upload'}
                        </span>
                      </label>
                    )}
                  </div>
                </div>
              )
            })}
          </div>
        )}

        <div className="mt-8 flex justify-end">
          <button
            onClick={() => onSubmit(applicationId)}
            disabled={!canSubmit}
            className="btn-white px-10 py-3 disabled:opacity-40"
          >
            Run Analysis →
          </button>
        </div>
      </div>
    </div>
  )
}
