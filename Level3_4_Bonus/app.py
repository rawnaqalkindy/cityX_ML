import streamlit as st
import pandas as pd
from model import load_and_train_model, assign_severity
import level3
import level4
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, DataReturnMode

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
        map_html = level3.create_map()
        st.components.v1.html(map_html, height=600, scrolling=True)

elif section == "Level 4: Report Classification":
    with st.spinner("Loading Report..."):
        st.header("Police Report Classification")
        df_reports = level4.process_reports()
        
        if 'detailed_description' in df_reports.columns:
            descriptions = df_reports["detailed_description"].tolist()
            if descriptions:
                # Inference
                X_police = vectorizer.transform(descriptions)
                pred_indices = model.predict(X_police)
                pred_categories = label_encoder.inverse_transform(pred_indices)

                df_reports["predicted_category"] = pred_categories
                df_reports["predicted_severity"] = df_reports["predicted_category"].apply(assign_severity)
                
                # KPI Summary Cards at the top using columns and metric functions
                total_reports = len(df_reports)
                avg_severity = df_reports["predicted_severity"].astype(float).mean()
                common_category = df_reports["predicted_category"].mode()[0] if not df_reports["predicted_category"].mode().empty else "N/A"
                
                col1, col2, col3 = st.columns(3)
                col1.metric("Total Reports", total_reports)
                col2.metric("Avg. Severity", f"{avg_severity:.2f} / 5")
                col3.metric("Most Common Category", common_category)
                
                # Interactive Filters
                unique_categories = sorted(df_reports["predicted_category"].unique().tolist())
                selected_categories = st.multiselect("Filter by Category", unique_categories, default=unique_categories)
                filtered_df = df_reports[df_reports["predicted_category"].isin(selected_categories)]
                
                # Tabbed Layout for Summary and Detailed Table
                tab1, tab2 = st.tabs(["Summary", "Detailed View"])
                with tab1:
                    st.subheader("Overview")
                    st.write("Overall statstics of the reports")
                    st.metric("Total Reports ", len(filtered_df))
                    if len(filtered_df) > 0:
                        avg_filtered_severity = filtered_df["predicted_severity"].astype(float).mean()
                        st.metric("Avg. Severity ", f"{avg_filtered_severity:.2f}")
                    else:
                        st.metric("Avg. Severity ", "N/A")
                with tab2:
                    df_display = filtered_df[[
                        "file", 
                        "report_number", 
                        "detailed_description", 
                        "predicted_category", 
                        "predicted_severity"
                    ]].copy()   

                    # Rename the columns to new titles
                    df_display.rename(columns={
                        "file": "File Number",
                        "report_number": "Report Number",
                        "detailed_description": "Description",
                        "predicted_category": "Predicted Category",
                        "predicted_severity": "Predicted Severity"
                    }, inplace=True)

                    # Convert severity to numeric
                    df_display["Predicted Severity"] = pd.to_numeric(
                        df_display["Predicted Severity"], errors="coerce"
                    )
                    gb = GridOptionsBuilder.from_dataframe(df_display)

                    gb.configure_default_column(
                        editable=False,
                        wrapText=True,
                        autoHeight=True,
                        sortable=False
                    )

                    gb.configure_column("Predicted Severity", sortable=True)
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

