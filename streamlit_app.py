
import streamlit as st
import pandas as pd
from pathlib import Path
import json
import tempfile, shutil, os, uuid
from datetime import datetime, date
from typing import Optional

# -----------------------------------------------------------
# DIRECTORIES
# -----------------------------------------------------------
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

PHOTO_DIR = DATA_DIR / "photo_proofs"
PHOTO_DIR.mkdir(exist_ok=True)

# -----------------------------------------------------------
# FILE PATHS
# -----------------------------------------------------------
PLAN_CSV = OUTPUT_DIR / "next_7day_mr_visit.csv"
METRICS_JSON = OUTPUT_DIR / "plan_metrics.json"
MAP_FILE = OUTPUT_DIR / "mr_travel_map.html"

PHYS_VISIT_CSV = DATA_DIR / "physician_visit_table.csv"
RCPA_CSV = DATA_DIR / "rcpa_chemist_table.csv"
MRS_CSV = DATA_DIR / "mr_reps.csv"

BACKUP_SUFFIX = ".bak.csv"

# -----------------------------------------------------------
# PAGE CONFIG
# -----------------------------------------------------------
st.set_page_config(page_title="Pharma SFA – Final MR Visit Plan", layout="wide")
st.title("Pharma Sales Force Automation — Final MR Visit Plan")

# -----------------------------------------------------------
# SAFE HELPERS
# -----------------------------------------------------------
def safe_write_df(df: pd.DataFrame, path: Path):
    """Backup + atomic write"""
    try:
        if path.exists():
            backup = path.with_suffix(path.suffix + BACKUP_SUFFIX)
            shutil.copy2(path, backup)
    except:
        pass
    with tempfile.NamedTemporaryFile(mode="w", delete=False, dir=str(path.parent), suffix=".tmp") as tmp:
        tmp_name = tmp.name
        df.to_csv(tmp_name, index=False)
    shutil.move(tmp_name, str(path))

def safe_append_row(path: Path, row: dict):
    if not path.exists():
        pd.DataFrame([row]).to_csv(path, index=False)
        return
    df = pd.read_csv(path)
    df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    safe_write_df(df, path)

def save_uploaded_file(uploaded_file, dest_dir: Path) -> Optional[str]:
    if not uploaded_file:
        return ""
    fname = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}_{uploaded_file.name}"
    dest = dest_dir / fname
    with open(dest, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return str(dest)

# -----------------------------------------------------------
# LOAD FINAL PLAN
# -----------------------------------------------------------
if not PLAN_CSV.exists():
    st.warning("Final plan not found. Run the notebook pipeline to generate output/next_7day_mr_visit.csv.")
    st.stop()

df = pd.read_csv(PLAN_CSV)

# MR name mapping fallback
if "mr_name" not in df.columns or df["mr_name"].isnull().all():
    if MRS_CSV.exists():
        mrs_df = pd.read_csv(MRS_CSV)
        mrs_map = dict(zip(mrs_df["mr_id"], mrs_df["mr_name"]))
        df["mr_name"] = df["assigned_mr"].map(mrs_map)
    else:
        df["mr_name"] = df["assigned_mr"]

# Ensure notes columns exist
for col in ["mr_notes", "mr_notes_updated_by", "mr_notes_updated_at"]:
    if col not in df.columns:
        df[col] = ""

# -----------------------------------------------------------
# KPI TILES
# -----------------------------------------------------------
col1, col2, col3, col4 = st.columns(4)
with col1: st.metric("Total visits", int(df.shape[0]))
with col2: st.metric("Unique doctors", int(df["doctor_id"].nunique()))
with col3: st.metric("Unique MRs", int(df["assigned_mr"].nunique()))
with col4: st.metric("High priority visits", int(df[df["segment"]=="High"].shape[0]) if "segment" in df.columns else 0)

st.markdown("---")

# -----------------------------------------------------------
# FILTER PANEL
# -----------------------------------------------------------
left, right = st.columns([2,5])

with left:
    seg = st.selectbox("Segment", ["All"] + sorted(df["segment"].dropna().unique()) if "segment" in df.columns else ["All"])
    therapy = st.selectbox("Therapy Area", ["All"] + sorted(df["therapy_area"].dropna().unique()) if "therapy_area" in df.columns else ["All"])
    mr = st.selectbox("MR", ["All"] + sorted(df["mr_name"].dropna().unique()))
    date_sel = st.selectbox("Date", ["All"] + sorted(df["scheduled_date"].dropna().unique()) if "scheduled_date" in df.columns else ["All"])
    search = st.text_input("Search doctor, molecule or notes")

with right:
    st.write("### Filtered Preview")

df_display = df.copy()
if seg != "All": df_display = df_display[df_display["segment"] == seg]
if therapy != "All": df_display = df_display[df_display["therapy_area"] == therapy]
if mr != "All": df_display = df_display[df_display["mr_name"] == mr]
if date_sel != "All": df_display = df_display[df_display["scheduled_date"] == date_sel]

if search:
    s = search.lower()
    cond = False
    for col in ["doctor_name", "molecules_list", "mr_notes"]:
        if col in df_display.columns:
            cond = cond | df_display[col].astype(str).str.lower().str.contains(s, na=False)
    df_display = df_display[cond]

st.dataframe(df_display.reset_index(drop=True), use_container_width=True)

st.markdown("---")

# -----------------------------------------------------------
# TRAVEL MAP
# -----------------------------------------------------------
import streamlit.components.v1 as components

st.write("### MR Travel Map")

if MAP_FILE.exists():
    try:
        html = MAP_FILE.read_text(encoding="utf-8")
        components.html(html, height=700, scrolling=True)
    except:
        st.info("Map exists but cannot be embedded. Open output/mr_travel_map.html manually.")
else:
    st.info("Map not found. Regenerate from notebook pipeline.")

st.markdown("---")

# -----------------------------------------------------------
# MR SUMMARY
# -----------------------------------------------------------
st.write("### MR-level Summary")
try:
    summary = df.groupby(["assigned_mr","mr_name"]).agg(
        num_visits=("doctor_id","count"),
        total_call_minutes=("call_duration_min","sum")
    ).reset_index()
    st.dataframe(summary, use_container_width=True)
except:
    st.info("Summary could not be computed.")

st.markdown("---")

# -----------------------------------------------------------
# MR NOTES EDITOR
# -----------------------------------------------------------
st.header("Edit MR Notes")

with st.expander("MR Notes Editor", expanded=False):
    df_live = pd.read_csv(PLAN_CSV)
    for col in ["mr_notes","mr_notes_updated_by","mr_notes_updated_at"]:
        if col not in df_live.columns:
            df_live[col] = ""

    pick_mode = st.radio("Select by", ["slot_id","MR name","Doctor name"])

    if pick_mode == "slot_id":
        key_val = st.selectbox("slot_id", [""] + df_live["slot_id"].astype(str).tolist())
        selected = df_live[df_live["slot_id"].astype(str) == key_val]
    elif pick_mode == "MR name":
        key_val = st.selectbox("MR", [""] + sorted(df_live["mr_name"].dropna().unique()))
        selected = df_live[df_live["mr_name"] == key_val]
    else:
        key_val = st.selectbox("Doctor", [""] + sorted(df_live["doctor_name"].dropna().unique()))
        selected = df_live[df_live["doctor_name"] == key_val]

    if selected.empty:
        st.info("Nothing selected.")
    else:
        st.dataframe(selected, use_container_width=True)
        sel_slot = st.selectbox("Select slot", selected["slot_id"].astype(str).tolist())
        idx = df_live.index[df_live["slot_id"].astype(str) == sel_slot].tolist()[0]

        new_note = st.text_area("MR Note", df_live.at[idx,"mr_notes"])
        updated_by = st.text_input("Updated by", "")

        if st.button("Save Note"):
            df_live.at[idx,"mr_notes"] = new_note
            df_live.at[idx,"mr_notes_updated_by"] = updated_by
            df_live.at[idx,"mr_notes_updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            safe_write_df(df_live, PLAN_CSV)
            st.success("Saved.")
            st.experimental_rerun()

st.markdown("---")

# -----------------------------------------------------------
# PHYSICIAN VISIT FORM
# -----------------------------------------------------------
st.header("Log Physician Visit")

with st.expander("Physician Visit Form", expanded=False):
    doctors = pd.read_csv(DATA_DIR/"doctors_master.csv") if (DATA_DIR/"doctors_master.csv").exists() else pd.DataFrame()
    mrs = pd.read_csv(MRS_CSV) if MRS_CSV.exists() else pd.DataFrame()

    mr_list = mrs["mr_id"].tolist() if not mrs.empty else []
    doc_list = doctors["doctor_id"].tolist() if not doctors.empty else []

    with st.form("visit_form"):
        mr_id = st.selectbox("MR", mr_list)
        doctor_id = st.selectbox("Doctor", doc_list)
        visit_date = st.date_input("Visit Date", value=date.today())
        visit_time = st.time_input("Time")
        visit_mode = st.selectbox("Mode", ["In-person","Online","Tele-call"])
        product = st.text_input("Products detailed")
        call_duration = st.number_input("Call duration (min)", min_value=1, value=10)
        notes = st.text_area("Core message")
        photo = st.file_uploader("Photo (optional)", type=["jpg","jpeg","png"])
        submit_visit = st.form_submit_button("Save Visit")

        if submit_visit:
            visit_id = f"V{uuid.uuid4().hex[:8]}"
            photo_path = save_uploaded_file(photo, PHOTO_DIR)

            new_row = {
                "visit_id": visit_id,
                "mr_id": mr_id,
                "doctor_id": doctor_id,
                "visit_date": visit_date.strftime("%Y-%m-%d"),
                "visit_time": visit_time.strftime("%H:%M"),
                "visit_mode": visit_mode,
                "product_detailed": product,
                "call_duration_min": call_duration,
                "core_message_shared": notes,
                "photo_proof_url": photo_path
            }

            safe_append_row(PHYS_VISIT_CSV, new_row)
            st.success(f"Saved visit {visit_id}")

st.markdown("---")

# -----------------------------------------------------------
# RCPA FORM
# -----------------------------------------------------------
st.header("Log RCPA / Chemist Snapshot")

with st.expander("RCPA Form", expanded=False):
    with st.form("rcpa_form"):
        mr_id = st.selectbox("MR", mr_list)
        rcpa_date = st.date_input("RCPA Date", value=date.today())
        chemist_name = st.text_input("Chemist name")
        brand = st.text_input("Brand tracked")
        comp_brand = st.text_input("Competitor brand")
        units = st.number_input("Weekly demand units", min_value=0, value=0)
        remarks = st.text_area("Remarks")
        photo = st.file_uploader("Photo (optional)", type=["jpg","jpeg","png"])
        submit_rcpa = st.form_submit_button("Save RCPA")

        if submit_rcpa:
            rcpa_id = f"R{uuid.uuid4().hex[:8]}"
            photo_path = save_uploaded_file(photo, PHOTO_DIR)
            new_rcpa = {
                "rcpa_id": rcpa_id,
                "mr_id": mr_id,
                "visit_date": rcpa_date.strftime("%Y-%m-%d"),
                "chemist_name": chemist_name,
                "your_brand_name": brand,
                "comp_brand_name": comp_brand,
                "weekly_demand_units": units,
                "remarks": remarks,
                "photo_proof_url": photo_path
            }
            safe_append_row(RCPA_CSV, new_rcpa)
            st.success(f"Saved RCPA {rcpa_id}")

st.markdown("---")
st.write("Backups are auto-created. For multi-user usage, migrate to SQLite/Postgres.")
