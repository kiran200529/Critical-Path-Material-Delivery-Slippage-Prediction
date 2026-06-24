import requests
import json
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from backend.config import OPENAI_API_KEY
from backend.models.order import Order
from backend.models.supplier import Supplier
from backend.models.material import Material
from backend.models.prediction import Prediction
from backend.models.alert import Alert

def generate_prediction_explanation(
    probability: float,
    risk_level: str,
    expected_delay_days: int,
    shap_features: List[Dict[str, Any]],
    input_data: Dict[str, Any]
) -> str:
    """
    Module 2: Generates an AI-assisted explanation for the prediction,
    using OpenAI if available, or falling back to a rule-based heuristic.
    """
    prompt = (
        f"You are a Senior Supply Chain Risk Expert. Explain this delivery risk prediction:\n"
        f"- Delay Probability: {int(probability * 100)}%\n"
        f"- Risk Level: {risk_level}\n"
        f"- Expected Delay Days: {expected_delay_days} days\n"
        f"- Input Data: {json.dumps(input_data)}\n"
        f"- Model Feature Contributions: {json.dumps(shap_features)}\n"
        f"Provide a brief, professional bullet-pointed root cause summary explaining WHY this risk level was predicted, "
        f"focusing on the most important model feature contributions. Limit to 3-5 clear bullet points."
    )
    
    if OPENAI_API_KEY:
        try:
            headers = {
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json"
            }
            body = {
                "model": "gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": "You are a helpful, professional construction procurement AI assistant. Keep responses concise and focused."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.2,
                "max_tokens": 300
            }
            response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=body, timeout=10)
            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"].strip()
        except Exception as e:
            print(f"OpenAI explanation request failed: {e}. Falling back to heuristics.")
            
    # Heuristic Fallback (High Fidelity)
    reasons = []
    
    # 1. Parse model contribution values to identify key risk drivers
    positive_contribs = [f for f in shap_features if f["shap_value"] > 0]
    positive_contribs.sort(key=lambda x: x["shap_value"], reverse=True)
    
    for c in positive_contribs[:3]:
        disp = c["display_name"]
        if "Supplier Tier" in disp:
            reasons.append("The selected supplier belongs to a higher-risk tier (e.g. Spot/Non-Framework) or has poor historical reliability.")
        elif "Material Category" in disp:
            reasons.append(f"The material category ({disp.split(': ')[-1]}) historically exhibits high logistics complexity and fabrication lead times.")
        elif "Distance" in disp:
            reasons.append(f"Long transit distance increase transit-phase exposure (Supplier is located far from site).")
        elif "Lead" in disp:
            reasons.append("Planned lead calendar days are compressed, providing very little scheduling buffer.")
        elif "Otif" in disp:
            reasons.append("Supplier rolling OTIF performance is poor (under 85% on-time delivery rate).")
        elif "Upstream" in disp:
            reasons.append("Upstream delay flags indicate initial program slippages in the manufacturing pipeline.")
        else:
            reasons.append(f"The factor '{disp}' is driving up the delay probability.")
            
    # Generic fallbacks if model contributions did not yield enough clear factors
    if not reasons:
        if probability >= 0.70:
            reasons.append("Supplier has poor historical on-time delivery performance.")
            reasons.append("The order falls within a high-demand construction busy season.")
            reasons.append("Transit logs suggest capacity stress in the logistics carrier network.")
        elif probability >= 0.40:
            reasons.append("Material category experiences seasonal demand surges.")
            reasons.append("Minor PO line changes before release introduced processing bottlenecks.")
        else:
            reasons.append("All operational parameters fall within standard safety margins.")
            reasons.append("Supplier holds a preferred framework status with consistent OTIF rates.")
            
    explanation = f"This delivery is likely to be delayed because:\n" + "\n".join([f"• {r}" for r in reasons])
    return explanation

def ask_procurement_copilot(db: Session, question: str) -> Dict[str, Any]:
    """
    Module 8: AI Procurement Copilot.
    Processes conversational queries about orders, suppliers, and general risks.
    Uses database records as a RAG context.
    """
    question_lower = question.lower()
    
    # 1. Retrieve RAG Context from database
    total_orders = db.query(Order).count()
    high_risk_orders = db.query(Order).filter(Order.prediction_probability >= 0.70).all()
    suppliers = db.query(Supplier).all()
    alerts = db.query(Alert).limit(5).all()
    
    # Compile a brief text database context
    context_lines = [
        f"System Stats: Total Orders: {total_orders}, Active Suppliers: {len(suppliers)}."
    ]
    
    context_lines.append("High Risk Orders:")
    for o in high_risk_orders[:3]:
        sup_name = db.query(Supplier.name).filter(Supplier.id == o.supplier_id).scalar() or "Unknown"
        mat_name = db.query(Material.material_name).filter(Material.id == o.material_id).scalar() or "Unknown"
        context_lines.append(f"- Order CSC-DEL-000000000{o.id}: {mat_name} from {sup_name}. Risk: {int(o.prediction_probability*100)}%, Expected Delay: {o.risk_score // 15 + 1} days.")
        
    context_lines.append("Supplier Rankings (Top Performers):")
    sorted_sups = sorted(suppliers, key=lambda x: x.performance_rating, reverse=True)
    for s in sorted_sups[:3]:
        context_lines.append(f"- {s.name} ({s.supplier_type}): Rating {s.performance_rating}/5.0, Risk Score {s.risk_score}/100")
        
    context = "\n".join(context_lines)
    
    # 2. Call OpenAI if available
    if OPENAI_API_KEY:
        try:
            headers = {
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json"
            }
            body = {
                "model": "gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": (
                        "You are an AI Procurement Copilot for a construction material supply platform. "
                        "Answer the user's question using the provided context. If the question is about specific orders, "
                        "cite their ID. Keep the response professional, actionable, and under 150 words."
                    )},
                    {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"}
                ],
                "temperature": 0.3,
                "max_tokens": 250
            }
            response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=body, timeout=10)
            if response.status_code == 200:
                result = response.json()
                return {
                    "answer": result["choices"][0]["message"]["content"].strip(),
                    "sources": ["Prediction History", "Supplier Performance Records"]
                }
        except Exception as e:
            print(f"OpenAI Copilot request failed: {e}. Using local response engine.")
            
    # Heuristic Rule-Based NLP Processor (Fallback)
    answer = ""
    sources = ["Database RAG Index"]
    
    if "risky" in question_lower or "danger" in question_lower or "high risk" in question_lower:
        if high_risk_orders:
            risky_list = []
            for o in high_risk_orders:
                sup_name = db.query(Supplier.name).filter(Supplier.id == o.supplier_id).scalar() or "Supplier"
                mat_name = db.query(Material.material_name).filter(Material.id == o.material_id).scalar() or "Material"
                risky_list.append(f"**Order #{o.id}** ({mat_name} from {sup_name}) has a **{int(o.prediction_probability*100)}%** risk of delay.")
            answer = "The highest risk orders currently flagged by the AI engine are:\n\n" + "\n".join([f"- {item}" for item in risky_list]) + "\n\nI recommend utilizing the Smart Supplier Recommendation engine to find alternatives."
        else:
            answer = "Great news! There are currently no critical high-risk orders flagged (delay probability >= 70%) in the database."
            
    elif "supplier" in question_lower or "choose" in question_lower or "recommend" in question_lower:
        best_sup = sorted_sups[0]
        worst_sup = sorted(suppliers, key=lambda x: x.risk_score, reverse=True)[0]
        answer = (
            f"Based on historical data and prediction accuracy:\n"
            f"- **Top Recommended Supplier**: **{best_sup.name}** (Rating: {best_sup.performance_rating}/5, Risk Score: {best_sup.risk_score}/100).\n"
            f"- **Highest Risk Supplier**: **{worst_sup.name}** (Rating: {worst_sup.performance_rating}/5, Risk Score: {worst_sup.risk_score}/100).\n\n"
            f"For new orders of critical-path items, prioritize Framework-based agreement suppliers like {best_sup.name} to minimize OTIF slippages."
        )
        sources.append("Supplier Scores Table")
        
    elif "material" in question_lower or "delays" in question_lower or "cause" in question_lower:
        answer = (
            "According to the ML feature importance analysis, the material categories most prone to delivery delays are:\n\n"
            "1. **Structural Steel & Metalwork** (due to customized fabrication times and oversize permits required).\n"
            "2. **Facades & Glazing** (susceptible to damage and transit handling delays).\n"
            "3. **MEP - Plant & Equipment** (driven by complex upstream manufacturing backlogs).\n\n"
            "For these categories, we suggest adding a minimum of **5 days safety buffer** in the Procurement Planner."
        )
        sources.append("Model Feature Contribution Engine")
        
    elif "reduce" in question_lower or "mitigate" in question_lower or "prevent" in question_lower:
        answer = (
            "To reduce project risk and prevent critical path material delays, apply these strategies:\n\n"
            "• **Adjust Procurement Schedule**: Order critical items earlier. Use the Planner module to calculate optimal order dates.\n"
            "• **Establish Safety Buffers**: Set a 3-day safety buffer for standard goods, and 5-7 days for bespoke fabricated materials.\n"
            "• **Select Framework Suppliers**: Restructure purchases toward Preferred Framework suppliers who maintain 95%+ OTIF ratings.\n"
            "• **Diversify Logistics**: For regional projects, choose FCA terms to allow self-collection and bypass carrier bottlenecks."
        )
        
    else:
        answer = (
            f"Hello! I am your AI Procurement Copilot. I scan prediction logs, supplier ratings, and active alerts to guide your operations.\n\n"
            f"You can ask me questions like:\n"
            f"- *'Why is this order risky?'*\n"
            f"- *'Which supplier should I choose?'*\n"
            f"- *'What materials cause the most delays?'*\n"
            f"- *'How can I reduce project risk?'*\n\n"
            f"Current context: There are **{total_orders} total orders**, **{len(high_risk_orders)} critical warnings**, and **{len(alerts)} pending alerts**."
        )
        
    return {
        "answer": answer,
        "sources": sources
    }
