from fastapi import APIRouter, HTTPException
from datetime import datetime, timedelta
from app.schemas import ScenarioRequest, ScenarioResponse, Scenario, CashFlowProjection
from app.services.scenario import build_scenario_prompt, generate_scenario
from app.db.pool import get_pool
from pydantic import ValidationError
import json

router = APIRouter()

def validate_flat_scenario(scenario: dict) -> bool:
    required_keys = {"recommendations", "tax_implications", "cash_flow_projection"}
    projection_keys = {"initial_impact", "estimated_tax_savings", "net_effect"}
    return (
        isinstance(scenario, dict)
        and required_keys.issubset(scenario.keys())
        and isinstance(scenario["recommendations"], str)
        and isinstance(scenario["tax_implications"], str)
        and isinstance(scenario["cash_flow_projection"], dict)
        and projection_keys.issubset(scenario["cash_flow_projection"].keys())
    )

@router.post("/scenario", response_model=ScenarioResponse)
async def generate_financial_scenario(payload: ScenarioRequest):
    user_id = payload.user_id
    session_id = payload.session_id
    scenario_type = payload.scenario_type
    timeframe_days = payload.timeframe_days
    aggregation_days = payload.aggregation_days
    user_request = payload.request
    hypothetical_changes = payload.hypothetical_changes

    pool = await get_pool()
    async with pool.acquire() as conn:
        recent_cutoff = datetime.now() - timedelta(days=timeframe_days)
        aggregation_cutoff = datetime.now() - timedelta(days=aggregation_days)

        recent_transactions = await conn.fetch("""
            SELECT date, description, amount, COALESCE(category,'uncategorized') AS category
            FROM transactions
            WHERE user_id = $1 AND date >= $2
            ORDER BY date DESC
            LIMIT 20
        """, user_id, recent_cutoff)

        aggregated_transactions = await conn.fetch("""
            SELECT to_char(date, 'YYYY-MM') AS month, category,
                   SUM(amount) AS total_amount
            FROM transactions
            WHERE user_id = $1 AND date >= $2 AND date < $3
            GROUP BY month, category
            ORDER BY month DESC
            LIMIT 12
        """, user_id, aggregation_cutoff, recent_cutoff)

    recent_summary = "\n".join([
        f"- {tx['date'].strftime('%Y-%m-%d')}: {tx['description']} (£{tx['amount']}) [{tx['category']}]"
        for tx in recent_transactions
    ]) if recent_transactions else "No recent transactions."

    agg_summary = "\n".join([
        f"- {row['month']} | {row['category']}: £{row['total_amount']}"
        for row in aggregated_transactions
    ]) if aggregated_transactions else "No older transactions."

    total_income = sum(tx['amount'] for tx in recent_transactions if tx['amount'] > 0)
    total_expenses = sum(-tx['amount'] for tx in recent_transactions if tx['amount'] < 0)

    change_texts = []
    for change in hypothetical_changes:
        amt = change.amount
        cat = change.category.lower()
        if amt > 0:
            total_income += amt
        else:
            total_expenses += -amt
        change_texts.append(f"- {change.description} (£{amt}) [{cat}]")

    hypothetical_summary = "\n".join(change_texts) if change_texts else "No hypothetical changes."
    net_balance = total_income - total_expenses

    summary_text = (
        f"Total income over last {timeframe_days} days + hypothetical changes: £{total_income}\n"
        f"Total expenses over last {timeframe_days} days + hypothetical changes: £{total_expenses}\n"
        f"Net balance over this period: £{net_balance}\n"
    )

    full_prompt = build_scenario_prompt(
        user_request,
        recent_summary,
        agg_summary,
        hypothetical_summary,
        summary_text
    )

    scenario_result = {}
    try:
        scenario_result = await generate_scenario(full_prompt)
        scenario_response = scenario_result.get("response", {})
        confidence_score = scenario_result.get("confidence", None)

        if not validate_flat_scenario(scenario_response):
            print("⚠️ Scenario format drift detected. Falling back to default.")
            scenario_response = {
                "recommendations": "Unable to validate scenario.",
                "tax_implications": "Model returned unexpected format.",
                "cash_flow_projection": {
                    "initial_impact": 0.0,
                    "estimated_tax_savings": None,
                    "net_effect": None
                }
            }

        validated_scenario = Scenario(**scenario_response)

    except ValidationError as ve:
        print("❌ Scenario validation failed:", ve)
        validated_scenario = Scenario(
            recommendations="Unable to validate scenario.",
            tax_implications="The model returned an unexpected format.",
            cash_flow_projection=CashFlowProjection(
                initial_impact=0.0,
                estimated_tax_savings=None,
                net_effect=None
            )
        )
        confidence_score = None

    except Exception as e:
        print("❌ LLM generation failed:", e)
        validated_scenario = Scenario(
            recommendations="Scenario generation failed.",
            tax_implications=str(e),
            cash_flow_projection=CashFlowProjection(
                initial_impact=0.0,
                estimated_tax_savings=None,
                net_effect=None
            )
        )
        confidence_score = None

    async with pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO conversation_logs (
                user_id, input_text, llm_response, task_type, source_model, session_id
            ) VALUES ($1, $2, $3, $4, $5, $6)
        """, str(user_id), full_prompt, json.dumps(validated_scenario.dict()), scenario_type, scenario_result.get("source_model", "unknown"), session_id)

    return ScenarioResponse(
        status="success",
        scenario=validated_scenario,
        confidence=confidence_score,
        scenario_type=scenario_type
    )