import streamlit as st
import requests
import json

API_URL = "http://127.0.0.1:8000/predict"

st.set_page_config(page_title="AI Real Estate Agent", page_icon="🏠", layout="centered")

# Custom styling
st.markdown("""
<style>
    .stTextArea textarea { font-size: 16px; }
    .price-box {
        background: linear-gradient(135deg, #1B4332, #2D6A4F);
        color: white;
        padding: 30px;
        border-radius: 15px;
        text-align: center;
        margin: 20px 0;
    }
    .price-box h1 { color: white; margin: 0; font-size: 42px; }
    .price-box p { color: #B7E4C7; margin: 5px 0 0 0; }
    .feature-card {
        background: #F8F9FA;
        padding: 15px;
        border-radius: 10px;
        border-left: 4px solid #2D6A4F;
        margin: 8px 0;
    }
    .missing-card {
        background: #FFF3CD;
        padding: 15px;
        border-radius: 10px;
        border-left: 4px solid #FFC107;
        margin: 8px 0;
    }
</style>
""", unsafe_allow_html=True)

st.title("🏠 AI Real Estate Agent")
st.markdown("Describe a property in Ames, Iowa and get an instant price estimate powered by ML + LLM.")

# Initialize session state
if "features" not in st.session_state:
    st.session_state.features = None
if "step" not in st.session_state:
    st.session_state.step = "input"

# Step 1: User describes the property
query = st.text_area(
    "Describe the property:",
    placeholder="e.g., A 1500 sqft house in Edwards with 2 bathrooms, a nice kitchen, and a 2-car finished garage, built in 1995",
    height=100
)

if st.button("🔍 Analyze Description", type="primary"):
    if not query.strip():
        st.warning("Please describe a property first!")
    else:
        with st.spinner("Reading your description..."):
            try:
                response = requests.post(API_URL, json={"query": query})
                data = response.json()

                if data["success"]:
                    st.session_state.features = data["features"]
                    st.session_state.initial_price = data["predicted_price"]
                    st.session_state.initial_interpretation = data["interpretation"]
                    st.session_state.confidence = data["confidence_note"]
                    st.session_state.step = "review"
                else:
                    st.warning(data["message"])
                    if data.get("suggestions"):
                        st.markdown("**Try mentioning some of these:**")
                        for s in data["suggestions"]:
                            st.markdown(f"- {s}")
            except requests.exceptions.ConnectionError:
                st.error("Cannot connect to the server. Make sure the Docker container is running!")

# Step 2: Show extracted features and let user fill missing ones
if st.session_state.step == "review" and st.session_state.features:
    features = st.session_state.features

    st.markdown("---")
    st.markdown("### ✅ What we understood from your description")

    extracted = features["extracted_fields"]
    missing = features["missing_fields"]

    if extracted:
        cols = st.columns(min(len(extracted), 4))
        for i, field in enumerate(extracted):
            value = features.get(field)
            if value is not None:
                display_name = field.replace("_", " ").title()
                with cols[i % len(cols)]:
                    st.markdown(f"""<div class="feature-card">
                        <strong>{display_name}</strong><br>{value}
                    </div>""", unsafe_allow_html=True)

    # Missing features form
    if missing:
        st.markdown("---")
        st.markdown("### 📝 Help us fill in the blanks")
        st.markdown("The more details you provide, the more accurate the estimate.")

        with st.form("missing_features_form"):
            user_fills = {}

            col1, col2 = st.columns(2)

            for i, field in enumerate(missing):
                target_col = col1 if i % 2 == 0 else col2

                with target_col:
                    if field == "overall_qual":
                        user_fills[field] = st.slider(
                            "Overall Quality (1=Poor, 10=Excellent)",
                            1, 10, 6
                        )
                    elif field == "gr_liv_area":
                        user_fills[field] = st.number_input(
                            "Living Area (sqft)",
                            min_value=300, max_value=6000, value=1400
                        )
                    elif field == "total_bsmt_sf":
                        user_fills[field] = st.number_input(
                            "Basement Area (sqft, 0 if none)",
                            min_value=0, max_value=6000, value=900
                        )
                    elif field == "garage_cars":
                        user_fills[field] = st.selectbox(
                            "Garage Capacity (cars)",
                            [0, 1, 2, 3, 4], index=2
                        )
                    elif field == "garage_finish":
                        user_fills[field] = st.selectbox(
                            "Garage Interior",
                            ["None (no garage)", "Unf (unfinished)", "RFn (rough finished)", "Fin (finished)"],
                            index=1
                        )
                    elif field == "fireplaces":
                        user_fills[field] = st.selectbox(
                            "Fireplaces",
                            [0, 1, 2, 3], index=0
                        )
                    elif field == "kitchen_qual":
                        user_fills[field] = st.selectbox(
                            "Kitchen Quality",
                            ["Po (Poor)", "Fa (Fair)", "TA (Typical)", "Gd (Good)", "Ex (Excellent)"],
                            index=2
                        )
                    elif field == "neighborhood":
                        neighborhoods = [
                            "NAmes", "CollgCr", "OldTown", "Edwards", "Somerst",
                            "NridgHt", "Gilbert", "Sawyer", "NWAmes", "SawyerW",
                            "Mitchel", "BrkSide", "Crawfor", "IDOTRR", "Timber",
                            "NoRidge", "StoneBr", "SWISU", "ClearCr", "MeadowV",
                            "BrDale", "Blmngtn", "Veenker", "NPkVill", "Blueste"
                        ]
                        user_fills[field] = st.selectbox(
                            "Neighborhood",
                            neighborhoods, index=0
                        )
                    elif field == "year_built":
                        user_fills[field] = st.number_input(
                            "Year Built",
                            min_value=1870, max_value=2025, value=1990
                        )
                    elif field == "year_remod":
                        user_fills[field] = st.number_input(
                            "Year Last Remodeled",
                            min_value=1870, max_value=2025, value=2000
                        )
                    elif field == "full_bath":
                        user_fills[field] = st.selectbox(
                            "Full Bathrooms",
                            [0, 1, 2, 3], index=1
                        )
                    elif field == "half_bath":
                        user_fills[field] = st.selectbox(
                            "Half Bathrooms",
                            [0, 1, 2], index=0
                        )

            submitted = st.form_submit_button("🏡 Get Updated Estimate", type="primary")

            if submitted:
                # Clean up selectbox values
                for key, val in user_fills.items():
                    if isinstance(val, str) and "(" in val:
                        user_fills[key] = val.split(" (")[0]

                # Merge with extracted features
                merged_features = dict(features)
                for key, val in user_fills.items():
                    merged_features[key] = val
                    if key in merged_features["missing_fields"]:
                        merged_features["missing_fields"].remove(key)
                        merged_features["extracted_fields"].append(key)

                # Build a new query with all features for the API
                feature_desc = []
                if merged_features.get("gr_liv_area"):
                    feature_desc.append(f"{merged_features['gr_liv_area']} sqft")
                if merged_features.get("overall_qual"):
                    feature_desc.append(f"overall quality {merged_features['overall_qual']}/10")
                if merged_features.get("full_bath"):
                    feature_desc.append(f"{merged_features['full_bath']} full bathrooms")
                if merged_features.get("neighborhood"):
                    feature_desc.append(f"in {merged_features['neighborhood']}")
                if merged_features.get("year_built"):
                    feature_desc.append(f"built in {merged_features['year_built']}")
                if merged_features.get("garage_cars"):
                    feature_desc.append(f"{merged_features['garage_cars']}-car garage")
                if merged_features.get("kitchen_qual"):
                    qual_map = {"Po": "poor", "Fa": "fair", "TA": "typical", "Gd": "good", "Ex": "excellent"}
                    kq = merged_features["kitchen_qual"]
                    feature_desc.append(f"{qual_map.get(kq, kq)} kitchen")
                if merged_features.get("fireplaces"):
                    feature_desc.append(f"{merged_features['fireplaces']} fireplaces")

                full_query = "A house with " + ", ".join(feature_desc)

                with st.spinner("Calculating with complete details..."):
                    try:
                        response = requests.post(API_URL, json={"query": full_query})
                        data = response.json()

                        if data["success"]:
                            st.markdown(f"""<div class="price-box">
                                <p>Updated Estimated Price</p>
                                <h1>${data['predicted_price']:,.0f}</h1>
                                <p>{data['confidence_note']}</p>
                            </div>""", unsafe_allow_html=True)

                            st.markdown("#### 🏡 Agent's Analysis")
                            st.markdown(data["interpretation"])
                    except Exception as e:
                        st.error(f"Something went wrong: {str(e)}")

    # Show initial estimate regardless
    st.markdown("---")
    st.markdown("#### 📊 Initial Estimate (before filling details)")
    st.markdown(f"""<div class="price-box">
        <p>Initial Estimated Price</p>
        <h1>${st.session_state.initial_price:,.0f}</h1>
        <p>{st.session_state.confidence}</p>
    </div>""", unsafe_allow_html=True)
    st.markdown(st.session_state.initial_interpretation)

# Footer
st.markdown("---")
st.caption("AI Real Estate Agent | SE Factory AI Engineering Bootcamp | Ames Housing Dataset")