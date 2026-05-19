import re
from io import BytesIO

import pandas as pd
import streamlit as st
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle


def find_evidence_sentences(contract_text, matched_keywords, limit=2):
    sentences = re.split(r'(?<=[.!?])\s+', contract_text)
    evidence = []

    for sentence in sentences:
        sentence_lower = sentence.lower()

        for keyword in matched_keywords:
            if keyword in sentence_lower:
                clean_sentence = sentence.strip()
                if clean_sentence not in evidence:
                    evidence.append(clean_sentence)
                break

        if len(evidence) >= limit:
            break

    return evidence


def analyze_contract(contract_text):
    text = contract_text.lower()

    checks = {
        "Parties": {
            "keywords": ["agreement between", "party", "parties", "client", "contractor", "company"],
            "strong_threshold": 2
        },
        "Payment Terms": {
            "keywords": ["payment", "fee", "invoice", "compensation", "amount", "due date", "late payment"],
            "strong_threshold": 2
        },
        "Termination": {
    "keywords": [
        "termination", "terminate", "notice period", "written notice",
        "days written notice", "breach", "end this agreement"
    ],
    "strong_threshold": 2
},
        "Confidentiality": {
            "keywords": ["confidential", "confidentiality", "non-disclosure", "proprietary information"],
            "strong_threshold": 1
        },
        "Limitation of Liability": {
            "keywords": ["limitation of liability", "liability shall not exceed", "not liable", "indirect damages", "consequential damages"],
            "strong_threshold": 1
        },
        "Indemnity": {
            "keywords": ["indemnify", "indemnity", "hold harmless", "defend against claims"],
            "strong_threshold": 1
        },
        "Governing Law": {
            "keywords": ["governing law", "laws of", "jurisdiction", "applicable law"],
            "strong_threshold": 1
        },
        "Dispute Resolution": {
            "keywords": ["dispute", "arbitration", "mediation", "court", "settlement", "resolve disputes"],
            "strong_threshold": 2
        },
        "Intellectual Property": {
            "keywords": ["intellectual property", "copyright", "trademark", "patent", "ownership", "license"],
            "strong_threshold": 2
        },
        "Data Protection": {
    "keywords": [
        "personal data", "data protection", "gdpr", "privacy",
        "data processing", "data controller", "data processor",
        "purpose of providing", "providing the services"
    ],
    "strong_threshold": 2
},
        "Force Majeure": {
            "keywords": ["force majeure", "act of god", "beyond reasonable control", "natural disaster", "war", "pandemic"],
            "strong_threshold": 1
        },
        "Assignment": {
            "keywords": ["assignment", "assign", "transfer this agreement", "without prior written consent"],
            "strong_threshold": 1
        },
        "Non-Compete / Restrictive Covenant": {
            "keywords": ["non-compete", "non-solicitation", "restrictive covenant", "restraint of trade"],
            "strong_threshold": 1
        }
    }

    results = {}

    for clause, data in checks.items():
        keywords = data["keywords"]
        threshold = data["strong_threshold"]

        matched_keywords = [keyword for keyword in keywords if keyword in text]

        if len(matched_keywords) >= threshold:
            status = "Present"
        elif len(matched_keywords) >= 1:
            status = "Weak"
        else:
            status = "Missing"

        evidence = find_evidence_sentences(contract_text, matched_keywords)

        results[clause] = {
            "status": status,
            "matched_keywords": matched_keywords,
            "evidence": evidence
        }

    total_checks = len(checks)
    score = 0

    for item in results.values():
        if item["status"] == "Present":
            score += 1
        elif item["status"] == "Weak":
            score += 0.5

    final_score = round((score / total_checks) * 100, 2)

    if final_score >= 80:
        risk_level = "Low Risk"
    elif final_score >= 50:
        risk_level = "Medium Risk"
    else:
        risk_level = "High Risk"

    return {
        "score": final_score,
        "risk_level": risk_level,
        "results": results
    }


def get_recommendation(clause):
    recommendations = {
        "Parties": "The contract should clearly identify all parties, including their legal names and roles.",
        "Payment Terms": "The contract should clearly state payment amount, due dates, invoicing process, and consequences of late payment.",
        "Termination": "The contract should explain how either party may terminate the agreement, including notice periods and breach-related termination.",
        "Confidentiality": "The contract should include confidentiality obligations covering sensitive, business, or proprietary information.",
        "Limitation of Liability": "The contract should clarify whether liability is limited and whether indirect or consequential damages are excluded.",
        "Indemnity": "The contract should state whether one party must indemnify the other for losses, claims, or third-party liabilities.",
        "Governing Law": "The contract should state the governing law and, where appropriate, the competent jurisdiction.",
        "Dispute Resolution": "The contract should explain how disputes will be resolved, such as through negotiation, mediation, arbitration, or courts.",
        "Intellectual Property": "The contract should explain ownership and permitted use of intellectual property created, shared, or licensed under the agreement.",
        "Data Protection": "The contract should address privacy and data protection obligations where personal data is collected, processed, or shared.",
        "Force Majeure": "The contract should explain what happens if performance becomes impossible due to events beyond the parties’ control.",
        "Assignment": "The contract should clarify whether rights or obligations may be assigned or transferred to another party.",
        "Non-Compete / Restrictive Covenant": "Any restrictive covenant should be clear, reasonable, and legally enforceable in the relevant jurisdiction."
    }

    return recommendations.get(clause, "This clause should be reviewed carefully.")


def convert_report_to_dataframe(report):
    rows = []

    for clause, result in report["results"].items():
        rows.append({
            "Clause": clause,
            "Status": result["status"],
            "Matched Keywords": ", ".join(result["matched_keywords"]) if result["matched_keywords"] else "None",
            "Evidence": " | ".join(result["evidence"]) if result["evidence"] else "None",
            "Recommendation": get_recommendation(clause) if result["status"] in ["Weak", "Missing"] else "No immediate issue detected in this basic screening."
        })

    return pd.DataFrame(rows)


def generate_legal_conclusion(report):
    present = []
    weak = []
    missing = []

    for clause, result in report["results"].items():
        if result["status"] == "Present":
            present.append(clause)
        elif result["status"] == "Weak":
            weak.append(clause)
        else:
            missing.append(clause)

    if report["score"] >= 80:
        conclusion = (
            "Based on this keyword-based screening, the contract appears to include many key clauses. "
            "However, the wording, enforceability, and commercial fairness of each clause should still be reviewed."
        )
    elif report["score"] >= 50:
        conclusion = (
            "Based on this keyword-based screening, the contract includes some important clauses, "
            "but several areas may require improvement or further legal review."
        )
    else:
        conclusion = (
            "Based on this keyword-based screening, the contract appears to be missing several important clauses. "
            "The missing or weak areas should be reviewed before relying on the contract."
        )

    return conclusion, present, weak, missing


def generate_pdf_report(report, df_report, conclusion):
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("Contract Risk Analyzer Report", styles["Title"]))
    story.append(Spacer(1, 16))

    story.append(Paragraph(
        f"<b>Overall Score:</b> {report['score']}%<br/>"
        f"<b>Risk Level:</b> {report['risk_level']}",
        styles["Normal"]
    ))
    story.append(Spacer(1, 16))

    story.append(Paragraph("<b>Legal Screening Conclusion</b>", styles["Heading2"]))
    story.append(Paragraph(conclusion, styles["Normal"]))
    story.append(Spacer(1, 16))

    story.append(Paragraph("<b>Detailed Clause Analysis</b>", styles["Heading2"]))

    table_data = [["Clause", "Status", "Matched Keywords"]]

    for _, row in df_report.iterrows():
        table_data.append([
            row["Clause"],
            row["Status"],
            row["Matched Keywords"]
        ])

    table = Table(table_data, colWidths=[150, 80, 250])

    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("PADDING", (0, 0), (-1, -1), 6),
    ]))

    story.append(table)
    story.append(Spacer(1, 16))

    story.append(Paragraph("<b>Recommendations</b>", styles["Heading2"]))

    for clause, result in report["results"].items():
        if result["status"] in ["Weak", "Missing"]:
            story.append(Paragraph(f"<b>{result['status']}: {clause}</b>", styles["Normal"]))
            story.append(Paragraph(get_recommendation(clause), styles["Normal"]))
            story.append(Spacer(1, 8))

    story.append(Spacer(1, 16))

    story.append(Paragraph(
        "<b>Legal Note:</b> This report is generated through keyword-based screening. "
        "It does not replace professional legal advice or a full contract review.",
        styles["Normal"]
    ))

    doc.build(story)
    buffer.seek(0)

    return buffer


st.set_page_config(
    page_title="Contract Risk Analyzer",
    page_icon="📄",
    layout="wide"
)

st.markdown("""
<style>
    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    .project-card {
        background-color: white;
        padding: 1.2rem;
        border-radius: 14px;
        border: 1px solid #e5e7eb;
        box-shadow: 0 4px 12px rgba(0,0,0,0.04);
        margin-bottom: 1rem;
    }

    .small-muted {
        color: #6b7280;
        font-size: 0.95rem;
    }
</style>
""", unsafe_allow_html=True)

st.title("📄 Contract Risk Analyzer")

st.markdown("""
<div class="project-card">
    <p>
        This tool performs a basic legal risk screening of contract text.
        It checks whether key clauses such as termination, payment terms,
        confidentiality, limitation of liability, indemnity, governing law,
        dispute resolution, intellectual property, data protection, and force majeure are present.
    </p>
    <p class="small-muted">
        Built as a LegalTech and data science project combining legal analysis,
        keyword-based NLP, evidence extraction, and automated report generation.
    </p>
</div>
""", unsafe_allow_html=True)

st.warning(
    "This is a keyword-based screening tool. It does not replace professional legal advice or a full contract review."
)

st.sidebar.title("About this project")

st.sidebar.write(
    "Contract Risk Analyzer is a beginner LegalTech/data science project for screening contract clauses."
)

st.sidebar.markdown("""
**Main features:**
- Contract clause detection
- Present / Weak / Missing classification
- Matched keyword detection
- Evidence sentence extraction
- Legal-style recommendations
- CSV report download
- PDF report download
""")

st.sidebar.markdown("""
**Built with:**
- Python
- Streamlit
- pandas
- ReportLab
- Regex
""")

sample_contract = """
This Agreement is made between ABC Limited and XYZ Services.

The Client shall pay the Contractor a monthly fee of 2,000 euros within 14 days of receiving an invoice.

Either party may terminate this Agreement by giving 30 days written notice.

Both parties agree to keep confidential information private and not disclose it to third parties.

This Agreement shall be governed by the laws of Germany.

The Contractor may use personal data only for the purpose of providing the services.
"""

contract_text = st.text_area(
    "Paste contract text here:",
    value=sample_contract,
    height=350
)

analyze_button = st.button("Analyze Contract")

if analyze_button:
    if not contract_text.strip():
        st.error("Please paste a contract before running the analysis.")
    else:
        report = analyze_contract(contract_text)
        df_report = convert_report_to_dataframe(report)
        conclusion, present, weak, missing = generate_legal_conclusion(report)

        st.subheader("Overall Result")

        col1, col2 = st.columns(2)

        with col1:
            st.metric("Contract Screening Score", f"{report['score']}%")

        with col2:
            st.metric("Risk Level", report["risk_level"])

        if report["risk_level"] == "Low Risk":
            st.success("The contract appears to include many key clauses.")
        elif report["risk_level"] == "Medium Risk":
            st.warning("The contract includes some key clauses but may need improvement.")
        else:
            st.error("The contract appears to be missing several important clauses.")

        st.subheader("Legal Screening Conclusion")
        st.write(conclusion)

        st.subheader("Detailed Analysis Table")
        st.dataframe(df_report, use_container_width=True)

        st.subheader("Present Clauses")
        if present:
            for item in present:
                result = report["results"][item]

                with st.expander(item):
                    st.write("**Matched keywords:**")
                    st.write(", ".join(result["matched_keywords"]) if result["matched_keywords"] else "None")

                    st.write("**Evidence:**")
                    if result["evidence"]:
                        for sentence in result["evidence"]:
                            st.write(f"- {sentence}")
                    else:
                        st.write("None")
        else:
            st.write("No present clauses detected.")

        st.subheader("Weak Clauses")
        if weak:
            for item in weak:
                result = report["results"][item]

                with st.expander(item):
                    st.write("**Matched keywords:**")
                    st.write(", ".join(result["matched_keywords"]) if result["matched_keywords"] else "None")

                    st.write("**Evidence:**")
                    if result["evidence"]:
                        for sentence in result["evidence"]:
                            st.write(f"- {sentence}")
                    else:
                        st.write("None")

                    st.write("**Recommendation:**")
                    st.write(get_recommendation(item))
        else:
            st.write("No weak clauses detected.")

        st.subheader("Missing Clauses")
        if missing:
            for item in missing:
                with st.expander(item):
                    st.write("**Matched keywords:** None")
                    st.write("**Evidence:** None")
                    st.write("**Recommendation:**")
                    st.write(get_recommendation(item))
        else:
            st.write("No missing clauses detected.")

        st.subheader("Download Report")

        csv_data = df_report.to_csv(index=False).encode("utf-8")

        st.download_button(
            label="Download CSV Report",
            data=csv_data,
            file_name="contract_risk_analysis_report.csv",
            mime="text/csv"
        )

        pdf_data = generate_pdf_report(report, df_report, conclusion)

        st.download_button(
            label="Download PDF Report",
            data=pdf_data,
            file_name="contract_risk_analysis_report.pdf",
            mime="application/pdf"
        )