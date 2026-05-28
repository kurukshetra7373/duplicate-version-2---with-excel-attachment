import streamlit as st
import pandas as pd
import json
import os
from datetime import date

st.set_page_config(
    page_title="Duplicate Destroyer",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── Persistent submission tracking ──
TRACKER_FILE = "submissions.json"

def load_tracker():
    today = str(date.today())
    if os.path.exists(TRACKER_FILE):
        with open(TRACKER_FILE, "r") as f:
            data = json.load(f)
        if data.get("today_date") != today:
            data["today_count"] = 0
            data["today_date"] = today
            for p in data.get("per_person", {}).values():
                p["today"] = 0
    else:
        data = {"total": 0, "today_count": 0, "today_date": today, "per_person": {}}
    if "per_person" not in data:
        data["per_person"] = {}
    return data

def save_tracker(data):
    with open(TRACKER_FILE, "w") as f:
        json.dump(data, f)

tracker = load_tracker()

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        color: #ffffff;
    }

    #MainMenu, footer, header { visibility: hidden; }

    .block-container {
        padding: 0 !important;
        max-width: 100% !important;
    }

    .stApp {
        background: linear-gradient(135deg, #1a1f6e 0%, #1e3a8a 45%, #2563eb 100%);
        min-height: 100vh;
    }

    /* ── DASHBOARD (LEFT) ── */
    .dashboard-panel {
        background: rgba(15, 25, 80, 0.6);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 18px;
        padding: 1.5rem;
        min-width: 260px;
        max-width: 280px;
        backdrop-filter: blur(10px);
    }
    .dashboard-title {
        font-size: 1.15rem;
        font-weight: 800;
        color: #ffffff;
        margin-bottom: 1rem;
    }
    .person-card {
        background: rgba(255,255,255,0.08);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 12px;
        padding: 0.85rem 1rem;
        margin-bottom: 0.7rem;
    }
    .person-card:last-child { margin-bottom: 0; }
    .person-name {
        font-size: 0.95rem;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 0.5rem;
    }
    .person-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 3px 0;
        font-size: 0.82rem;
        color: rgba(255,255,255,0.7);
    }
    .person-val {
        font-size: 1rem;
        font-weight: 700;
        color: #ffffff;
    }
    .person-divider {
        border: none;
        border-top: 1px solid rgba(255,255,255,0.1);
        margin: 4px 0;
    }
    .no-submissions {
        font-size: 0.8rem;
        color: rgba(255,255,255,0.5);
        text-align: center;
        padding: 1rem 0;
    }

    /* ── FORM CARD (RIGHT) ── */
    .form-title {
        font-size: 2rem;
        font-weight: 800;
        color: #ffffff;
        text-align: center;
        margin-bottom: 2rem;
    }

    /* ── Selectbox ── */
    div[data-testid="stSelectbox"] label {
        color: #ffffff !important;
        font-size: 0.88rem !important;
        font-weight: 600 !important;
    }
    div[data-testid="stSelectbox"] > div > div {
        background-color: rgba(30, 60, 150, 0.5) !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
        border-radius: 10px !important;
        color: #ffffff !important;
        font-size: 0.9rem !important;
    }
    div[data-testid="stSelectbox"] > div > div:focus-within {
        border-color: rgba(255,255,255,0.5) !important;
        box-shadow: 0 0 0 2px rgba(255,255,255,0.15) !important;
    }
    div[data-testid="stSelectbox"] svg { fill: rgba(255,255,255,0.7) !important; }

    /* ── Check Button ── */
    .stButton > button {
        width: 100%;
        background: #3b82f6;
        color: #ffffff;
        border: none;
        padding: 0.85rem 1.5rem;
        border-radius: 10px;
        font-size: 1rem;
        font-weight: 700;
        cursor: pointer;
        transition: all 0.2s;
        box-shadow: 0 4px 20px rgba(59,130,246,0.4);
        margin-top: 0.5rem;
    }
    .stButton > button:hover {
        background: #2563eb;
        box-shadow: 0 6px 28px rgba(59,130,246,0.55);
        transform: translateY(-1px);
    }

    /* ── Link Button ── */
    .stLinkButton > a {
        width: 100%;
        display: block;
        text-align: center;
        background: rgba(255,255,255,0.1);
        color: #ffffff !important;
        border: 1px solid rgba(255,255,255,0.3);
        padding: 0.85rem 1.5rem;
        border-radius: 10px;
        font-size: 1rem;
        font-weight: 700;
        text-decoration: none !important;
        transition: all 0.2s;
        margin-top: 0.5rem;
    }
    .stLinkButton > a:hover {
        background: rgba(255,255,255,0.18);
        border-color: rgba(255,255,255,0.5);
    }

    /* ── Alert ── */
    div[data-testid="stAlert"] {
        border-radius: 10px;
        font-size: 0.9rem;
        font-weight: 500;
        margin-top: 1rem;
    }

    /* ── Candidate History ── */
    .history-panel {
        background: rgba(15, 25, 80, 0.5);
        border: 1px solid rgba(255,255,255,0.12);
        border-radius: 14px;
        padding: 1.2rem 1.5rem;
        margin-top: 1.2rem;
        overflow-x: auto;
    }
    .history-title {
        font-size: 0.95rem;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 0.8rem;
        letter-spacing: 0.02em;
    }
    .history-count {
        font-size: 0.8rem;
        font-weight: 500;
        color: rgba(255,255,255,0.55);
        margin-left: 0.5rem;
    }
    .history-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 0.82rem;
        min-width: 800px;
    }
    .history-table th {
        background: rgba(59,130,246,0.3);
        color: rgba(255,255,255,0.85);
        font-weight: 600;
        padding: 0.5rem 0.75rem;
        text-align: left;
        border-bottom: 1px solid rgba(255,255,255,0.1);
        white-space: nowrap;
    }
    .history-table td {
        color: rgba(255,255,255,0.85);
        padding: 0.45rem 0.75rem;
        border-bottom: 1px solid rgba(255,255,255,0.06);
        vertical-align: middle;
        white-space: nowrap;
    }
    .history-table tr:last-child td { border-bottom: none; }
    .history-table tr:hover td { background: rgba(255,255,255,0.05); }
    .history-badge {
        display: inline-block;
        background: rgba(59,130,246,0.25);
        border: 1px solid rgba(59,130,246,0.4);
        border-radius: 6px;
        padding: 2px 8px;
        font-size: 0.78rem;
        color: #93c5fd;
    }
    .badge-green {
        background: rgba(34,197,94,0.2);
        border-color: rgba(34,197,94,0.4);
        color: #86efac;
    }
    .badge-red {
        background: rgba(239,68,68,0.2);
        border-color: rgba(239,68,68,0.4);
        color: #fca5a5;
    }
</style>
""", unsafe_allow_html=True)

# ── Load data ──
df_raw = pd.read_excel("aa.xlsx")
df = df_raw.copy()

DISPLAY_COLS = ["Date", "Submitted By", "Consultant Full Name", "Actual Owner",
                "open/closed", "Position/Role", "Location", "DL", "SSN", "H1B", "OPT"]

# Normalize key lookup columns
for col in ["Consultant Full Name", "Position/Role", "Location", "Actual Owner"]:
    if col in df.columns:
        df[col] = df[col].astype(str).str.lower().str.strip()

name_col   = "Consultant Full Name"
role_col   = "Position/Role"
loc_col    = "Location"
owner_col  = "Actual Owner"

name_list  = ["-- Select --"] + sorted(df[name_col].dropna().unique().tolist()) if name_col in df.columns else ["-- Select --"]
role_list  = ["-- Select --"] + sorted(df[role_col].dropna().unique().tolist()) if role_col in df.columns else ["-- Select --"]
loc_list   = ["-- Select --"] + sorted(df[loc_col].dropna().unique().tolist()) if loc_col in df.columns else ["-- Select --"]
owner_list = ["-- Select --"] + sorted(df[owner_col].dropna().unique().tolist()) if owner_col in df.columns else ["-- Select --"]

# ── Submission dashboard counts from "Submitted By" ──
submitted_by_col = "Submitted By" if "Submitted By" in df.columns else None
EXCLUDED_SUBMITTERS = {"prasanth"}

if submitted_by_col:
    df[submitted_by_col] = df[submitted_by_col].astype(str).str.strip()
    submission_counts = (
        df[submitted_by_col]
        .replace("nan", pd.NA)
        .dropna()
        .loc[lambda s: ~s.str.lower().isin(EXCLUDED_SUBMITTERS)]
        .value_counts()
        .to_dict()
    )
else:
    submission_counts = {}

today_counts = {k: v.get("today", 0) for k, v in tracker.get("per_person", {}).items()}

# ── Layout ──
left, right = st.columns([1, 2.8])

# ── LEFT: Dashboard ──
with left:
    person_cards_html = ""
    for pname, total in sorted(submission_counts.items(), key=lambda x: x[1], reverse=True):
        today_val = today_counts.get(pname.lower(), 0)
        person_cards_html += (
            f'<div class="person-card">'
            f'<div class="person-name">{pname}</div>'
            f'<div class="person-row"><span>Total</span><span class="person-val">{total}</span></div>'
            f'<hr class="person-divider">'
            f'<div class="person-row"><span>Today</span><span class="person-val">{today_val}</span></div>'
            f'</div>'
        )
    if not person_cards_html:
        person_cards_html = '<div class="no-submissions">No data yet.</div>'

    st.markdown(
        f'<div class="dashboard-panel"><div class="dashboard-title">Submission Dashboard</div>{person_cards_html}</div>',
        unsafe_allow_html=True
    )

# ── Session state ──
if "check_result" not in st.session_state:
    st.session_state.check_result = None
if "check_msg" not in st.session_state:
    st.session_state.check_msg = ""

# ── RIGHT: Form ──
with right:
    st.markdown('<div class="form-title">Duplicate Destroyer</div>', unsafe_allow_html=True)

    name  = st.selectbox("Select Consultant Full Name *", name_list)
    role  = st.selectbox("Select Position/Role", role_list)
    loc   = st.selectbox("Select Location", loc_list)
    owner = st.selectbox("Select Actual Owner", owner_list)

    b1, b2 = st.columns(2)
    with b1:
        check = st.button("Check Duplicate")
    with b2:
        st.link_button("📊 Open Master Sheet ↗", "https://docs.google.com/spreadsheets/d/1h-CNfX6IR4UziLkuVVZkwh2LFZtpczypO9yEOSSPUw4/preview")

    if check:
        if name == "-- Select --":
            st.session_state.check_result = "warning"
            st.session_state.check_msg = "⚠️  Please select a Consultant Name before checking."
        else:
            query = (df[name_col] == name)
            if role != "-- Select --" and role_col in df.columns:
                query &= (df[role_col] == role)
            if loc != "-- Select --" and loc_col in df.columns:
                query &= (df[loc_col] == loc)
            if owner != "-- Select --" and owner_col in df.columns:
                query &= (df[owner_col] == owner)

            match = df[query]
            if not match.empty:
                st.session_state.check_result = "error"
                st.session_state.check_msg = "⚠️  Duplicate found — this combination already exists. Do not submit."
            else:
                if name not in tracker["per_person"]:
                    tracker["per_person"][name] = {"total": 0, "today": 0}
                tracker["per_person"][name]["total"] += 1
                tracker["per_person"][name]["today"] += 1
                tracker["total"] += 1
                tracker["today_count"] += 1
                save_tracker(tracker)
                st.session_state.check_result = "success"
                st.session_state.check_msg = "✅  No duplicate found — safe to submit."
        st.rerun()

    if st.session_state.check_result == "warning":
        st.warning(st.session_state.check_msg)
    elif st.session_state.check_result == "error":
        st.error(st.session_state.check_msg)
    elif st.session_state.check_result == "success":
        st.success(st.session_state.check_msg)

    # ── Candidate History ──
    if name != "-- Select --" and name_col in df.columns:
        candidate_rows = df_raw[df[name_col] == name].copy()
        if not candidate_rows.empty:
            show_cols = [c for c in DISPLAY_COLS if c in candidate_rows.columns]
            rows_html = ""
            for _, row in candidate_rows[show_cols].iterrows():
                cells = ""
                for col in show_cols:
                    val = row[col]
                    if pd.isna(val) or str(val).lower() in ("nan", "none", ""):
                        val = "—"
                    else:
                        val = str(val)
                    if col == "open/closed":
                        badge_class = "badge-green" if val.lower() == "open" else "badge-red" if val.lower() == "closed" else "history-badge"
                        cells += f'<td><span class="history-badge {badge_class}">{val}</span></td>'
                    elif col in ("DL", "SSN", "H1B", "OPT"):
                        cells += f'<td><span class="history-badge">{val}</span></td>'
                    else:
                        cells += f"<td>{val}</td>"
                rows_html += f"<tr>{cells}</tr>"

            headers = "".join(f"<th>{c}</th>" for c in show_cols)
            st.markdown(
                f'<div class="history-panel">'
                f'<div class="history-title">Existing Submissions'
                f'<span class="history-count">{len(candidate_rows)} record(s)</span></div>'
                f'<table class="history-table"><thead><tr>{headers}</tr></thead>'
                f'<tbody>{rows_html}</tbody></table></div>',
                unsafe_allow_html=True
            )
