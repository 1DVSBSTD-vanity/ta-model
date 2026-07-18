import streamlit as st
import pandas as pd
import math

# Page Configurations
st.set_page_config(page_title="Human Capital Forecasting Engine", layout="wide")

st.title("Fireworks AI: Human Capital Sourcing & Capacity Engine")
st.markdown("### Structural Scale Modeling: 200 to 600 Total Employees")

# Sidebar - Model Control Panel Input Blocks
st.sidebar.header("1. Core Scale Metrics")
base_hc = st.sidebar.number_input("Initial Headcount (TTM Base)", value=200)
target_hc = st.sidebar.number_input("Target Ending Headcount", value=600)
attrition_rate = st.sidebar.slider("Annual TTM Attrition Rate (%)", 0.0, 25.0, 10.0) / 100

st.sidebar.header("2. Departmental Allocation (%)")
tech_pct = st.sidebar.slider("Tech / Infrastructure Allocation", 0, 100, 65) / 100
gtm_pct = st.sidebar.slider("GTM Allocation", 0, 100, 25) / 100
ga_pct = 1.0 - (tech_pct + gtm_pct)
st.sidebar.text(f"G&A Allocation (Auto-Calculated): {round(ga_pct*100,1)}%")

st.sidebar.header("3. Offer Acceptance Metrics")
accept_tech = st.sidebar.slider("Bay Area Tech Acceptance Rate (%)", 40, 100, 65) / 100
accept_gtm = st.sidebar.slider("Global GTM Average Acceptance Rate (%)", 50, 100, 85) / 100
accept_ga = st.sidebar.slider("G&A Acceptance Rate (%)", 50, 100, 90) / 100

st.sidebar.header("4. Recruiter Production (Offers / Quarter)")
quota_tech = st.sidebar.number_input("Tech Recruiter Quota", value=8)
quota_gtm = st.sidebar.number_input("GTM Recruiter Quota", value=12)
quota_ga = st.sidebar.number_input("G&A Recruiter Quota", value=15)

st.sidebar.header("5. Team Span Ratios")
manager_ratio = st.sidebar.number_input("ICs per Recruiting Manager", value=9)

# Engine Calculations: The Quarterly Waterfall
net_growth_per_quarter = (target_hc - base_hc) / 4

q_data = []
current_hc = base_hc

for q in range(1, 5):
    q_attrition = current_hc * (attrition_rate / 4)
    q_hires_needed = net_growth_per_quarter + q_attrition
    ending_hc = current_hc + net_growth_per_quarter
    
    q_data.append({
        "Quarter": f"Q{q}",
        "Starting Headcount (TTM)": int(current_hc),
        "Net Planned Growth": int(net_growth_per_quarter),
        "TTM Attrition Backfills": round(q_attrition, 1),
        "Total Target Hires": round(q_hires_needed, 1)
    })
    current_hc = ending_hc

df_waterfall = pd.DataFrame(q_data)

# Total Aggregate Volumetric Metrics
total_hires_needed = df_waterfall["Total Target Hires"].sum()
total_tech_hires = total_hires_needed * tech_pct
total_gtm_hires = total_hires_needed * gtm_pct
total_ga_hires = total_hires_needed * ga_pct

# Offer Conversion Math
offers_tech = total_tech_hires / accept_tech
offers_gtm = total_gtm_hires / accept_gtm
offers_ga = total_ga_hires / accept_ga
total_offers = offers_tech + offers_gtm + offers_ga

# Ramped Steady-State TA Recruiter Capacity Needs
rec_tech_needed = (offers_tech / 4) / quota_tech
rec_gtm_needed = (offers_gtm / 4) / quota_gtm
rec_ga_needed = (offers_ga / 4) / quota_ga

# Sourcing Footprint Modifiers
sourcer_tech = rec_tech_needed * 0.5
sourcer_gtm = rec_gtm_needed * 0.25
total_ic_squad = rec_tech_needed + rec_gtm_needed + rec_ga_needed + sourcer_tech + sourcer_gtm
managers_needed = total_ic_squad / manager_ratio

# UI Data Layout Modules
col1, col2, col3 = st.columns(3)
col1.metric("Total Protected Hires (12M)", f"{round(total_hires_needed, 0)}")
col2.metric("Total Validated Offers Required", f"{round(total_offers, 0)}")
col3.metric("Total System Attrition Mitigated", f"{round(df_waterfall['TTM Attrition Backfills'].sum(), 0)}")

st.subheader("1. Headcount & Pre-Emptive Attrition Waterfall")
st.dataframe(df_waterfall, use_container_width=True)

st.subheader("2. Tailored Infrastructure Resource Blueprint (Recruiting & Talent Ops Only)")

infrastructure_template = pd.DataFrame({
    "Functional Sourcing Role": [
        "Recruiting Managers",
        "Technical Recruiters",
        "GTM Recruiters",
        "G&A Recruiters",
        "Dedicated Sourcing Partners",
        "Talent Operations Leader"
    ],
    "Steady-State Run Rate (FTEs)": [
        round(max(1.0, math.ceil(managers_needed)), 1),
        round(max(1.0, math.ceil(rec_tech_needed)), 1),
        round(max(1.0, math.ceil(rec_gtm_needed)), 1),
        round(max(1.0, math.ceil(rec_ga_needed)), 1),
        round(max(1.0, math.ceil(sourcer_tech + sourcer_gtm)), 1),
        1.0
    ],
    "Peak Scale-Up Staffing (Months 1-6)": [
        round(max(1.0, math.ceil(managers_needed)), 1),
        round(max(1.0, math.ceil(rec_tech_needed * 1.25)), 1), # Adds front-loaded ramp cushion
        round(max(1.0, math.ceil(rec_gtm_needed * 1.2)), 1),
        round(max(1.0, math.ceil(rec_ga_needed)), 1),
        round(max(1.0, math.ceil((sourcer_tech + sourcer_gtm) * 1.25)), 1),
        1.0
    ],
    "Strategic Guardrails & Framework Scope": [
        f"Calculated via a strict {manager_ratio}:1 IC monitoring ratio topology.",
        f"Anchored against a conservative {int(accept_tech*100)}% Bay Area tech acceptance model.",
        f"Reflects a global {int(accept_gtm*100)}% conversion average with senior market protections.",
        f"Optimized to hit high-velocity {int(accept_ga*100)}% conversion pipelines easily.",
        "Front-loaded 1:2 on Tech and 1:4 on GTM to insulate initial pipelines.",
        "Fixed core asset. Cleanly isolates compensation/mobility to separate People paths."
    ]
})

st.dataframe(infrastructure_template, use_container_width=True)
st.info("Note: Core Compensation, Benefits, and Employee Mobility variables are intentionally excluded from this model run to avoid any structural footprint overlaps with internal organizational designs.")
