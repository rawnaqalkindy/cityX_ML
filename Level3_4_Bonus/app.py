import streamlit as st
import pandas as pd
from model import load_and_train_model, assign_severity
import level3
import level4

st.set_page_config(page_title="CityX Crime Dashboard", layout="wide")
st.sidebar.title("CityX Crime Dashboard")
section = st.sidebar.radio(
    "Choose a Section",
    ["Level 3: Geo-Spatial Mapping", "Level 4: Report Classification"]
)

# Loading the model
vectorizer, model, label_encoder = load_and_train_model()

if section == "Level 3: Geo-Spatial Mapping":
    with st.spinner("Loading Map..."):
        st.header("Interactive Crime Map")
        map_html = level3.create_geo_map()
        st.components.v1.html(map_html, height=600, scrolling=True)

elif section == "Level 4: Report Classification":
    with st.spinner("Loading Report..."):
        st.header("Police Report Classification")
        df_reports = level4.process_police_reports()
        
        if 'detailed_description' in df_reports.columns:
            descriptions = df_reports["detailed_description"].tolist()
            if descriptions:
                X_police = vectorizer.transform(descriptions)  # Inference
                pred_indices = model.predict(X_police)
                pred_categories = label_encoder.inverse_transform(pred_indices)
                df_reports["predicted_category"] = pred_categories
                df_reports["predicted_severity"] = df_reports["predicted_category"].apply(assign_severity)
                
            
                df_display = df_reports[[
                    "file", 
                    "report_number", 
                    "detailed_description", 
                    "predicted_category", 
                    "predicted_severity"
                ]].copy()

                # Convert severity to numeric
                df_display["predicted_severity"] = pd.to_numeric(
                    df_display["predicted_severity"], errors="coerce"
                )

      
                pd.set_option('display.max_colwidth', None)

                styled_table = (
                    df_display.style
                    .hide_index()
                    .set_properties(
                        subset=["detailed_description"],
                        **{"white-space": "pre-wrap"}  #  multiline text
                    )
                    .background_gradient(
                        cmap="YlOrRd",
                        subset=["predicted_severity"]
                    )
                )

                styled_html = styled_table.to_html(index=False)
                st.write(styled_html, unsafe_allow_html=True)

            else:
                st.write("No detailed descriptions found in the extracted reports.")
        else:
            st.write("Extraction did not produce any 'detailed_description' field.")

