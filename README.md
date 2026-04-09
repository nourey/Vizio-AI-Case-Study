# Vizio Case

This repository contains five independent sections. Each section lives in its own folder with a dedicated write-up.

---

## Sections

### 1. Data Pipeline
**Folder:** [`Pipeline/`](Pipeline/)

Normalizes raw job postings from three providers Dice, Naukri, and Reed into a single canonical schema. Each provider has its own transformer module. A single entry point (`pipeline.py`) loads all three CSVs and outputs a unified DataFrame.

- [`pipeline.py`](Pipeline/pipeline.py) — entry point
- [`dice.py`](Pipeline/dice.py) — Dice transformer
- [`naukri.py`](Pipeline/naukri.py) — Naukri transformer
- [`reed.py`](Pipeline/reed.py) — Reed transformer
- [`Dockerfile`](Pipeline/Dockerfile) — containerized runner
- [`requirements.txt`](Pipeline/requirements.txt) — dependencies

---

### 2. Data Modeling — Talent Schema
**Folder:** [`Data Modeling - Talent Schema/`](Data%20Modeling%20-%20Talent%20Schema/)

Proposes a relational schema for storing candidate profiles. Covers table design, normalization decisions, and the reasoning behind prioritizing candidates as the primary entity.

- [`data_model.md`](Data%20Modeling%20-%20Talent%20Schema/data_model.md) — schema design and rationale
- [`db_schema.dbml`](Data%20Modeling%20-%20Talent%20Schema/db_schema.dbml) — DBML schema definition

---

### 3. Company Enrichment Design
**Folder:** [`Company Enrichment Design/`](Company%20Enrichment%20Design/)

System design for enriching raw company data from job feeds. Covers primary company representation, identity resolution for deduplication, and separation of raw vs. processed data layers.

- [`SystemDesign.md`](Company%20Enrichment%20Design/SystemDesign.md)

---

### 4. Hiring Intent Design
**Folder:** [`Hiring Intent Design/`](Hiring%20Intent%20Design/)

A signal based model to estimate how actively a company is hiring. Combines job posting signals with external signals to score hiring intent beyond the presence of a job ad.

- [`Design.md`](Hiring%20Intent%20Design/Design.md)

---

### 5. Job-to-Talent Matching MVP
**Folder:** [`Job-to-Talent Matching MVP/`](Job-to-Talent%20Matching%20MVP/)

An MVP design for matching candidates to job postings in two stages: eligibility filtering and fit scoring. Assumes structured, normalized fields on both the job and talent sides.

- [`MVP.md`](Job-to-Talent%20Matching%20MVP/MVP.md)

---

### 6. RAG Extension
**Folder:** [`RAG Extension/`](RAG%20Extension/)

System design for extending the matching pipeline with a Retrieval Augmented Generation layer. Covers what data to index, retrieval strategy, and how RAG complements the structured scoring approach.

- [`System.md`](RAG%20Extension/System.md)
