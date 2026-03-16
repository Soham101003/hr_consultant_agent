import re
import gradio as gr
from langchain.tools import tool

# ---- TOOL DEFINITIONS ----

@tool
def compliance_tool(transcripts: str):
    """Detect unethical hiring advice in transcripts given by HR consultants and flag them"""
    violation_examples = [
        "exaggerat",
        "fake experience",
        "lie on your resume",
        "young candidates",
        "machine learning experience",
    ]
    for v in violation_examples:
        if re.search(v, transcripts.lower()):
            return "Violations detected"
    return "No violations found"

@tool
def risk_scoring_tool(user_rating: float, consultations_per_week: int, violation: str):
    """Calculate the risk score for a particular HR consultant"""
    violation_score = 40 if violation == "Violations detected" else 0
    rating_penalty = (5 - user_rating) * 10
    activity_risk = max(0, consultations_per_week - 40) * 0.5
    return violation_score + rating_penalty + activity_risk

@tool
def alerting_tool(consultant_id: str, risk_score: float, violation: str):
    """Generate alert if compliance violation is too HIGH or any violation detected"""
    if risk_score > 40 or violation == "Violations detected":
        return f"ALERT: Consultant {consultant_id} flagged for ethical compliance violations"
    else:
        return f"No compliance violations, no alert required"

# ---- GRADIO FUNCTION ----

def run_check(consultant_id, transcript, user_rating, consultations_per_week):
    violation = compliance_tool.invoke({"transcripts": transcript})
    risk = risk_scoring_tool.invoke({
        "user_rating": user_rating,
        "consultations_per_week": int(consultations_per_week),
        "violation": violation
    })
    alert = alerting_tool.invoke({
        "consultant_id": consultant_id,
        "risk_score": risk,
        "violation": violation
    })
    return violation, str(risk), alert

# ---- GRADIO INTERFACE ----

demo = gr.Interface(
    fn=run_check,
    inputs=[
        gr.Textbox(label="Consultant ID", value="HR01"),
        gr.Textbox(label="Transcript", lines=3, value="Your CV is weak, exaggerate your experience"),
        gr.Slider(minimum=1, maximum=5, step=0.5, value=2.5, label="User Rating"),
        gr.Slider(minimum=0, maximum=100, step=1, value=60, label="Consultations per Week")
    ],
    outputs=[
        gr.Textbox(label="Violation Status"),
        gr.Textbox(label="Risk Score"),
        gr.Textbox(label="Alert")
    ],
    title="HR Compliance Monitoring Agent",
    description="Enter consultant details to check for ethical violations and compute risk score.",
    examples=[
        ["HR01", "Your CV is weak, exaggerate your experience", 2.5, 60],
        ["HR02", "You should target backend developer roles with your CV", 5.0, 20],
        ["HR03", "Recruiters usually choose young candidates for this role", 4.5, 30],
        ["HR04", "Let us optimize your resume for ATS scoring", 3.0, 50],
        ["HR05", "Add some Machine learning experience to your resume", 4.0, 20],
    ]
)

if __name__ == "__main__":
    demo.launch()
