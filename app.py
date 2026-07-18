import tempfile
from pathlib import Path

import pandas as pd
import streamlit as st

from email_cleaner import process_csv
from excel_cleaner import process_excel


st.set_page_config(
    page_title="ZenBright Email Verification",
    page_icon="📧",
    layout="wide",
)


def add_final_status(df):
    def classify(row):
        email_status = str(row.get("email_status", ""))
        disposable = str(row.get("disposable_email", ""))
        mx_status = str(row.get("mx_status", ""))

        if email_status == "invalid_format":
            return "Invalid"

        if mx_status == "no_mx":
            return "Invalid"

        if disposable == "yes":
            return "Risky"

        if mx_status == "dns_error":
            return "Risky"

        if email_status == "valid_format" and mx_status == "valid_mx":
            return "Valid"

        return "Unknown"

    df["final_status"] = df.apply(classify, axis=1)
    return df


st.markdown(
    """
    <style>
    .main-title {
        font-size: 42px;
        font-weight: 700;
        margin-bottom: 0px;
    }

    .brand-name {
        font-size: 18px;
        font-weight: 600;
        margin-top: 0px;
        opacity: 0.8;
    }

    .subtitle {
        font-size: 18px;
        margin-bottom: 25px;
    }

    .footer {
        text-align: center;
        margin-top: 50px;
        padding-top: 20px;
        border-top: 1px solid #ddd;
        font-size: 14px;
        opacity: 0.7;
    }

    .notice {
        padding: 15px;
        border-radius: 8px;
        background-color: rgba(128,128,128,0.08);
        margin-top: 20px;
        margin-bottom: 20px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


st.markdown(
    '<div class="main-title">📧 ZenBright Email Verification</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="brand-name">Powered by ZenBright Data</div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="subtitle">
    Clean, validate, deduplicate, and analyze email addresses
    from CSV and Excel files.
    </div>
    """,
    unsafe_allow_html=True,
)


st.markdown(
    """
    <div class="notice">
    <strong>Verification Note:</strong>
    This tool checks email syntax, disposable domains, and MX/domain
    configuration. MX validation does not guarantee that an individual
    mailbox exists or can receive email.
    </div>
    """,
    unsafe_allow_html=True,
)


uploaded_file = st.file_uploader(
    "Upload CSV or Excel file",
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

        st.dataframe(
            preview_df.head(20),
            use_container_width=True,
        )

        email_columns = [
            str(col).strip().lower()
            for col in preview_df.columns
        ]

        if "email" not in email_columns:
            st.error(
                "The uploaded file must contain an 'email' column."
            )
            st.stop()

        if st.button(
            "Verify Emails",
            type="primary",
            use_container_width=True,
        ):

            with st.spinner(
                "Processing and verifying email records..."
            ):

                with tempfile.TemporaryDirectory() as temp_dir:

                    temp_dir = Path(temp_dir)

                    input_path = (
                        temp_dir / uploaded_file.name
                    )

                    input_path.write_bytes(
                        uploaded_file.getvalue()
                    )

                    if suffix == ".csv":

                        output_path = (
                            temp_dir / "verified_emails.csv"
                        )

                        process_csv(
                            str(input_path),
                            str(output_path),
                        )

                        result_df = pd.read_csv(
                            output_path
                        )

                        download_name = (
                            "zenbright_verified_emails.csv"
                        )

                        mime_type = "text/csv"

                    else:

                        output_path = (
                            temp_dir / "verified_emails.xlsx"
                        )

                        process_excel(
                            str(input_path),
                            str(output_path),
                        )

                        result_df = pd.read_excel(
                            output_path
                        )

                        download_name = (
                            "zenbright_verified_emails.xlsx"
                        )

                        mime_type = (
                            "application/vnd."
                            "openxmlformats-officedocument."
                            "spreadsheetml.sheet"
                        )

                    result_df = add_final_status(
                        result_df
                    )

                    total = len(result_df)

                    valid = (
                        result_df["final_status"]
                        .eq("Valid")
                        .sum()
                    )

                    invalid = (
                        result_df["final_status"]
                        .eq("Invalid")
                        .sum()
                    )

                    risky = (
                        result_df["final_status"]
                        .eq("Risky")
                        .sum()
                    )

                    disposable = (
                        result_df
                        .get(
                            "disposable_email",
                            pd.Series(dtype=str),
                        )
                        .eq("yes")
                        .sum()
                    )

                    valid_mx = (
                        result_df
                        .get(
                            "mx_status",
                            pd.Series(dtype=str),
                        )
                        .eq("valid_mx")
                        .sum()
                    )

                    no_mx = (
                        result_df
                        .get(
                            "mx_status",
                            pd.Series(dtype=str),
                        )
                        .eq("no_mx")
                        .sum()
                    )

                    st.success(
                        "Email verification completed successfully."
                    )

                    st.subheader(
                        "Verification Summary"
                    )

                    col1, col2, col3 = st.columns(3)

                    col1.metric(
                        "Total Emails",
                        total,
                    )

                    col2.metric(
                        "Valid",
                        valid,
                    )

                    col3.metric(
                        "Invalid",
                        invalid,
                    )

                    col4, col5, col6 = st.columns(3)

                    col4.metric(
                        "Risky",
                        risky,
                    )

                    col5.metric(
                        "Disposable",
                        disposable,
                    )

                    col6.metric(
                        "Valid MX",
                        valid_mx,
                    )

                    st.metric(
                        "No MX",
                        no_mx,
                    )

                    st.subheader(
                        "Verification Results"
                    )

                    st.dataframe(
                        result_df,
                        use_container_width=True,
                    )

                    if suffix == ".csv":

                        download_data = (
                            result_df
                            .to_csv(
                                index=False
                            )
                            .encode("utf-8")
                        )

                    else:

                        excel_output = (
                            temp_dir /
                            "zenbright_verified_final.xlsx"
                        )

                        result_df.to_excel(
                            excel_output,
                            index=False,
                        )

                        download_data = (
                            excel_output.read_bytes()
                        )

                    st.download_button(
                        label="Download Verified File",
                        data=download_data,
                        file_name=download_name,
                        mime=mime_type,
                        use_container_width=True,
                    )


    except Exception as exc:

        st.error(
            f"An error occurred: {exc}"
        )


st.markdown(
    """
    <div class="footer">
    © 2026 ZenBright Data · Email Verification Toolkit
    </div>
    """,
    unsafe_allow_html=True,
)