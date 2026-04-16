import streamlit as st
import requests

# 1. SETUP & STYLE
# ---------------------------------------------------------
API_URL = "https://ai-real-estate-agent-production.up.railway.app/predict"

st.set_page_config(page_title="AI Real Estate Agent", page_icon="🏠")

# Simple custom CSS for the price display
st.markdown("""
    <style>
    .price-display {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #2e7bcf;
        margin: 10px 0px;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. HEADER & INPUT BOX
# ---------------------------------------------------------
st.title("🏠 AI Real Estate Agent")

st.info("""
**Example description:** "A 1500 sqft house in Edwards with 2 bathrooms, a nice kitchen, and a 2-car finished garage, built in 1995"
""")

# The main input box
user_description = st.text_area(
    "Describe the property you want to estimate:",
    placeholder="Enter details here...",
    height=150
)

# Initialize storage for our data so it doesn't disappear when the page reloads
if "data" not in st.session_state:
    st.session_state.data = None

# 3. THE "LAUNCH" BUTTON
# ---------------------------------------------------------
if st.button("🚀 Launch AI Analysis", type="primary"):
    if not user_description.strip():
        st.warning("Please enter a description first!")
    else:
        with st.spinner("The AI is analyzing your text..."):
            try:
                # Send the description to the LLM API
                response = requests.post(API_URL, json={"query": user_description})
                result = response.json()

                if result["success"]:
                    # Save the result to session state
                    st.session_state.data = result
                else:
                    st.error("The AI couldn't understand that. Try adding more details.")
            except:
                st.error("Connection error. Is the server running?")

# 4. DISPLAY RESULTS (Only if we have data)
# ---------------------------------------------------------
if st.session_state.data:
    res = st.session_state.data
    features = res["features"]

    st.divider()

    # SECTION: What we understood
    st.subheader("✅ What we understood...")
    found = ", ".join(features["extracted_fields"]).replace("_", " ").title()
    st.write(f"**Extracted details:** {found}")
    
    # SECTION: Initial Estimate
    st.subheader("💰 Initial Estimate")
    st.markdown(f"""
        <div class="price-display">
            <p>Based on your text, the estimated value is:</p>
            <h2>${res['predicted_price']:,.2f}</h2>
            <small>{res['confidence_note']}</small>
        </div>
    """, unsafe_allow_html=True)

    # SECTION: Help us fill in the blanks
    missing = features["missing_fields"]
    if missing:
        st.divider()
        st.subheader("📝 Help us fill in the blanks")
        st.write("The AI missed these details. Provide them for a more accurate price:")

        # Create a form for the missing info
        with st.form("refinement_form"):
            user_inputs = {}
            cols = st.columns(2)
            
            for i, field in enumerate(missing):
                label = field.replace("_", " ").title()
                # Use the left column for even items, right for odd
                with cols[i % 2]:
                    if "qual" in field:
                        user_inputs[field] = st.slider(f"{label} (1-10)", 1, 10, 5)
                    elif "sqft" in field or "area" in field:
                        user_inputs[field] = st.number_input(f"{label}", value=1200)
                    else:
                        user_inputs[field] = st.text_input(f"{label}")

            submit_update = st.form_submit_button("Update Estimate")
            
            if submit_update:
                st.success("Details received! (In a full app, this would trigger a re-calculation)")

# 5. FOOTER
# ---------------------------------------------------------
st.markdown("---")
st.caption("Powered by LLM + Ames Housing Dataset")



# SECTION: Help us fill in the blanks
missing = features["missing_fields"]
if missing:
        st.divider()
        st.subheader("📝 Help us fill in the blanks")
        st.write("The AI missed these details. Provide them for a more accurate price:")

        with st.form("refinement_form"):
            user_inputs = {}
            cols = st.columns(2)
            
            for i, field in enumerate(missing):
                label = field.replace("_", " ").title()
                with cols[i % 2]:
                    if "qual" in field:
                        user_inputs[field] = st.slider(f"{label} (1-10)", 1, 10, 5)
                    elif "sqft" in field or "area" in field or "sf" in field:
                        user_inputs[field] = st.number_input(f"{label}", value=1000)
                    else:
                        user_inputs[field] = st.text_input(f"{label}")

            # This button triggers the FINAL calculation
            submit_update = st.form_submit_button("✨ Generate Final Valuation", type="primary")
            
            if submit_update:
                # We create a new prompt combining the old text + new specific details
                extra_details = ", ".join([f"{k}: {v}" for k, v in user_inputs.items()])
                final_query = f"{user_description}. Additional details: {extra_details}"
                
                with st.spinner("Calculating final results..."):
                    try:
                        final_res = requests.post(API_URL, json={"query": final_query}).json()
                        
                        if final_res["success"]:
                            st.balloons() # Added a little celebration!
                            st.divider()
                            st.header("🏁 Final AI Verdict")
                            
                            # Final Price Box
                            st.markdown(f"""
                                <div style="background-color: #1B4332; color: white; padding: 30px; border-radius: 15px; text-align: center;">
                                    <h3>Final Estimated Value</h3>
                                    <h1 style="font-size: 50px;">${final_res['predicted_price']:,.2f}</h1>
                                    <p style="color: #B7E4C7;">{final_res['confidence_note']}</p>
                                </div>
                            """, unsafe_allow_html=True)
                            
                            # Final Interpretation
                            st.info("**AI Analysis:** " + final_res["interpretation"])
                        else:
                            st.error("Could not generate final estimate.")
                    except:
                        st.error("Server connection lost during final update.")

# Footer
st.markdown("---")
st.caption("AI Real Estate Agent | Ames Housing Project")