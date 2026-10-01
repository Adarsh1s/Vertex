"""FinPulse: transaction ETL and personal-finance intelligence endpoints."""
import csv
import hashlib
import io
import json
from datetime import date
from decimal import Decimal, InvalidOperation

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user

router = APIRouter()


class GoalCreate(BaseModel):
    goal_name: str = Field(min_length=2, max_length=120)
    target_amount: float = Field(gt=0)
    current_amount: float = Field(default=0, ge=0)
    target_date: date
    expected_return_pct: float = Field(default=8.0, ge=0, le=30)


def _value(row: dict, *names: str) -> str:
    normalized = {str(k).strip().lower(): str(v).strip() for k, v in row.items() if k}
    for name in names:
        if name in normalized and normalized[name]:
            return normalized[name]
    return ""


def _parse_amount(value: str) -> Decimal:
    cleaned = value.replace(",", "").replace("₹", "").replace("INR", "").strip()
    if cleaned.startswith("(") and cleaned.endswith(")"):
        cleaned = "-" + cleaned[1:-1]
    return Decimal(cleaned)


def _classify(description: str, amount: Decimal) -> tuple[str, str]:
    desc = description.lower()
    if amount > 0:
        return "income", "Income"
    categories = {
        "grocer": "Groceries", "swiggy": "Food & Dining", "zomato": "Food & Dining",
        "uber": "Transport", "ola": "Transport", "fuel": "Transport", "rent": "Housing",
        "electric": "Utilities", "mobile": "Utilities", "netflix": "Entertainment",
        "amazon": "Shopping", "pharmacy": "Health", "hospital": "Health",
    }
    return "expense", next((category for token, category in categories.items() if token in desc), "Uncategorized")


async def _refresh_spending_snapshot(user_id: str, db: AsyncSession) -> None:
    """Executes the PostgreSQL warehouse ETL stored procedure directly in the database engine."""
    await db.execute(text("CALL sp_refresh_monthly_spending_facts(:user_id)"), {"user_id": user_id})
    await db.commit()


@router.post("/imports/transactions")
async def import_transactions(
    file: UploadFile = File(...), user_id: str = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(400, "Upload a .csv bank or transaction export.")
    try:
        payload = (await file.read()).decode("utf-8-sig")
        rows = list(csv.DictReader(io.StringIO(payload)))
    except (UnicodeDecodeError, csv.Error) as exc:
        raise HTTPException(400, f"Could not read CSV: {exc}")
    if not rows:
        raise HTTPException(400, "The CSV has no transaction rows.")

    result = await db.execute(text("""
        INSERT INTO raw_data_imports (user_id, source_file_name, total_rows, status)
        VALUES (:user_id, :file_name, :total_rows, 'processing') RETURNING import_id
    """), {"user_id": user_id, "file_name": file.filename, "total_rows": len(rows)})
    import_id = result.scalar_one()
    accepted = rejected = duplicates = 0
    try:
        for number, row in enumerate(rows, start=2):
            await db.execute(text("""
                INSERT INTO stg_transaction_rows (import_id, row_number, raw_row)
                VALUES (:import_id, :row_number, CAST(:raw_row AS jsonb))
            """), {"import_id": import_id, "row_number": number, "raw_row": json.dumps(row)})
            try:
                raw_date = _value(row, "date", "transaction date", "transaction_date")
                transaction_date = date.fromisoformat(raw_date.replace("/", "-"))
                description = _value(row, "description", "narration", "merchant", "details")
                amount = _parse_amount(_value(row, "amount", "transaction amount", "debit/credit"))
                if not description or amount == 0:
                    raise ValueError("description and a non-zero amount are required")
                transaction_type, category = _classify(description, amount)
                fingerprint = hashlib.sha256(f"{user_id}|{transaction_date}|{description}|{amount}".encode()).hexdigest()
                inserted = await db.execute(text("""
                    INSERT INTO financial_transactions
                      (user_id, import_id, transaction_date, description, amount, transaction_type, category, fingerprint)
                    VALUES (:user_id, :import_id, :transaction_date, :description, :amount, :transaction_type, :category, :fingerprint)
                    ON CONFLICT (user_id, fingerprint) DO NOTHING
                    RETURNING transaction_id
                """), {"user_id": user_id, "import_id": import_id, "transaction_date": transaction_date,
                      "description": description, "amount": amount, "transaction_type": transaction_type,
                      "category": category, "fingerprint": fingerprint})
                if inserted.scalar_one_or_none() is None:
                    duplicates += 1
                else:
                    accepted += 1
            except (ValueError, InvalidOperation) as exc:
                rejected += 1
                await db.execute(text("""UPDATE stg_transaction_rows SET validation_error = :error
                    WHERE import_id = :import_id AND row_number = :row_number"""),
                    {"error": str(exc), "import_id": import_id, "row_number": number})
        await _refresh_spending_snapshot(user_id, db)
        await db.execute(text("""UPDATE raw_data_imports SET status = 'completed', accepted_rows = :accepted,
            rejected_rows = :rejected WHERE import_id = :import_id"""),
            {"accepted": accepted, "rejected": rejected, "import_id": import_id})
        await db.commit()
    except Exception:
        await db.rollback()
        raise HTTPException(500, "Import failed; no transaction data was saved.")
    return {"import_id": import_id, "accepted_rows": accepted, "rejected_rows": rejected,
            "duplicate_rows": duplicates, "message": "CSV landed, validated, and loaded into FinPulse analytics."}


@router.get("/imports")
async def list_imports(user_id: str = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(text("""SELECT import_id, source_file_name, status, total_rows, accepted_rows,
        rejected_rows, imported_at FROM raw_data_imports WHERE user_id = :user_id ORDER BY imported_at DESC"""), {"user_id": user_id})
    return result.mappings().all()


@router.post("/goals")
async def create_goal(goal: GoalCreate, user_id: str = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if goal.target_date <= date.today():
        raise HTTPException(400, "Target date must be in the future.")
    result = await db.execute(text("""INSERT INTO financial_goals
        (user_id, goal_name, target_amount, current_amount, target_date, expected_return_pct)
        VALUES (:user_id, :goal_name, :target_amount, :current_amount, :target_date, :expected_return_pct)
        RETURNING *"""), {"user_id": user_id, **goal.model_dump()})
    await db.commit()
    return result.mappings().one()


@router.get("/goals")
async def list_goals(user_id: str = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(text("SELECT * FROM financial_goals WHERE user_id = :user_id AND is_active ORDER BY target_date"), {"user_id": user_id})
    return result.mappings().all()


@router.get("/goals/{goal_id}/simulation")
async def simulate_goal(goal_id: int, user_id: str = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(text("SELECT * FROM financial_goals WHERE goal_id = :goal_id AND user_id = :user_id"), {"goal_id": goal_id, "user_id": user_id})
    goal = result.mappings().one_or_none()
    if not goal:
        raise HTTPException(404, "Goal not found.")
    months = max(1, (goal["target_date"].year - date.today().year) * 12 + goal["target_date"].month - date.today().month)
    monthly_rate = float(goal["expected_return_pct"]) / 1200
    future_value_of_current = float(goal["current_amount"]) * (1 + monthly_rate) ** months
    remaining = max(0, float(goal["target_amount"]) - future_value_of_current)
    monthly_needed = remaining / months if monthly_rate == 0 else remaining * monthly_rate / ((1 + monthly_rate) ** months - 1)
    return {
        "goal_id": goal_id,
        "goal_name": goal["goal_name"],
        "months_remaining": months,
        "target_amount": float(goal["target_amount"]),
        "current_amount": float(goal["current_amount"]),
        "projected_current_amount": round(future_value_of_current, 2),
        "monthly_investment_needed": round(monthly_needed, 2),
        "on_track": float(goal["current_amount"]) >= float(goal["target_amount"])
    }


@router.get("/health")
async def health_score(user_id: str = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(text("""
        WITH portfolio AS (SELECT asset_class_count, largest_allocation_pct FROM fact_monthly_portfolio_snapshots
            WHERE user_id = :user_id ORDER BY snapshot_month DESC LIMIT 1),
        spending AS (SELECT income_amount, expense_amount FROM fact_monthly_spending_snapshots
            WHERE user_id = :user_id ORDER BY snapshot_month DESC LIMIT 1),
        goals AS (SELECT COUNT(*) AS total, COUNT(*) FILTER (WHERE current_amount >= target_amount) AS complete
            FROM financial_goals WHERE user_id = :user_id AND is_active)
        SELECT COALESCE((SELECT asset_class_count FROM portfolio), 0) asset_classes,
               COALESCE((SELECT largest_allocation_pct FROM portfolio), 100) largest_allocation,
               COALESCE((SELECT income_amount FROM spending), 0) income,
               COALESCE((SELECT expense_amount FROM spending), 0) expenses,
               (SELECT total FROM goals) goal_count, (SELECT complete FROM goals) completed_goals
    """), {"user_id": user_id})
    row = result.mappings().one()
    savings_rate = max(0, (float(row["income"]) - float(row["expenses"])) / float(row["income"]) * 100) if row["income"] else 0
    diversification = min(30, int(row["asset_classes"]) * 8) + (10 if float(row["largest_allocation"]) <= 35 else 0)
    savings = min(30, round(savings_rate * 1.5))
    goal_score = 20 if not row["goal_count"] else round(20 * int(row["completed_goals"]) / int(row["goal_count"]))
    score = min(100, diversification + savings + goal_score + 10)
    return {"score": score, "band": "Strong" if score >= 75 else "Building" if score >= 50 else "Needs attention",
            "breakdown": {"diversification": diversification, "savings_habit": savings, "goal_progress": goal_score, "readiness": 10},
            "savings_rate_pct": round(savings_rate, 1)}


@router.get("/rebalancing")
async def rebalancing(user_id: str = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(text("""
        WITH active AS (SELECT portfolio_id, model_id, total_investment FROM user_portfolios WHERE user_id = :user_id AND is_active),
        current_alloc AS (SELECT i.asset_class_id, SUM(upp.allocation_percentage) current_pct FROM user_portfolio_positions upp
            JOIN instruments i ON i.instrument_id = upp.instrument_id JOIN active a ON a.portfolio_id = upp.portfolio_id GROUP BY i.asset_class_id)
        SELECT ac.name asset_class, pa.allocation_percentage target_pct, COALESCE(c.current_pct, 0) current_pct,
            ROUND((pa.allocation_percentage - COALESCE(c.current_pct, 0)) * a.total_investment / 100, 2) amount_to_adjust
        FROM active a JOIN portfolio_allocations pa ON pa.model_id = a.model_id JOIN asset_classes ac ON ac.asset_class_id = pa.asset_class_id
        LEFT JOIN current_alloc c ON c.asset_class_id = pa.asset_class_id
        WHERE ABS(pa.allocation_percentage - COALESCE(c.current_pct, 0)) >= 5 ORDER BY ABS(pa.allocation_percentage - COALESCE(c.current_pct, 0)) DESC
    """), {"user_id": user_id})
    return result.mappings().all()


@router.get("/alerts")
async def alerts(user_id: str = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    health = await health_score(user_id, db)
    alerts = []
    if health["savings_rate_pct"] < 20:
        alerts.append({"severity": "high", "title": "Low savings rate", "message": "Aim to save at least 20% of monthly income to improve resilience."})
    if health["breakdown"]["diversification"] < 25:
        alerts.append({"severity": "medium", "title": "Portfolio concentration", "message": "Add more asset-class diversification before increasing investment."})
    if not health["breakdown"]["goal_progress"]:
        alerts.append({"severity": "medium", "title": "No goal progress recorded", "message": "Create a target to turn your portfolio into an actionable plan."})
    return alerts
