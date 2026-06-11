# NexusAI-BankGuard

AI-powered autonomous lending intelligence platform for SME loan underwriting and fraud detection.

Overview

NexusAI BankGuard uses a multi-agent AI architecture to automate loan assessment, document verification, fraud analysis, business validation, risk scoring, and explainable decision making.

The system provides transparent lending recommendations while keeping humans in the loop for borderline cases.

Features
Multi-Agent AI Pipeline
Dynamic Risk Scoring
Fraud Detection Engine
Business Validation
Explainable AI Decisions
Human-in-the-Loop Review
Document Verification
Audit Logging
MongoDB Atlas Integration
FastAPI Backend
React + TypeScript Frontend
Vercel Deployment
Architecture
Applicant
    ↓
Intake Agent
    ↓
Document Verification Agent
    ↓
Fraud Intelligence Agent
    ↓
Business Validation Agent
    ↓
Risk Scoring Agent
    ↓
Explainability Agent
    ↓
Trust & Compliance Agent
    ↓
Final Decision
(APPROVED / MANUAL REVIEW / REJECTED)
Tech Stack
Frontend
React 18
TypeScript
Vite
Tailwind CSS
Backend
Python
FastAPI
MongoDB Atlas
GridFS
Deployment
Vercel
AI Agents
Agent	Responsibility
Agent 1	Intake & Risk Coordination
Agent 2	Document Verification
Agent 3	Fraud Intelligence
Agent 4	Business Validation
Agent 5	Risk Scoring
Agent 6	Explainability
Agent 7	Trust & Compliance
Decision Outcomes
Approved

Low-risk applications with strong verification.

Manual Review

Borderline applications requiring human oversight.

Rejected

Applications exhibiting significant fraud indicators or unacceptable risk.

Installation
Clone Repository
git clone https://github.com/alok20060/Harvest.git
cd Harvest
Install Backend Dependencies
pip install -r requirements.txt
Start Backend
uvicorn main:app --reload
Start Frontend
cd nexus-frontend
npm install
npm run dev
Build
npm run build
Deployment

Hosted on Vercel with MongoDB Atlas.

Key Highlights
Autonomous multi-agent lending workflow.
Explainable and auditable decisions.
Fraud-aware underwriting.
Human-in-the-loop governance.
Scalable cloud-native architecture.
Future Improvements
OCR-based document extraction
Credit bureau integration
Real-time KYC APIs
Advanced graph-based fraud analytics
Reinforcement learning for adaptive risk scoring
Authors

Alok VK

Engineering Student | AI & ML Enthusiast
