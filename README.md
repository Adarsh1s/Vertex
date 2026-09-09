# 💓 FinPulse — Personal Investment Intelligence & Analytics

A modern, full-stack financial intelligence platform that calculates risk-profiled investment portfolios, processes real transaction data through an automated ETL pipeline, and provides financial goal simulations, health scores, and rebalancing alerts.

**Tech Stack:** PostgreSQL (Neon Serverless) · FastAPI · SQLAlchemy (Async) · Streamlit · Docker

---

## 🌟 FinPulse Capabilities

- **Personalized Portfolio Engine:** Risk-based portfolio allocations tailored for Indian markets (Conservative, Moderate, Aggressive), complete with asset class and instrument-level breakdowns, expected return models (1Y/3Y/5Y), and versioned ACID generation.
- **Transaction ETL & Personal Data Lake:** Ingestion pipeline for bank/credit CSV statements. Staged for full auditability, validated against schemas, de-duplicated using SHA-256 fingerprints, and auto-classified into semantic categories.
- **Analytics Data Warehouse (Star Schema):** Pre-aggregated monthly spending and net worth fact snapshots (`fact_monthly_spending_snapshots`, `fact_monthly_portfolio_snapshots`) against a time dimension (`dim_month`) for high-speed sub-millisecond analytics.
- **Financial Goals & Health Scoring:** Target planning with geometric return projections to determine required monthly SIPs; composite health score (0–100) assessing savings rates, portfolio diversification, and runway.
- **Dynamic Rebalancing & Alerts:** Automated drift detection alerting users when asset allocation drifts by $\ge 5\%$ points or savings fall below safety thresholds.

---

## 🏗️ System Architecture

```
┌───────────────────────────┐           Bearer JWT           ┌────────────────────────────┐
│   Streamlit Web UI        │ ─────────────────────────────► │   FastAPI Backend Server   │
│   (Port 8501)             │ ◄───────────────────────────── │   (Port 8000)              │
└───────────────────────────┘             JSON               └──────────────┬─────────────┘
                                                                            │
                                                                 AsyncPG / SQL Queries
                                                                 (Over WSS Port 443 or 5432)
                                                                            │
                                                                            ▼
                                                             ┌────────────────────────────┐
                                                             │   Neon PostgreSQL Cloud    │
                                                             │   • App Tables (OLTP)      │
                                                             │   • Staging Lake (JSONB)   │
                                                             │   • Star Schema Warehouse  │
                                                             └────────────────────────────┘
```

### Key Architectural Highlights
1. **Self-Contained FastAPI Auth:** Uses secure PBKDF2-SHA256 password hashing and standard HS256 JWT tokens stored in the database's `app_users` table. Fast, reliable, and completely eliminates third-party auth service downtime and cookie restrictions.
2. **Port 443 Transparent WebSocket Proxy:** Consumer Wi-Fi and corporate firewalls frequently drop outbound TCP port 5432. FinPulse includes a built-in transparent tunnel (`neon_proxy.py`) that encapsulates PostgreSQL wire protocol over Neon's TLS WebSocket endpoint (`wss://.../v2` on standard port 443).
3. **Multi-Stage Data Pipeline:** Staged landing (`raw_data_imports` + `stg_transaction_rows`) $\to$ Cleaned transaction store (`financial_transactions`) $\to$ Analytical facts (`fact_monthly_spending_snapshots`).

---

## 📁 Project Structure

```
DBMS_PROJECT/
├── docker-compose.yml              ← Multi-container orchestration (Backend + Frontend)
├── .gitignore                      ← Ignores secrets (.env, secrets.toml), caches, and logs
├── db_schema.dbml                  ← DBML representation of database design
├── exam_queries.sql                ← Sample analytical & demonstration queries
├── backend/
│   ├── Dockerfile
│   ├── .env.example                ← Template for DB credentials
│   ├── requirements.txt
│   ├── app/
│   │   ├── main.py                 ← FastAPI entry point & CORS configuration
│   │   ├── core/
│   │   │   ├── config.py           ← Pydantic settings & DB URL parser
│   │   │   ├── database.py         ← Async SQLAlchemy engine & session maker
│   │   │   ├── neon_proxy.py       ← Local WSS-to-TCP proxy for port 443 bypass
│   │   │   └── security.py         ← JWT bearer verification & token extraction
│   │   ├── models/                 ← SQLAlchemy ORM models (users, portfolios, etc.)
│   │   ├── schemas/                ← Pydantic v2 request/response schemas
│   │   ├── routers/
│   │   │   ├── auth.py             ← Sign-up, Sign-in, and Current User profile
│   │   │   ├── profile.py          ← Financial onboarding profile
│   │   │   ├── questionnaire.py    ← 7-question risk assessment logic
│   │   │   ├── portfolio.py        ← Portfolio generation, history, and comparison
│   │   │   ├── finpulse.py         ← ETL data hub, spending snapshots, goals & alerts
│   │   │   └── reference.py        ← Seed data lookup (instruments, models, asset classes)
│   │   └── services/
│   │       ├── portfolio_engine.py ← ACID transaction portfolio generator
│   │       └── risk_engine.py      ← Score calculation & profile classifier
│   └── sql/
│       ├── schema.sql              ← Core relational schema DDL
│       ├── views.sql               ← Multi-table reporting views (user_portfolio_summary)
│       ├── triggers_functions.sql  ← Audit logging trigger + risk profile calculator
│       ├── seed.sql                ← ~230 rows of market reference data & instruments
│       ├── finpulse_upgrade.sql    ← ETL staging lake, warehouse facts, dimensions, and goals
│       └── local_auth_upgrade.sql  ← Direct app_users table & view upgrades
└── frontend/
    ├── Dockerfile
    ├── app.py                      ← Main landing page (Sign in / Sign up)
    ├── pages/
    │   ├── 1_Onboarding.py         ← Income, investment horizon & financial profile
    │   ├── 2_Questionnaire.py      ← 7-question risk MCQ assessment
    │   ├── 3_Dashboard.py          ← Asset allocation pie chart, positions, and rebalancing
    │   ├── 4_History.py            ← Versioned portfolio change history
    │   ├── 5_Compare.py            ← What-if risk model comparison
    │   ├── 6_Profile.py            ← User profile management & password reset
    │   ├── 7_Data_Hub.py           ← Transaction CSV ETL upload & Data Lake inspector
    │   └── 8_Goals_Health.py       ← Financial health score & goal simulations
    └── utils/
        ├── auth.py                 ← Authentication helper (session state & token storage)
        ├── api.py                  ← FastAPI REST client with auto-URL detection
        └── charts.py               ← Interactive Plotly visualizations
```

---

## 🗄️ Database Schema & Data Architecture

The database implements **OLTP operational tables**, an **audit trail**, a **data lake**, and a **star-schema analytical data warehouse**:

| Category | Table / View | Description |
|---|---|---|
| **Identity & Users** | `app_users` | Primary user store (ID, email, PBKDF2 hashed password, timestamps) |
| **Operational (OLTP)** | `user_profiles` | User financial parameters (income, investment amount, horizon, risk profile) |
| | `risk_profiles` | Conservative, Moderate, Aggressive definitions |
| | `asset_classes` | Equity, Debt, Gold, Cash, International |
| | `portfolio_models` | Asset allocation templates mapped to risk profiles |
| | `portfolio_allocations` | Asset class target weights per portfolio model |
| | `instruments` | 14 real Indian market instruments (Nifty 50, Gold ETF, Liquid Funds, etc.) |
| | `instrument_allocations` | Target weights per instrument within models |
| | `instrument_returns` | Historical/expected 1Y, 3Y, 5Y return rates |
| | `user_portfolios` | Versioned portfolio instances per user (`is_active` flag + version number) |
| | `user_portfolio_positions` | Detailed allocations (quantities, weights, amounts in ₹) |
| **Data Lake & Staging** | `raw_data_imports` | Immutable metadata log of uploaded CSV batches and ETL statuses |
| | `stg_transaction_rows` | Landing staging table storing raw rows as `JSONB` with validation notes |
| **Trusted Store** | `financial_transactions` | Cleaned, de-duplicated (SHA-256 fingerprint), categorized personal transactions |
| **Data Warehouse** | `dim_month` | Time/calendar dimension pre-populated across 10 years for OLAP queries |
| | `fact_monthly_spending_snapshots` | Aggregated monthly income, expenses, savings, and transaction frequency |
| | `fact_monthly_portfolio_snapshots` | Monthly net worth, diversification index, and primary asset class % |
| | `financial_goals` | User target goals (target amount, target date, required monthly SIP) |
| **Auditing & Views** | `audit_log` | Trigger-generated audit record on every portfolio creation or modification |
| | `user_portfolio_summary` | Denormalized 7-table view consumed by the dashboard for instant display |

---

## 🚀 Quick Start (Docker)

### 1. Clone & Setup Environment

```bash
git clone <your-repo-url>
cd DBMS_PROJECT
cp backend/.env.example backend/.env
```

### 2. Configure Neon Database Connection

Open `backend/.env` and paste your Neon PostgreSQL connection string:
```env
DATABASE_URL=postgresql+asyncpg://<username>:<password>@<neon-host>/FinPulse?sslmode=require
```

### 3. Initialize Database Tables

Run the SQL migration scripts in your Neon SQL Editor or via `psql` in this exact order:
1. `backend/sql/schema.sql`
2. `backend/sql/views.sql`
3. `backend/sql/triggers_functions.sql`
4. `backend/sql/seed.sql`
5. `backend/sql/finpulse_upgrade.sql`
6. `backend/sql/local_auth_upgrade.sql`

### 4. Build & Start Services

```bash
docker compose up --build
```

Access the applications:
- **Streamlit Web Application:** [http://localhost:8501](http://localhost:8501)
- **FastAPI Interactive Docs (Swagger):** [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🔄 User Journey & Workflow

```
1. Sign Up / Sign In
   └── Uses secure local PBKDF2 authentication in Neon DB
2. Onboarding (1_Onboarding.py)
   └── Captures monthly income, total investment amount, and horizon
3. Risk Questionnaire (2_Questionnaire.py)
   └── 7 scenario MCQs → Database function maps score to Risk Profile
4. Dashboard (3_Dashboard.py)
   └── ACID portfolio generation → Allocation Pie Chart + Positions + Returns
5. Data Hub ETL (7_Data_Hub.py)
   └── Upload Bank CSV → Raw staging (Data Lake) → Sanitized ledger → Star Schema refresh
6. Goals & Health (8_Goals_Health.py)
   └── Financial health score (0-100), savings gap analysis & goal simulator
```

---

## 🔌 API Reference Highlights

| Endpoint | Method | Description |
|---|---|---|
| `/auth/sign-up` | `POST` | Register new user account with hashed password |
| `/auth/sign-in` | `POST` | Authenticate and issue Bearer JWT token |
| `/auth/me` | `GET` | Retrieve authenticated user identity |
| `/profile/create` | `POST` | Save initial financial onboarding profile |
| `/questionnaire/submit` | `POST` | Compute risk score and assign risk model |
| `/portfolio/generate` | `POST` | ACID transaction: deactivate old $\to$ generate new portfolio |
| `/portfolio/current` | `GET` | Active portfolio positions and allocation breakdown |
| `/finpulse/import-transactions` | `POST` | Multipart CSV ETL ingestion into Data Lake |
| `/finpulse/spending-summary` | `GET` | Monthly analytics from warehouse fact table |
| `/finpulse/health-score` | `GET` | Composite 4-factor financial health score |
| `/finpulse/goals` | `POST` / `GET` | Create and track personal investment goals |

---

## 🛡️ Key Design Decisions

| Decision | Rationale |
|---|---|
| **Direct DB Auth over Third-Party Auth** | Eliminates external latency, CORS errors, and service limits; self-contained within the project database. |
| **WSS Port 443 Fallback Tunnel** | Transparently circumvents ISP-level blocking of standard PostgreSQL port 5432 on residential networks. |
| **Multi-Tiered Data Architecture** | Separates unvalidated raw ingestion (Data Lake) from transactional consistency (OLTP) and fast analytical queries (Warehouse facts). |
| **ACID Portfolio Versioning** | Every generation deactivates prior models without data loss; historical performance can be audited and compared anytime. |
| **Database-Level Enforced Triggers** | `trg_audit_portfolio` ensures comprehensive audit logs even if application-level logging fails. |
