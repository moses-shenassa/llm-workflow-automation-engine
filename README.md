# LLM Workflow Automation Engine

A production-style proof‑of‑concept demonstrating **LLM‑powered ticket triage**, workflow orchestration with **n8n**, and a clean **FastAPI + HTML/JS frontend**. Built to showcase real‑world automation architecture for employers evaluating AI engineering capability.

Why This Project

This repo is designed as a realistic, production-style example for employers evaluating AI workflow engineering skills. It demonstrates:

End-to-end architecture (frontend → API → LLM → workflow engine)

Structured JSON outputs from an LLM (ticket summary, category, priority, review flag)

Integration with an orchestration tool (n8n webhook → FastAPI) suitable for real-world automation.

---

## 🌐 Overview

This project implements an end‑to‑end workflow:

1. **Frontend (HTML/JS)** – A simple Ticket Triage Console where a user submits:
   - customer name  
   - email  
   - ticket text  

2. **Backend (FastAPI)** – Receives the ticket and runs the core LLM classification:
   - summarizes the issue  
   - assigns category  
   - determines priority  
   - flags whether human review is needed  
   - returns structured JSON  

3. **Workflow Orchestration (n8n)** – Optional automation layer:
   - Production webhook endpoint  
   - HTTP Request → FastAPI  
   - Webhook Response returns structured result  

---

## 🏗️ Architecture

[ Frontend ] → [ FastAPI ] → [ LLM Engine ]  
                 ↑  
                 |  
           [ n8n Webhook ]

---

## 📁 Project Structure

```
llm-workflow-automation-engine/
├── src/
│   ├── api_server.py
│   ├── workflow_engine.py
│   ├── prompts.py
│   ├── config.py
│   ├── schema.py
│
├── static/
│   └── index.html
│
├── n8n/
│   └── ticket-intake-llm.workflow.json
│
├── requirements.txt
├── config.example.toml
└── README.md
```

Reliability & Validation

All LLM responses are coerced into a structured schema (see schema.py).

The workflow engine validates that required fields are present before returning a response.

Errors are surfaced as HTTP 4xx/5xx with JSON error bodies for easy monitoring and integration.

---

## 🔧 Setup

### 1. Clone the repo
git clone <your_repo>

### 2. Create venv
python -m venv .venv  
# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate


### 3. Install deps
pip install -r requirements.txt

### 4. Copy config
copy config.example.toml config.toml

Fill in API key + model.

---

## ▶️ Run FastAPI + Frontend
uvicorn src.api_server:app --reload  
→ Visit: http://127.0.0.1:8000/

---

## 🌐 n8n Setup (Optional)

Run n8n:
n8n

Import workflow file in `n8n/ticket-intake-llm.workflow.json`.

Production URL will look like:
http://localhost:5678/webhook/ticket-intake-llm

---

## 📈 Sample Output

summary: Customer reports a double charge  
metadata:  
  customer_name: Jane Doe  
  email: jane@example.com  
  priority: high  
  category: billing  
  needs_human_review: true  

---

