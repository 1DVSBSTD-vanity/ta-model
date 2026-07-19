import streamlit as st
import pandas as pd
import math
import io

# =====================================================================
# 1. APP CONFIGURATION
# =====================================================================
st.set_page_config(page_title="TA Resource Model Calculator", layout="wide")
st.title("📊 Fireworks AI: TA Resource Model Calculator")

# =====================================================================
# 2. FILE UPLOADER (Connects your local Excel file)
# =====================================================================
st.info("📂 Please upload 'Fireworks AI_ TA Resource Model Calculator.xlsx' to initialize the model.")
uploaded_file = st.file_uploader("Upload Excel Model", type=["xlsx"])

if uploaded_file:
    # Read the Excel file
    # NOTE: If your data is on a specific sheet, change sheet_name=0 to the name, e.g., sheet_name="Inputs"
    df = pd.read_excel(uploaded_file, sheet_name=0)

    # =====================================================================
    # 3. DYNAMIC CONTROL PANEL
    # =====================================================================
    st.sidebar.header("🎛️ Control Panel Variables")
    
    # We create a dictionary to store the modified values from the sidebar
    modified_inputs = {}
    
    # Automatically detect numeric columns to create inputs for
    # You can customize this list if you only want specific columns to be controls
    numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns.tolist()
    
    with st.sidebar:
        st.write("Adjust the drivers below to update the model:")
        for col in numeric_cols:
            # Skip columns that look like calculated results (optional filter)
            if "Total" in col or "Result" in col:
                continue
                
            # Get the initial value from the first row of the Excel file (Baseline)
            # We assume Row 0 contains the baseline values
            base_val = float(df[col].iloc[0]) if not pd.isna(df[col].iloc[0]) else 0.0
            
            # Create a number input for this column
            modified_inputs[col] = st.number_input(
                label=f"{col}",
                value=base_val,
                step=1.0 if base_val > 10 else 0.1
            )

    # =====================================================================
    # 4. CALCULATION & CEILING LOGIC
    # =====================================================================
    # Create a copy of the dataframe to hold our "Scenario" data
    scenario_df = df.copy()
    
    # Update the first row with our new sidebar values
    for col, new_val in modified_inputs.items():
        scenario_df.at[0, col] = new_val

    # --- APPLY LOGIC ---
    # Example: If your model calculates "Headcount Needed" based on these inputs
    # You likely have a formula. Since we are reading raw data, we simulate a calculation here.
    # REPLACE the formula below with the actual logic from your Excel file.
    
    # Example Logic: (Volume / Capacity) = Raw Headcount
    # We look for columns named like 'Volume' or 'Capacity' dynamically
    
    # Let's try to find a 'Headcount' or similar result column to apply CEILING to
    # If specific columns need ceiling, list them here:
    ceiling_columns = [col for col in df.columns if "Headcount" in col or "FTE" in col or "Resource" in col]
    
    if ceiling_columns:
        st.subheader("🛠️ Model Adjustments (Ceiling Applied)")
        for col in ceiling_columns:
            # Get the raw value (assuming it might be calculated or just adjusted)
            raw_val = scenario_df.at[0, col]
            
            # 1. Apply Ceiling Logic
            aligned_val = math.ceil(raw_val)
            
            # Update the dataframe with the integer value
            scenario_df.at[0, col] = aligned_val
            
            # Display the adjustment
            st.metric(
                label=f"Adjusted {col}", 
                value=aligned_val, 
                delta=f"Rounded up from {raw_val:.2f}"
            )
    else:
        # Fallback if no specific columns match
        st.warning("⚠️ No 'Headcount' or 'FTE' columns found to apply ceiling logic automatically.")

    # =====================================================================
    # 5. DISPLAY RESULTS
    # =====================================================================
    st.divider()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📄 Original Baseline (From Excel)")
        st.dataframe(df, use_container_width=True)
        
    with col2:
        st.subheader("🔮 Scenerio Model (Live Updated)")
        st.dataframe(scenario_df, use_container_width=True)

else:
    # Prompt to upload if no file is present
    st.write("👆 **Please upload the Excel file in the sidebar to begin.**")
    
    # Optional: Mock data for visual layout if you want to see how it looks before uploading
    st.markdown("---")
    st.caption("Waiting for `Fireworks AI_ TA Resource Model Calculator.xlsx`...")
