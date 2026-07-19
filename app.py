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

    with st.expander("🌍 Geographic & Segment Weights", expanded=True):
        amer_alloc = st.slider("AMER Allocation (%)", min_value=0.0, max_value=100.0, value=75.0, step=1.0) / 100.0
        # Combine EMEA and APAC to calculate the aggregate international capacity factor
        emea_alloc = st.slider("EMEA Allocation (%)", min_value=0.0, max_value=100.0, value=17.0, step=1.0) / 100.0
        apac_alloc = st.slider("APAC Allocation (%)", min_value=0.0, max_value=100.0, value=8.0, step=1.0) / 100.0
        intl_alloc = (emea_alloc + apac_alloc) / 100.0

    with st.expander("🎯 Recruiter Production Quotas (Baseline)", expanded=False):
        tech_quota = st.number_input("Technical Recruiter Quota (Offers/Qtr)", value=8)
        gtm_ent_quota = st.number_input("GTM Recruiter Quota (Offers/Qtr)", value=12)
        ga_quota = st.number_input("G&A Recruiter Quota (Offers/Qtr)", value=15)

    with st.expander("🤝 Offer Acceptance Matrices", expanded=False):
        tech_accept = st.slider("Bay Area Tech Acceptance Rate (%)", min_value=0.0, max_value=100.0, value=65.0, step=1.0) / 100.0
        gtm_accept = st.slider("Global GTM Acceptance Rate (%)", min_value=0.0, max_value=100.0, value=85.0, step=1.0) / 100.0
        ga_accept = st.slider("G&A Acceptance Rate (%)", min_value=0.0, max_value=100.0, value=90.0, step=1.0) / 100.0

    with st.expander("⚙️ Ramping & International Modifiers", expanded=True):
        universal_ramp_penalty = st.slider("90-Day Universal Ramping Penalty (%)", min_value=0.0, max_value=100.0, value=25.0, step=1.0) / 100.0
        intl_production_modifier = st.slider("International Recruiter Efficiency Multiplier (%)", min_value=10.0, max_value=150.0, value=80.0, step=5.0) / 100.0
        
    with st.expander("👥 TA Structure Ratios & Roles", expanded=False):
        ics_per_manager = st.number_input("ICs per Recruiting Manager", value=10)
        tech_sourcer_ratio = st.number_input("Tech Sourcer-to-Recruiter Ratio", value=0.5, step=0.05)
        gtm_sourcer_ratio = st.number_input("GTM Sourcer-to-Recruiter Ratio", value=0.25, step=0.05)
        coordinators_per_recruiter = st.number_input("Coordinators per Recruiter Ratio", value=0.4, step=0.05)

# Validate Department Allocations
if not math.isclose((tech_alloc + gtm_alloc + ga_alloc), 1.0):
    st.warning("⚠️ Warning: Your Departmental Allocations do not sum to 100%. Adjust inputs in the sidebar layout for accurate mathematical modeling.")

# =====================================================================
# 3. BACKEND COMPUTATIONAL CASCADE ENGINE (MATHEMATICAL WATERFALL)
# =====================================================================
quarters = ["Q1", "Q2", "Q3", "Q4"]
net_growth_per_q = (target_hc - base_hc) / 4

# Initialize metrics dictionaries
start_hc, net_growth, attrition_backfills, end_hc, total_hires_needed = {}, {}, {}, {}, {}
offers_tech, offers_gtm, offers_ga = {}, {}, {}
req_tech_rec, req_gtm_rec, req_ga_rec, req_src, req_coord, req_mgr, req_ops = {}, {}, {}, {}, {}, {}, {}

current_starting_hc = base_hc

for q in quarters:
    start_hc[q] = current_starting_hc
    net_growth[q] = net_growth_per_q
    
    # Attrition matching spreadsheet formulas
    current_ending_hc = current_starting_hc + net_growth_per_q
    avg_q_hc = (current_starting_hc + current_ending_hc) / 2
    attrition_backfills[q] = math.ceil(avg_q_hc * (attrition_rate / 4.0))
    
    end_hc[q] = current_ending_hc
    total_hires_needed[q] = net_growth[q] + attrition_backfills[q]
    
    # Offers Required Logic
    offers_tech[q] = math.ceil((total_hires_needed[q] * tech_alloc) / tech_accept) if tech_accept > 0 else 0
    offers_gtm[q] = math.ceil((total_hires_needed[q] * gtm_alloc) / gtm_accept) if gtm_accept > 0 else 0
    offers_ga[q] = math.ceil((total_hires_needed[q] * ga_alloc) / ga_accept) if ga_accept > 0 else 0
    
    # Calculate weighted quarterly recruiter capacity combining AMER baseline and International expectations
    # 90-day universal ramp penalty lowers baseline production for the first quarter of deployment
    ramp_factor = (1.0 - universal_ramp_penalty) if q == "Q1" else 1.0
    
    # Blended capacity factor equation based on geographic distribution splits
    amer_pct = amer_alloc / 100.0
    intl_pct = intl_alloc
    
    tech_capacity = ((tech_quota * amer_pct) + (tech_quota * intl_pct * intl_production_modifier)) * ramp_factor
    gtm_capacity = ((gtm_ent_quota * amer_pct) + (gtm_ent_quota * intl_pct * intl_production_modifier)) * ramp_factor
    ga_capacity = ((ga_quota * amer_pct) + (ga_quota * intl_pct * intl_production_modifier)) * ramp_factor
    
    # TA Headcount calculations
    req_tech_rec[q] = math.ceil(offers_tech[q] / tech_capacity) if tech_capacity > 0 else 0
    req_gtm_rec[q] = math.ceil(offers_gtm[q] / gtm_capacity) if gtm_capacity > 0 else 0
    req_ga_rec[q] = math.ceil(offers_ga[q] / ga_capacity) if ga_capacity > 0 else 0
    
    req_src[q] = math.ceil((req_tech_rec[q] * tech_sourcer_ratio) + (req_gtm_rec[q] * gtm_sourcer_ratio))
    total_active_recs = req_tech_rec[q] + req_gtm_rec[q] + req_ga_rec[q]
    req_coord[q] = math.ceil(total_active_recs * coordinators_per_recruiter)
    
    total_ics = total_active_recs + req_src[q] + req_coord[q]
    req_mgr[q] = math.ceil(total_ics / ics_per_manager) if ics_per_manager > 0 else 0
    req_ops[q] = 1
    
    # Cycle starting headcount forward
    current_starting_hc = current_ending_hc

# =====================================================================
# 4. ROW-SAFE MATRIX CONSTRUCTOR
# =====================================================================
matrix_rows = [
    ["📋 COMPANY LEVEL HYPERSCALE PIPELINE", "", "", "", "", ""],
    ["Starting Headcount (TTM)", int(start_hc["Q1"]), int(start_hc["Q2"]), int(start_hc["Q3"]), int(start_hc["Q4"]), "—"],
    ["Net Planned Growth", int(net_growth["Q1"]), int(net_growth["Q2"]), int(net_growth["Q3"]), int(net_growth["Q4"]), int(sum(net_growth.values()))],
    ["TTM Attrition Backfills", int(attrition_backfills["Q1"]), int(attrition_backfills["Q2"]), int(attrition_backfills["Q3"]), int(attrition_backfills["Q4"]), int(sum(attrition_backfills.values()))],
    ["Ending Headcount Blueprint", int(end_hc["Q1"]), int(end_hc["Q2"]), int(end_hc["Q3"]), int(end_hc["Q4"]), "—"],
    ["Total Target Hires Needed", int(total_hires_needed["Q1"]), int(total_hires_needed["Q2"]), int(total_hires_needed["Q3"]), int(total_hires_needed["Q4"]), int(sum(total_hires_needed.values()))],
    
    ["🎯 PIPELINE OFFERS REQUIRED", "", "", "", "", ""],
    ["AMER Tech Offers Required", int(offers_tech["Q1"]), int(offers_tech["Q2"]), int(offers_tech["Q3"]), int(offers_tech["Q4"]), int(sum(offers_tech.values()))],
    ["Global GTM Offers Required", int(offers_gtm["Q1"]), int(offers_gtm["Q2"]), int(offers_gtm["Q3"]), int(offers_gtm["Q4"]), int(sum(offers_gtm.values()))],
    ["G&A Offers Required", int(offers_ga["Q1"]), int(offers_ga["Q2"]), int(offers_ga["Q3"]), int(offers_ga["Q4"]), int(sum(offers_ga.values()))],
    
    ["🛠️ TALENT ACQUISITION ORG CAPACITY REQUIREMENTS", "", "", "", "", ""],
    ["Technical Recruiters Required", int(req_tech_rec["Q1"]), int(req_tech_rec["Q2"]), int(req_tech_rec["Q3"]), int(req_tech_rec["Q4"]), "—"],
    ["GTM Recruiters Required", int(req_gtm_rec["Q1"]), int(req_gtm_rec["Q2"]), int(req_gtm_rec["Q3"]), int(req_gtm_rec["Q4"]), "—"],
    ["G&A Recruiters Required", int(req_ga_rec["Q1"]), int(req_ga_rec["Q2"]), int(req_ga_rec["Q3"]), int(req_ga_rec["Q4"]), "—"],
    ["Dedicated Sourcing Partners", int(req_src["Q1"]), int(req_src["Q2"]), int(req_src["Q3"]), int(req_src["Q4"]), "—"],
    ["Recruiting Coordinators", int(req_coord["Q1"]), int(req_coord["Q2"]), int(req_coord["Q3"]), int(req_coord["Q4"]), "—"],
    ["Recruiting Managers Required", int(req_mgr["Q1"]), int(req_mgr["Q2"]), int(req_mgr["Q3"]), int(req_mgr["Q4"]), "—"],
    ["Talent Operations Leader", int(req_ops["Q1"]), int(req_ops["Q2"]), int(req_ops["Q3"]), int(req_ops["Q4"]), "—"]
]

df_model = pd.DataFrame(
    matrix_rows, 
    columns=["Metric Waterfall Profile Layer", "Q1", "Q2", "Q3", "Q4", "12-Month Total"]
)

# =====================================================================
# 5. DATA PRESENTATION LAYOUT
# =====================================================================
col_data1, col_data2 = st.columns([1, 4])

with col_data1:
