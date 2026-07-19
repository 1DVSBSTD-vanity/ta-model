import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import math
import pandas as pd

# =====================================================================
# 1. PAGE CONFIGURATION & LAYOUT
# =====================================================================
st.set_page_config(
    page_title="Data Alignment Portal",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Application Data Portal")
st.subheader("Google Sheets & Gamma Synchronization System")

# =====================================================================
# 2. GOOGLE SHEETS API CONNECTION SETUP
# =====================================================================
@st.cache_resource
def init_google_sheets():
    """Establishes connection to Google Sheets using Streamlit Secrets."""
    try:
        # Define the access scopes needed
        scopes = [
            "https://googleapis.com",
            "https://googleapis.com"
        ]
        
        # Load credentials securely from st.secrets
        # Ensure your secrets.toml has a [gcp_service_account] section
        creds = Credentials.from_service_account_info(
            st.secrets["gcp_service_account"], 
            scopes=scopes
        )
        
        # Authorize gspread client
        client = gspread.authorize(creds)
        return client
    except Exception as e:
        st.error(f"⚠️ Google Sheets Authentication Failed: {e}")
        return None

# Initialize the client
gc = init_google_sheets()

# =====================================================================
# 3. USER INPUT INTERFACE
# =====================================================================
st.markdown("### 📥 Enter Transaction or Layout Matrix Data")

col1, col2, col3 = st.columns(3)

with col1:
    item_name = st.text_input("Item or Project Name", value="New Project Asset")

with col2:
    # Capturing raw numeric data that might contain uneven floats/decimals
    raw_metric_value = st.number_input(
        "Enter Metric Value (Hours, Cost, or Multiplier)", 
        value=14.23, 
        step=0.01,
        help="This raw value will automatically pass through ceiling logic to align with Sheets/Gamma grids."
    )

with col3:
    allocation_category = st.selectbox(
        "Gamma Theme / Category",
        options=["Core Development", "UI/UX Layout", "Database Sync", "Marketing Operations"]
    )

# =====================================================================
# 4. CRITICAL CEILING LOGIC & DATA ALIGNMENT
# =====================================================================
# math.ceil() rounds any decimal UP to the next nearest whole integer.
# Converting to int() removes any trailing '.0' so it fits perfectly into grid columns or flat sheets.
aligned_integer_value = int(math.ceil(raw_metric_value))

# Layout metrics validation display
st.markdown("---")
metric_col1, metric_col2 = st.columns(2)
with metric_col1:
    st.metric(label="Raw Input Value", value=f"{raw_metric_value:.2f}")
with metric_col2:
    st.metric(label="Ceiling Aligned Integer (Sent to Sheets/Gamma)", value=aligned_integer_value, delta="Aligned UP")

# =====================================================================
# 5. DATA TRANSMISSION & SYNCHRONIZATION
# =====================================================================
st.markdown("### 🚀 Synchronize System Data")

if st.button("Execute Alignment & Push Data", type="primary"):
    if gc is not None:
        try:
            # Open your Google Sheet by name or URL (Replace with your actual sheet name)
            # Ensure your Service Account email is shared on the Google Sheet as an Editor!
            sheet = gc.open("Your_Google_Sheet_Name").sheet1
            
            # Construct the clean payload utilizing our ceiling-aligned value
            payload_row = [
                item_name, 
                aligned_integer_value,  # Fixed: No decimals to break column widths or alignments
                allocation_category
            ]
            
            # Append row data to Google Sheets
            sheet.append_row(payload_row)
            st.success("✅ Success: Data cleanly appended to Google Sheets matrix!")
            
            # ---------------------------------------------------------
            # MOCK GAMMA LAYOUT ENGINE SYNC
            # ---------------------------------------------------------
            # This is where your Gamma grid structural allocation happens.
            # Using the aligned integer keeps columns cleanly structured.
            st.info(f"🔄 Gamma Engine Syncing: Allocated {aligned_integer_value} total block items across grid layout.")
            
        except gspread.exceptions.SpreadsheetNotFound:
            st.error("❌ Google Sheet Error: The specified sheet name was not found. Please verify the exact title.")
        except Exception as sync_error:
            st.error(f"❌ Synchronization failed: {sync_error}")
    else:
        st.warning("⚠️ Action blocked: Google Sheets credentials are not configured inside Streamlit Secrets.")

# =====================================================================
# 6. LOCAL DATA PREVIEW
# =====================================================================
st.markdown("---")
st.markdown("### 📋 Current Active Session Preview Matrix")

# Displaying what the final clean export looks like locally
preview_data = {
    "Target Identity": [item_name],
    "Aligned Unit Metric (Ceiling)": [aligned_integer_value],
    "Gamma Deployment Vector": [allocation_category]
}

df_preview = pd.DataFrame(preview_data)
st.dataframe(df_preview, use_container_width=True)
