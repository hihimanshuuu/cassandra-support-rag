# AI Support Assistant: Project Plan

## Goal
- LLM providers (current): Gemini (free tier) + OpenAI. 

## Decisions
- Sample data: Apache Cassandra docs (copied into own free Confluence Cloud space)
- Synthetic data: LLM-generated cases, TRs, logs (fictional company "Northwind Data Services")
- Vector store: Chroma (local)
- Embeddings: BGE-M3 (fallback: nomic-embed-text), independent of chat LLM
- Interface: Streamlit with provider dropdown
- Python 3.10.5, venv in .venv
- Evaluation: golden set of 60-100 questions; baseline first, thresholds later

## Timeline (start Oct 31, 2026)
1 Setup | 2 Confluence content | 3 Sample data | 4 Golden set | 5 Ingestion/retrieval
6 Generation + citations | 7 Provider switching | 8 Baseline eval | 9 Streamlit app | 10 Tuning + handover
Target finish: ~Dec 18 (+1 buffer week)

## Rules
- Plan before code; understand each step before moving on.
- Never put real company data in this project or send it to personal API accounts.