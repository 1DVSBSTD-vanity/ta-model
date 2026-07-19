import streamlit as st
import pandas as pd
import math

# =====================================================================
# 1. APP CONFIGURATION & STYLING
# =====================================================================
st.set_page_config(
    page_title="Fireworks AI - Dynamic TA Model",
    page_icon="🎆",
    layout="wide"
)

st.title("🎆 Fireworks AI: Talent Acquisition Planning Suite")
st.subheader("Dynamic Operational Dashboard & 12-Month Resource Capacity Model")
st.markdown("---")

# =====================================================================
# 2. APP STATE & CONTROL PANEL (LEFT SIDEBAR OVERLAY)
# =====================================================================
with st.sidebar:
    st.header("🎛️ Control Panel Drivers")
    
    with st.expander("📈 Scale & Growth Drivers", expanded=True):
        base_hc = st.number_input("Initial Base Headcount", value=200, step=10)
        target_hc = st.number_input("Target Ending Headcount", value=600, step=10)
        attrition_rate = st.slider("Annual TTM Attrition Rate (%)", min_value=0.0, max_value=50.0, value=10.0, step=0.5) / 100.0

    with st.expander("🏢 Departmental Allocations", expanded=False):
        tech_alloc = st.slider("Tech / Product Allocation (%)", min_value=0.0, max_value=100.0, value=65.0, step=1.0) / 100.0
        gtm_alloc = st.slider("GTM Allocation (%)", min_value=0.0, max_value=100.0, value=25.0, step=1.0) / 100.0
        ga_alloc = st.slider("G&A Allocation (%)", min_value=0.0, max_value=100.0, value=10.0, step=1.0) / 100.0

    with st.expander("🌍 Geographic & Segment Weights", expanded=False):
        amer_alloc = st.slider("AMER Allocation (%)", min_value=0.0, max_value=100.0, value=75.0, step=1.0) / 100.0
        emea_alloc = st.slider("EMEA Allocation (%)", min_value=0.0, max_value=100.0, value=17.0, step=1.0) / 100.0
        apac_alloc = st.slider("APAC Allocation (%)", min_value=0.0, max_value=100.0, value=8.0, step=1.0) / 100.0

    with st.expander("🎯 Recruiter Production Quotas", expanded=False):
        tech_quota = st.number_input("Technical Recruiter Quota (Offers/Qtr)", value=8)
        gtm_ent_quota = st.number_input("GTM Recruiter Quota (Offers/Qtr)", value=12)
        ga_quota = st.number_input("G&A Recruiter Quota (Offers/Qtr)", value=15)

    with st.expander("🤝 Offer Acceptance Matrices", expanded=False):
        tech_accept = st.slider("Bay Area Tech Acceptance Rate (%)", min_value=0.0, max_value=100.0, value=65.0, step=1.0) / 100.0
        gtm_accept = st.slider("Global GTM Acceptance Rate (%)", min_value=0.0, max_value=100.0, value=85.0, step=1.0) / 100.0
        ga_accept = st.slider("G&A Acceptance Rate (%)", min_value=0.0, max_value=100.0, value=90.0, step=1.0) / 100.0

    with st.expander("⚙️ TA Ratios, Modifiers & Roles", expanded=False):
        ics_per_manager = st.number_input("ICs per Recruiting Manager", value=10)
        tech_sourcer_ratio = st.number_input("Tech Sourcer-to-Recruiter Ratio", value=0.5, step=0.05)
        gtm_sourcer_ratio = st.number_input("GTM Sourcer-to-Recruiter Ratio", value=0.25, step=0.05)
        ramping_penalty = st.slider("Tech Recruiter Ramping Penalty (%)", min_value=0.0, max_value=100.0, value=25.0, step=1.0) / 100.0
        coordinators_per_recruiter = st.number_input("Coordinators per Recruiter Ratio", value=0.4, step=0.05)

# Verify Allocation Matrix Validation
if not math.isclose((tech_alloc + gtm_alloc + ga_alloc), 1.0):
    st.warning("⚠️ Warning: Your Departmental Allocations do not sum to 100%. Adjust inputs in the sidebar layout for accurate mathematical modeling.")

# =====================================================================
# 3. BACKEND COMPUTATIONAL CASCADE ENGINE (MATHEMATICAL WATERFALL)
# =====================================================================
quarters = ["Q1", "Q2", "Q3", "Q4"]

# Step A: Layout Baseline Growth Distribution Profiles
net_growth_per_q = (target_hc - base_hc) / 4

# Initialize tracking dictionaries for quarterly calculations
start_hc = {}
net_growth = {}
attrition_backfills = {}
end_hc = {}
total_hires_needed = {}

current_starting_hc = base_hc

for q in quarters:
    start_hc[q] = current_starting_hc
    net_growth[q] = net_growth_per_q
    
    # Quarterly attrition math mirroring the spreadsheet: ((Start + End) / 2) * (Annual Attrition / 4)
    current_ending_hc = current_starting_hc + net_growth_per_q
    avg_q_hc = (current_starting_hc + current_ending_hc) / 2
    
    # We round backfills using math.ceil to cleanly map discrete backfill targets
    attrition_backfills[q] = math.ceil(avg_q_hc * (attrition_rate / 4.0))
    
    end_hc[q] = current_ending_hc
    total_hires_needed[q] = net_growth[q] + attrition_backfills[q]
    
    # The ending headcount becomes the next quarter's baseline
    current_starting_hc = current_ending_hc

# Step B: Pipeline Offer Generation Logic Cascades
offers_tech = {}
offers_gtm = {}
offers_ga = {}

for q in quarters:
    q_hires = total_hires_needed[q]
    
    # Segment hire targets based on departmental weight structures
    tech_hires = q_hires * tech_alloc
    gtm_hires = q_hires * gtm_alloc
    ga_hires = q_hires * ga_alloc
    
    # Offers Required = Hires Target / Acceptance Rate (With strict ceiling tracking)
    offers_tech[q] = math.ceil(tech_hires / tech_accept) if tech_accept > 0 else 0
    offers_gtm[q] = math.ceil(gtm_hires / gtm_accept) if gtm_accept > 0 else 0
    offers_ga[q] = math.ceil(ga_hires / ga_accept) if ga_accept > 0 else 0

# Step C: Operational TA Organization Capacity Mapping (Ceiling Logic Applied)
req_tech_recruiters = {}
req_gtm_recruiters = {}
req_ga_recruiters = {}
req_sourcers = {}
req_coordinators = {}
req_managers = {}
req_ops_leaders = {}

for q in quarters:
    # Recruiter capacity factors ramping modifiers where applicable
    tech_capacity_per_recruiter = tech_quota * (1.0 - ramping_penalty)
    
    # Recruiters needed = Offers Produced / Quarterly Quota Capacity
    req_tech_recruiters[q] = math.ceil(offers_tech[q] / tech_capacity_per_recruiter) if tech_capacity_per_recruiter > 0 else 0
    req_gtm_recruiters[q] = math.ceil(offers_gtm[q] / gtm_ent_quota) if gtm_ent_quota > 0 else 0
    req_ga_recruiters[q] = math.ceil(offers_ga[q] / ga_quota) if ga_quota > 0 else 0
    
    # Sourcing infrastructure layer calculated from recruiter ratios
    tech_sourcers = req_tech_recruiters[q] * tech_sourcer_ratio
    gtm_sourcers = req_gtm_recruiters[q] * gtm_sourcer_ratio
    req_sourcers[q] = math.ceil(tech_sourcers + gtm_sourcers)
    
    # Coordinator allocations mapped across core active hiring units
    total_active_recruiters = req_tech_recruiters[q] + req_gtm_recruiters[q] + req_ga_recruiters[q]
    req_coordinators[q] = math.ceil(total_active_recruiters * coordinators_per_recruiter)
    
    # Management layer matching IC dashboard spans of control
    total_ics = total_active_recruiters + req_sourcers[q] + req_coordinators[q]
    req_managers[q] = math.ceil(total_ics / ics_per_manager) if ics_per_manager > 0 else 0
    
    # Fixed systemic leadership headcount placement
    req_ops_leaders[q] = 1

# =====================================================================
# 4. EXECUTABLE DATA PRESENTATION VISUALIZATIONS
# =====================================================================
col_data1, col_data2 = st.columns([1, 4])

with col_data1:
    st.metric("Total 12-Month Target Hires", value=f"{sum(total_hires_needed.values())} Hires")
    st.metric("Peak Target TA Org Size", value=f"{req_tech_recruiters['Q4'] + req_gtm_recruiters['Q4'] + req_ga_recruiters['Q4'] + req_sourcers['Q4'] + req_coordinators['Q4'] + req_managers['Q4'] + req_ops_leaders['Q4']} FTE")

with col_data2:
    # Build complete model dataframe matrix structured matching user requirement output
    waterfall_matrix = {
        "Metric Waterfall Profile Layer": [
            "📋 COMPANY LEVEL HYPERSCALE PIPELINE",
            "Starting Headcount (TTM)",
            "Net Planned Growth",
            "TTM Attrition Backfills",
            "Ending Headcount Blueprint",
            "Total Target Hires Needed",
            "🎯 PIPELINE PIPELINE OFFERS REQUIRED",
            "AMER Tech Offers Required",
            "Global GTM Offers Required",
            "G&A Offers Required",
            "🛠️ TALENT ACQUISITION ORG CAPACITY REQUIREMENTS",
            "Technical Recruiters Required",
            "GTM Recruiters Required",
            "G&A Recruiters Required",
            "Dedicated Sourcing Partners",
            "Recruiting Coordinators",
            "Recruiting Managers Required",
            "Talent Operations Leader"
        ],
        "Q1": [
            "", int(start_hc["Q1"]), int(net_growth["Q1"]), int(attrition_backfills["Q1"]), int(end_hc["Q1"]), int(total_hires_needed["Q1"]),
            "", int(offers_tech["Q1"]), int(offers_gtm["Q1"]), int(offers_ga["Q1"]),
            "", int(req_tech_recruiters["Q1"]), int(req_gtm_recruiters["Q1"]), int(req_ga_recruiters["Q1"]), int(req_sourcers["Q1"]), int(req_coordinators["Q1"]), int(req_managers["Q1"]), int(req_ops_leaders["Q1"])
        ],
        "Q2": [
            "", int(start_hc["Q2"]), int(net_growth["Q2"]), int(attrition_backfills["Q2"]), int(end_hc["Q2"]), int(total_hires_needed["Q2"]),
            "", int(offers_tech["Q2"]), int(offers_gtm["Q2"]), int(offers_ga["Q2"]),
            "", int(req_tech_recruiters["Q2"]), int(req_gtm_recruiters["Q2"]), int(req_ga_recruiters["Q2"]), int(req_sourcers["Q2"]), int(req_coordinators["Q2"]), int(req_managers["Q2"]), int(req_ops_leaders["Q2"])
        ],
        "Q3": [
            "", int(start_hc["Q3"]), int(net_growth["Q3"]), int(attrition_backfills["Q3"]), int(end_hc["Q3"]), int(total_hires_needed["Q3"]),
            "", int(offers_tech["Q3"]), int(offers_gtm["Q3"]), int(offers_ga["Q3"]),
