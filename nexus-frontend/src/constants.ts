import type { DemoCase } from './types'

export const BACKEND = (typeof window !== 'undefined' &&
  (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'))
  ? 'http://127.0.0.1:8006'
  : ''

export const VIDEO_URL = 'https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260403_050628_c4e32401-fab4-4a27-b7a8-6e9291cd5959.mp4'

export const DEMO_CASES: DemoCase[] = [
  { id:'DEMO-01', label:'Demo Case 1', name:'ABC Traders Pvt Ltd', owner:'Rajesh Kumar', amount:500000, revenue:200000, years:5, industry:'Retail & FMCG', purpose:'Working capital expansion', note:'Established business · Low ratio' },
  { id:'DEMO-02', label:'Demo Case 2', name:'New Startup Ltd', owner:'Test User', amount:1000000, revenue:100000, years:1, industry:'Services & IT', purpose:'Expansion', note:'New startup · Medium ratio' },
  { id:'DEMO-03', label:'Demo Case 3', name:'Fake Corp Ltd', owner:'Fraud User', amount:1000000, revenue:100000, years:3, industry:'General Trade', purpose:'Equipment purchase', note:'Medium ratio · Watchlist match' },
]

export const INDUSTRIES = [
  'Retail & FMCG', 'Services & IT', 'Manufacturing', 'Healthcare', 'Real Estate',
  'Agriculture', 'Finance & Banking', 'Education', 'Logistics & Transport',
  'Food & Beverage', 'Construction', 'General Trade', 'Other'
]
