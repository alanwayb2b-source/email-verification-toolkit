import io
import tempfile
from pathlib import Path

import pandas as pd
import streamlit as st

from email_cleaner import process_csv
from excel_cleaner import process_excel


st.set_page_config(
    page_title="Email Verification Toolkit",
    page_icon="📧",
    layout="wide",
)

st.title("📧 Email Verification Toolkit")
st.write(
    "Upload a CSV or Excel file, clean and validate email addresses, "
    "remove duplicates, and download the processed results."
)

uploaded_file = st.file_uploader(
    "Upload your file",
    type=["csv", "xlsx"],
)

if uploaded_file is not None:
    suffix = Path(uploaded_file.name).suffix.lower()

    try:
        if suffix == ".csv":
            preview_df = pd.read_csv(uploaded_file)
        elif suffix == ".xlsx":
            preview_df = pd.read_excel(uploaded_file)
        else:
            st.error("Unsupported file format.")
            st.stop()

        st.subheader("Input Preview")
        st.dataframe(preview_df.head(20), use_container_width=True)

        if "email" not in [str(col).strip().lower() for col in preview_df.columns]:
            st.error("The uploaded file must contain an 'email' column.")
            st.stop()

        if st.button("Process Emails", type="primary"):
            with st.spinner("Processing email records..."):
                with tempfile.TemporaryDirectory() as temp_dir:
                    temp_dir = Path(temp_dir)

                    input_path = temp_dir / uploaded_file.name
                    input_path.write_bytes(uploaded_file.getvalue())

                    if suffix == ".csv":
                        output_path = temp_dir / "processed_emails.csv"

                        process_csv(
                            str(input_path),
                            str(output_path),
                        )

                        result_df = pd.read_csv(output_path)
                        download_data = output_path.read_bytes()
                        mime_type = "text/csv"
                        download_name = "processed_emails.csv"

                    else:
                        output_path = temp_dir / "processed_emails.xlsx"

                        process_excel(
                            str(input_path),
                            str(output_path),
                        )

                        result_df = pd.read_excel(output_path)
                        download_data = output_path.read_bytes()
                        mime_type = (
                            "application/vnd.openxmlformats-officedocument."
                            "spreadsheetml.sheet"
                        )
                        download_name = "processed_emails.xlsx"

                    st.success(
                        f"Processing complete. "
                        f"{len(result_df)} unique records processed."
                    )

                    st.subheader("Processed Results")
                    st.dataframe(
                        result_df.head(100),
                        use_container_width=True,
                    )

                    st.download_button(
                        label="Download Processed File",
                        data=download_data,
                        file_name=download_name,
                        mime=mime_type,
                    )

    except Exception as exc:
        st.error(f"An error occurred: {exc}")