\# Contract Risk Analyzer



A LegalTech and data science web application that performs a basic legal risk screening of contract text.



\## Overview



Contract Risk Analyzer allows users to paste contract text and receive a keyword-based screening report. The tool checks whether important contract clauses are present, weak, or missing.



It is designed as a beginner LegalTech project combining legal knowledge, text processing, keyword-based NLP, evidence extraction, and automated report generation.



\## Features



\- Contract clause detection

\- Present / Weak / Missing classification

\- Matched keyword detection

\- Evidence sentence extraction

\- Legal-style recommendations

\- CSV report download

\- PDF report download

\- Streamlit web interface



\## Clauses Checked



\- Parties

\- Payment Terms

\- Termination

\- Confidentiality

\- Limitation of Liability

\- Indemnity

\- Governing Law

\- Dispute Resolution

\- Intellectual Property

\- Data Protection

\- Force Majeure

\- Assignment

\- Non-Compete / Restrictive Covenant



\## Tech Stack



\- Python

\- Streamlit

\- pandas

\- ReportLab

\- Regular Expressions



\## How It Works



The app uses keyword-based text analysis to identify key contract clauses. It classifies each clause as Present, Weak, or Missing, extracts supporting evidence sentences, generates legal-style recommendations, and provides downloadable CSV and PDF reports.



\## Disclaimer



This tool is for learning and preliminary contract screening only. It does not replace professional legal advice or a full contract review.



\## How to Run Locally



```bash

pip install -r requirements.txt

streamlit run app.py



Author



Built by Akinwumi Oluwatofunmisin Testimony as a LegalTech and data science portfolio project.

