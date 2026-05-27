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

    /* ── FULL PAGE GRADIENT ── */
    .stApp {
        background: linear-gradient(135deg, #1a1f6e 0%, #1e3a8a 45%, #2563eb 100%);
        min-height: 100vh;
    }

    .page-wrapper {
        display: flex;
        gap: 1.5rem;
        padding: 2rem 2.5rem;
        min-height: 100vh;
        align-items: flex-start;
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
    .form-panel {
        flex: 1;
        background: rgba(15, 25, 80, 0.5);
        border: 1px solid rgba(255,255,255,0.12);
        border-radius: 18px;
        padding: 2.5rem 3rem;
        backdrop-filter: blur(10px);
    }
    .form-title {
        font-size: 2rem;
        font-weight: 800;
        color: #ffffff;
        text-align: center;
        margin-bottom: 2rem;
    }
    .field-label {
        font-size: 0.88rem;
        font-weight: 600;
        color: #ffffff;
        margin-bottom: 6px;
        display: block;
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
</style>
""", unsafe_allow_html=True)

# ── Load data ──
df = pd.read_excel("aa.xlsx")
df["Name"]        = df["Name"].astype(str).str.lower().str.strip()
df["Role"]        = df["Role"].astype(str).str.lower().str.strip()
df["Vendor Name"] = df["Vendor Name"].astype(str).str.lower().str.strip()
df["Client"]      = df["Client"].astype(str).str.lower().str.strip()

has_location = "Location" in df.columns
if has_location:
    df["Location"] = df["Location"].astype(str).str.lower().str.strip()
    location_list = ["-- Select --"] + sorted(df["Location"].dropna().unique().tolist())

name_list   = ["-- Select --"] + sorted(df["Name"].dropna().unique().tolist())
role_list   = ["-- Select --"] + sorted(df["Role"].dropna().unique().tolist())
vendor_list = ["-- Select --"] + sorted(df["Vendor Name"].dropna().unique().tolist())
client_list = ["-- Select --"] + sorted(df["Client"].dropna().unique().tolist())

# ── Count submissions from "Submitted By" column ──
submitted_by_col = None
for col in df.columns:
    if col.strip().lower().replace(" ", "") == "submittedby":
        submitted_by_col = col
        break

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

# Today's count per person from tracker
today_counts = {k: v.get("today", 0) for k, v in tracker.get("per_person", {}).items()}

# ── Layout: dashboard (left) + form (right) ──
left, right = st.columns([1, 2.8])

# ── LEFT: Submission Dashboard ──
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
        person_cards_html = '<div class="no-submissions">No data in Submitted By column yet.</div>'

    st.markdown(
        f'<div class="dashboard-panel"><div class="dashboard-title">Submission Dashboard</div>{person_cards_html}</div>',
        unsafe_allow_html=True
    )

# ── Session state for check result ──
if "check_result" not in st.session_state:
    st.session_state.check_result = None
if "check_msg" not in st.session_state:
    st.session_state.check_msg = ""

# ── RIGHT: Form ──
with right:
    st.markdown('<div class="form-panel"><div class="form-title">Duplicate Destroyer</div></div>', unsafe_allow_html=True)

    client = st.selectbox("Select Client", client_list)
    name   = st.selectbox("Select Name *", name_list)
    role   = st.selectbox("Select Role", role_list)
    vendor = st.selectbox("Select Vendor Name", vendor_list)

    if has_location:
        location = st.selectbox("Select Location", location_list)
    else:
        location = "-- Select --"
        st.selectbox("Select Location", ["-- Select --"])

    b1, b2 = st.columns(2)
    with b1:
        check = st.button("Check Duplicate")
    with b2:
        st.link_button("📊 Open Master Sheet ↗", "https://docs.google.com/spreadsheets/d/1h-CNfX6IR4UziLkuVVZkwh2LFZtpczypO9yEOSSPUw4/preview")

    if check:
        if name == "-- Select --":
            st.session_state.check_result = "warning"
            st.session_state.check_msg = "⚠️  Please select 'Name' before checking."
        else:
            query = (df["Name"] == name)
            if client != "-- Select --":
                query &= (df["Client"] == client)
            if role != "-- Select --":
                query &= (df["Role"] == role)
            if vendor != "-- Select --":
                query &= (df["Vendor Name"] == vendor)
            if has_location and location != "-- Select --":
                query &= (df["Location"] == location)

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
