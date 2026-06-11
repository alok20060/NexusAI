export type Screen = 'home' | 'form' | 'upload' | 'pipeline' | 'results'

export interface DemoCase {
  id: string
  label: string
  name: string
  owner: string
  amount: number
  revenue: number
  years: number
  industry: string
  purpose: string
  note: string
}

export interface FormData {
  biz: string
  owner: string
  amount: string
  revenue: string
  years: string
  industry: string
  purpose: string
}

export interface ChecklistItem {
  document_type: string
  required: boolean
  upload_status: string
  file_name: string
  uploaded_at: string
}

export interface ApiResult {
  final_response: {
    final_recommendation: string
    fraud_risk: string
    repayment_risk: string
    risk_score: number
    fraud_score?: number
    trust_score?: number
    confidence: number
    explainability_report?: string
    key_reasons?: string[]
    decision_explanation?: string
    reference_id?: string
    reasoning_trace?: Array<{agent: string; text: string}>
    timeline?: Array<{stage: string; status: string; timestamp?: string}>
    audit_log?: Array<{timestamp: string; message: string}>
  }
  agent_3_output?: {
    fraud_match?: boolean
    mongodb_connected?: boolean
    fraud_records_found?: number
    fraud_signals?: string[]
  }
  agent_4_output?: {
    business_status?: string
  }
  input?: {
    business_name: string
    owner_name: string
    loan_amount: number
    monthly_revenue: number
    industry: string
    loan_purpose: string
    years_in_business: number
    application_id?: string
  }
}
