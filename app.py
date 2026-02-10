import streamlit as st
import pandas as pd
import io

from main import (
    clean_dataframe,
    translate_hindi_df,
    pdf_to_df,
    image_to_df
)

# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="Excel Data Cleaner",
    page_icon="📄",
    layout="centered"
)

# ================= HEADER =================
st.markdown(
    """
    <h1 style="text-align:center;">📄 Excel / PDF / Image Data Cleaner</h1>
    <p style="text-align:center;">
        Clean your data with <b>Hindi → English</b>,
        <b>Phone normalization</b> and
        <b>Pincode → State/District</b> mapping.
    </p>
    """,
    unsafe_allow_html=True
)

st.divider()

# ================= SIDEBAR =================
with st.sidebar:
    st.header("ℹ️ Features")
    st.markdown(
        """
        ✔ Hindi → English conversion  
        ✔ Phone number normalization  
        ✔ Pincode → State & District  
        ✔ No row deletion  
        ✔ Excel / PDF / Image support  

        ---
        **Supported formats**
        - `.xlsx`
        - `.pdf`
        - `.jpg`, `.png`
        """
    )

translate_on = st.sidebar.checkbox(
    "🔤 Translate Hindi to English",
    value=True
)

st.divider()

# ======================================================
# 🔹 SECTION 1: SINGLE FILE UPLOAD
# ======================================================
st.subheader("📁 Single File Upload")

single_file = st.file_uploader(
    "Upload one Excel / PDF / Image",
    type=["xlsx", "pdf", "jpg", "jpeg", "png"],
    key="single"
)

if single_file:
    with st.spinner("🔄 Processing file..."):
        if single_file.name.lower().endswith(".xlsx"):
            df = pd.read_excel(single_file)
        elif single_file.name.lower().endswith(".pdf"):
            df = pdf_to_df(single_file)
        else:
            df = image_to_df(single_file)

        if df.empty:
            st.error("❌ No data detected in file.")
        else:
            df = clean_dataframe(df)
            if translate_on:
                df = translate_hindi_df(df)

            df.drop_duplicates(inplace=True)

            st.success(f"✅ Rows processed: {len(df)}")
            st.dataframe(df.head(10), use_container_width=True)

            # ---- Excel download (BytesIO FIX) ----
            buffer = io.BytesIO()
            df.to_excel(buffer, index=False)
            buffer.seek(0)

            output_name = f"cleaned_{single_file.name}.xlsx"
            st.download_button(
                "⬇ Download Cleaned Excel",
                data=buffer,
                file_name=output_name,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

st.divider()

# ======================================================
# 🔹 SECTION 2: MULTIPLE FILE UPLOAD
# ======================================================
st.subheader("📂 Multiple Files Upload")

multi_files = st.file_uploader(
    "Upload multiple Excel / PDF / Images",
    type=["xlsx", "pdf", "jpg", "jpeg", "png"],
    accept_multiple_files=True,
    key="multiple"
)

if multi_files:
    all_dfs = []

    with st.spinner("🔄 Processing multiple files..."):
        for file in multi_files:
            if file.name.lower().endswith(".xlsx"):
                df = pd.read_excel(file)
            elif file.name.lower().endswith(".pdf"):
                df = pdf_to_df(file)
            else:
                df = image_to_df(file)

            if df.empty:
                continue

            df = clean_dataframe(df)
            if translate_on:
                df = translate_hindi_df(df)

            all_dfs.append(df)

    if not all_dfs:
        st.error("❌ No valid data found in uploaded files.")
    else:
        final_df = pd.concat(all_dfs, ignore_index=True)
        final_df.drop_duplicates(inplace=True)

        st.success(f"✅ Total rows after merge: {len(final_df)}")
        st.dataframe(final_df.head(10), use_container_width=True)

        # ---- Excel download (BytesIO FIX) ----
        buffer = io.BytesIO()
        final_df.to_excel(buffer, index=False)
        buffer.seek(0)

        st.download_button(
            "⬇ Download Combined Cleaned Excel",
            data=buffer,
            file_name="cleaned_multiple_files.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

# ================= FOOTER =================
st.divider()
st.markdown(
    """
    <p style="text-align:center; font-size: 0.9em;">
        Built with ❤️ using Python & Streamlit<br>
        © 2026
    </p>
    """,
    unsafe_allow_html=True
)

