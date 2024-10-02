import streamlit as st
import delta_sharing
import pandas as pd
import tempfile
import os

st.title("Delta Sharing Data Downloader")
st.write("Upload your config.share file to download the table as a CSV file.")

# File uploader for config.share
uploaded_file = st.file_uploader("Choose your config.share file", type="share")

if uploaded_file is not None:
    # Save the uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=".share") as temp_config:
        temp_config.write(uploaded_file.getvalue())
        temp_config_path = temp_config.name
    
    # Create a SharingClient
    client = delta_sharing.SharingClient(temp_config_path)
    
    # Get available shares
    shares = client.list_shares()
    
    # Let user select a share
    selected_share = st.selectbox("Select a share", [share.name for share in shares])
    
    if selected_share:
        # Get schemas for the selected share
        schemas = client.list_schemas(delta_sharing.Share(name=selected_share))
        
        # Let user select a schema
        selected_schema = st.selectbox("Select a schema", [schema.name for schema in schemas])
        
        if selected_schema:
            # Get tables for the selected schema
            tables = client.list_tables(delta_sharing.Schema(name=selected_schema, share=selected_share))
            
            # Let user select a table
            selected_table = st.selectbox("Select a table", [table.name for table in tables])
            
            if selected_table:
                # Construct the table url
                table_url = f"{temp_config_path}#{selected_share}.{selected_schema}.{selected_table}"
                
                # Read the table as a pandas DataFrame
                df = delta_sharing.load_as_pandas(table_url)
                
                # Create a temporary file for the CSV
                with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as temp_csv:
                    df.to_csv(temp_csv.name, index=False)
                    temp_csv_path = temp_csv.name
                
                # Create a download button
                with open(temp_csv_path, "rb") as file:
                    btn = st.download_button(
                        label="Download CSV",
                        data=file,
                        file_name="data.csv",
                        mime="text/csv"
                    )
                
                # Delete the temporary CSV file after download
                if btn:
                    os.remove(temp_csv_path)
                    st.success("Download complete! The temporary file has been deleted.")

    # Clean up the temporary config file
    os.remove(temp_config_path)