import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, DataReturnMode, JsCode
from model import load_and_train_model, assign_severity
import level3
import level4

st.set_page_config(page_title="CityX Crime Dashboard", layout="wide")
st.sidebar.title("CityX Crime Dashboard")
section = st.sidebar.radio(
    "Choose a Section",
    ["Level 3: Geo-Spatial Mapping", "Level 4: Report Classification"]
)

# Load model
vectorizer, model, label_encoder = load_and_train_model()

severity_color = JsCode("""
function(params) {
    if (params.value == null) {
        return {'backgroundColor': '#ffffff'};
    }
    switch(params.value) {
        case 1:
            return {'backgroundColor': '#ffff99'}; // Light Yellow
        case 2:
            return {'backgroundColor': '#ffcc66'}; // Orange
        case 3:
            return {'backgroundColor': '#ff9966'}; // Darker Orange
        case 4:
            return {'backgroundColor': '#ff6666'}; // Red
        default:
            return {'backgroundColor': '#ffffff'};
    }
};
""")

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
                # Run inference
                X_police = vectorizer.transform(descriptions)
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

  
                df_display.reset_index(drop=True, inplace=True)
                gb = GridOptionsBuilder.from_dataframe(df_display)

                gb.configure_default_column(
                    editable=False,
                    wrapText=True,
                    autoHeight=True,
                    sortable=False,
                    filter=False
                )

                # predicted_severity sortable + numeric filter + color styling
                gb.configure_column(
                    "predicted_severity",
                    sortable=True,
                    filter="agNumberColumnFilter",  # allows >=, <=, etc.
                    cellStyle=severity_color
                )

                gb.configure_pagination(paginationAutoPageSize=True)
                gb.configure_side_bar()

                grid_options = gb.build()

                AgGrid(
                    df_display,
                    gridOptions=grid_options,
                    data_return_mode=DataReturnMode.AS_INPUT,
                    update_mode=GridUpdateMode.MODEL_CHANGED,
                    fit_columns_on_grid_load=True,
                    theme="streamlit",
                    enable_enterprise_modules=False
                )

            else:
                st.write("No detailed descriptions found in the extracted reports.")
        else:
            st.write("Extraction did not produce any 'detailed_description' field.")
