import pandas as pd
import streamlit as st
import json

from utils.api import (
    get_imports, 
    import_transactions, 
    trigger_market_crawl, 
    get_raw_market_lake, 
    get_latest_market_prices, 
    get_partition_telemetry
)
from utils.auth import require_auth
from utils.ui import apply_page_style, render_sidebar_brand

st.set_page_config(page_title="Data Hub & Lakehouse — Vertex", page_icon="🏛️", layout="wide")
require_auth()
apply_page_style()
render_sidebar_brand()

# Header Banner
st.markdown("""
    <div style="margin-bottom: 24px;">
        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 6px;">
            <span class="badge-chip badge-info">MEDALLION ARCHITECTURE</span>
            <span class="badge-chip badge-success">🟢 HYBRID MULTI-MODEL STORAGE</span>
        </div>
        <h1 style="font-size: 2.2rem; margin-bottom: 4px;">
            <span class="vertex-gradient-text">Unified Lakehouse</span> & Ingestion Data Hub
        </h1>
        <p style="color: #475569; font-size: 0.95rem; margin: 0;">
            Bronze Semi-Structured JSONB Lake • Silver Declarative Partitioned Store • Gold OLAP Materialized Analytics
        </p>
    </div>
""", unsafe_allow_html=True)

# 3-Tier Visual Architecture Cards
st.markdown("""
    <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; margin-bottom: 24px;">
        <div class="vertex-card" style="padding: 18px; margin-bottom: 0; border-top: 3px solid #B45309;">
            <div style="font-size: 0.75rem; color: #B45309; font-weight: 700; text-transform: uppercase;">1. BRONZE TIER</div>
            <div style="font-size: 1.1rem; font-weight: 700; color: #0F172A; margin: 4px 0;">Semi-Structured Lake</div>
            <div style="font-size: 0.82rem; color: #475569;">raw_market_scrapes & staging rows stored as JSONB with GIN path indexing.</div>
        </div>
        <div class="vertex-card" style="padding: 18px; margin-bottom: 0; border-top: 3px solid #64748B;">
            <div style="font-size: 0.75rem; color: #475569; font-weight: 700; text-transform: uppercase;">2. SILVER TIER</div>
            <div style="font-size: 1.1rem; font-weight: 700; color: #0F172A; margin: 4px 0;">Partitioned Store</div>
            <div style="font-size: 0.82rem; color: #475569;">market_price_history partitioned by date range (2025, 2026, future) + BRIN.</div>
        </div>
        <div class="vertex-card" style="padding: 18px; margin-bottom: 0; border-top: 3px solid #D97706;">
            <div style="font-size: 0.75rem; color: #D97706; font-weight: 700; text-transform: uppercase;">3. GOLD TIER</div>
            <div style="font-size: 1.1rem; font-weight: 700; color: #0F172A; margin: 4px 0;">OLAP Materialized Views</div>
            <div style="font-size: 0.82rem; color: #475569;">mv_instrument_performance_metrics refreshed concurrently inside PostgreSQL.</div>
        </div>
    </div>
""", unsafe_allow_html=True)

tab_market, tab_transactions = st.tabs(["🕷️ Scrapling Market Lakehouse & Telemetry", "🗂️ Bank Statements ETL Ingestion"])

# =============================================================================
# TAB 1: SCRAPLING MARKET LAKEHOUSE & PARTITIONS
# =============================================================================
with tab_market:
    st.markdown("""
        <div class="vertex-card" style="padding: 20px 24px; margin-bottom: 20px;">
            <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 12px;">
                <div>
                    <h3 style="font-size: 1.2rem; margin-bottom: 4px;">Automated Market Ingestion Engine (Scrapling)</h3>
                    <p style="color: #475569; font-size: 0.88rem; margin: 0; max-width: 700px;">
                        Deploys stealth TLS impersonation (JA3/JA4 browser fingerprints) to bypass Cloudflare Turnstile on AMFI India NAVs and NSE ETF quotes.
                    </p>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    col_btn, col_blank = st.columns([1, 2])
    with col_btn:
        if st.button("🚀 Trigger Live Crawl & Ingest", type="primary", use_container_width=True):
            with st.spinner("Scrapling is bypassing anti-bot checks and ingesting feeds..."):
                res = trigger_market_crawl()
                if res.status_code == 200:
                    data = res.json()
                    st.success(data.get("message", "Ingestion completed successfully!"))
                    st.toast("Data Lake & Partitioned Warehouse Updated!", icon="✅")
                    st.rerun()
                else:
                    st.error(f"Ingestion failed: {res.text}")

    # Fetch Partition Telemetry
    telem_res = get_partition_telemetry()
    if telem_res.status_code == 200:
        telem_data = telem_res.json()
        bronze_count = telem_data.get("bronze_lake_rows", 0)
        partitions = telem_data.get("partitions", [])

        # Display Top KPI Metrics
        m1, m2, m3, m4 = st.columns(4)
        p25_rows = next((p["exact_rows"] for p in partitions if p["partition_name"] == "market_price_history_2025"), 0)
        p26_rows = next((p["exact_rows"] for p in partitions if p["partition_name"] == "market_price_history_2026"), 0)

        with m1:
            st.markdown(f"""
                <div class="vertex-card" style="padding: 16px;">
                    <div class="vertex-metric-label">Bronze Lake Payload</div>
                    <div class="vertex-metric-val">{bronze_count}</div>
                    <div style="font-size: 0.75rem; color: #B45309; font-weight: 500; margin-top: 2px;">JSONB Raw Scrapes</div>
                </div>
            """, unsafe_allow_html=True)

        with m2:
            st.markdown(f"""
                <div class="vertex-card" style="padding: 16px;">
                    <div class="vertex-metric-label">2025 Partition</div>
                    <div class="vertex-metric-val">{p25_rows:,}</div>
                    <div style="font-size: 0.75rem; color: #64748B; margin-top: 2px;">Historical Base Rows</div>
                </div>
            """, unsafe_allow_html=True)

        with m3:
            st.markdown(f"""
                <div class="vertex-card" style="padding: 16px;">
                    <div class="vertex-metric-label">2026 Partition</div>
                    <div class="vertex-metric-val" style="color: #15803D;">{p26_rows:,}</div>
                    <div style="font-size: 0.75rem; color: #15803D; margin-top: 2px;">Live Scraped Rows</div>
                </div>
            """, unsafe_allow_html=True)

        with m4:
            st.markdown("""
                <div class="vertex-card" style="padding: 16px;">
                    <div class="vertex-metric-label">Anti-Bot Status</div>
                    <div style="margin: 6px 0 4px 0;"><span class="badge-chip badge-success">STEALTH TLS ACTIVE</span></div>
                    <div style="font-size: 0.75rem; color: #64748B;">HTTP/2 WAF Bypass</div>
                </div>
            """, unsafe_allow_html=True)

        # Database Partition Storage Inspector
        st.markdown("<h3 style='margin-top: 20px; font-size: 1.25rem;'>Physical Table Partition Catalog (Silver Tier)</h3>", unsafe_allow_html=True)
        st.caption("PostgreSQL declarative range partitioning (`PARTITION BY RANGE (price_date)`). Chronological queries leverage partition pruning to skip unneeded years.")
        
        part_df = pd.DataFrame([
            {
                "Physical Partition": p["partition_name"],
                "Storage Footprint": p["total_size"],
                "Exact Tuple Count": p["exact_rows"]
            }
            for p in partitions if not p["partition_name"].endswith("_pkey") and not p["partition_name"].endswith("_idx")
        ])
        st.dataframe(part_df, use_container_width=True, hide_index=True)

    # Bronze Data Lake Inspector
    st.markdown("<h3 style='margin-top: 24px; font-size: 1.25rem;'>Bronze Data Lake Inspector (`raw_market_scrapes`)</h3>", unsafe_allow_html=True)
    st.caption("Raw semi-structured JSONB documents indexed via GIN (`jsonb_path_ops`). Demonstrates NoSQL capability in PostgreSQL.")
    
    lake_res = get_raw_market_lake(limit=10)
    if lake_res.status_code == 200 and lake_res.json():
        lake_items = lake_res.json()
        summary_rows = []
        for item in lake_items:
            summary_rows.append({
                "Scrape ID": item["scrape_id"],
                "Source Feed": item["source_feed"],
                "Ticker / Scheme": item["ticker_or_scheme"],
                "HTTP Status": item["http_status"],
                "Scraped At": item["scraped_at"]
            })
        st.dataframe(pd.DataFrame(summary_rows), use_container_width=True, hide_index=True)

        with st.expander("🔍 Inspect Sample Raw JSONB Payload from Data Lake"):
            st.json(lake_items[0]["raw_payload"])
    else:
        st.info("No raw lake scrapes found. Click 'Trigger Live Crawl & Ingest' above to fetch data.")

    # Gold Tier Materialized View Analytics
    st.markdown("<h3 style='margin-top: 24px; font-size: 1.25rem;'>Gold Tier Analytics (`mv_instrument_performance_metrics`)</h3>", unsafe_allow_html=True)
    st.caption("Pre-aggregated materialized view refreshed concurrently directly inside PostgreSQL.")
    
    prices_res = get_latest_market_prices()
    if prices_res.status_code == 200 and prices_res.json():
        prices_df = pd.DataFrame(prices_res.json())
        display_df = prices_df[[
            "asset_class", "instrument_name", "ticker", "instrument_type", 
            "latest_price", "avg_historical_price", "price_volatility_stddev", "latest_date"
        ]].rename(columns={
            "asset_class": "Asset Class",
            "instrument_name": "Instrument",
            "ticker": "Ticker",
            "instrument_type": "Type",
            "latest_price": "Latest Price / NAV (₹)",
            "avg_historical_price": "Avg Price (₹)",
            "price_volatility_stddev": "Volatility (StdDev)",
            "latest_date": "Latest As Of"
        })
        st.dataframe(display_df, use_container_width=True, hide_index=True)

# =============================================================================
# TAB 2: BANK TRANSACTIONS ETL
# =============================================================================
with tab_transactions:
    st.markdown("""
        <div class="vertex-card" style="padding: 20px 24px; margin-bottom: 20px;">
            <h3 style="font-size: 1.2rem; margin-bottom: 4px;">Personal Financial Transactions Ingestion</h3>
            <p style="color: #475569; font-size: 0.88rem; margin: 0;">
                Upload bank or credit card statements. Vertex stages raw rows in Bronze, deduplicates via SHA-256 digital fingerprints into Silver, and triggers PL/pgSQL fact updates into Gold.
            </p>
        </div>
    """, unsafe_allow_html=True)

    with st.expander("Supported CSV Format Guidelines"):
        st.code("date,description,amount\n2026-09-01,Salary,95000\n2026-09-02,Swiggy,-420")
        st.write("Accepted aliases: `transaction date`, `narration`, `merchant`, and `details`. Positive amounts are income; negative amounts are expenses.")

    uploaded = st.file_uploader("Upload Bank Statement (CSV)", type=["csv"], key="bank_csv_uploader")
    if uploaded and st.button("⚡ Process & Load Transactions", type="primary"):
        with st.spinner("Landing in Bronze, deduplicating, and triggering warehouse refresh..."):
            response = import_transactions(uploaded)
        if response.status_code == 200:
            data = response.json()
            st.success(data["message"])
            a, b, c = st.columns(3)
            with a:
                st.metric("Loaded into Silver", data["accepted_rows"])
            with b:
                st.metric("Rejected / Invalid", data["rejected_rows"])
            with c:
                st.metric("Duplicates Skipped (SHA-256)", data["duplicate_rows"])
        else:
            st.error(response.text)

    imports = get_imports()
    st.markdown("<h3 style='margin-top: 24px; font-size: 1.25rem;'>Transaction Ingestion Batches (`raw_data_imports`)</h3>", unsafe_allow_html=True)
    if imports.status_code == 200 and imports.json():
        st.dataframe(pd.DataFrame(imports.json()), use_container_width=True, hide_index=True)
    else:
        st.info("No transaction batches imported yet.")
