import streamlit as st
import os
import pandas as pd
from main import clean_dataframe, translate_hindi_df, pdf_to_df, image_to_df

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
        Upload your file and get a cleaned Excel with
        <b>Hindi → English conversion</b>,
        <b>phone normalization</b>,
        <b>pincode → state/district mapping</b>.
    </p>
    """,
    unsafe_allow_html=True
)

st.divider()

# ================= SIDEBAR =================
with st.sidebar:
    st.header("ℹ️ How it works")
    st.markdown(
        """
        **1. Upload** Excel / PDF / Image  
        **2. We process**  
        - Remove duplicates  
        - Normalize phone numbers  
        - Convert Hindi → English  
        - Add State & District from Pincode  
        **3. Download** cleaned Excel  

        ---
        **Supported formats**
        - `.xlsx`
        - `.pdf`
        - `.jpg`, `.png`
        """
    )

# ================= FILE UPLOAD =================
uploaded_file = st.file_uploader(
    "📤 Upload your file",
    type=["xlsx", "pdf", "jpg", "jpeg", "png"]
)

# ================= PROCESSING =================
if uploaded_file:
    os.makedirs("input", exist_ok=True)
    os.makedirs("output", exist_ok=True)

    input_path = os.path.join("input", uploaded_file.name)
    with open(input_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    st.success(f"✅ Uploaded: {uploaded_file.name}")
    st.caption(f"File size: {uploaded_file.size / 1024:.2f} KB")

    with st.spinner("🔄 Processing file... please wait"):
        if uploaded_file.name.lower().endswith(".xlsx"):
            df = pd.read_excel(input_path)

        elif uploaded_file.name.lower().endswith(".pdf"):
            df = pdf_to_df(input_path)

        else:
            df = image_to_df(input_path)

        if df.empty:
            st.error("❌ No table detected in the file.")
        else:
            df = clean_dataframe(df)
            df = translate_hindi_df(df)
            df.drop_duplicates(inplace=True)

            output_file = f"cleaned_{uploaded_file.name}.xlsx"
            output_path = os.path.join("output", output_file)
            df.to_excel(output_path, index=False)

    # ================= PREVIEW =================
    if not df.empty:
        st.subheader("👀 Data Preview (first 10 rows)")
        st.dataframe(df.head(10), use_container_width=True)

        # ================= DOWNLOAD =================
        with open(output_path, "rb") as f:
            st.download_button(
                label="⬇ Download Cleaned Excel",
                data=f,
                file_name=output_file,
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


# import streamlit as st
# import os
# import shutil
# import pandas as pd
# from main import clean_dataframe, translate_hindi_df, pdf_to_df, image_to_df

# st.set_page_config(page_title="Excel Data Cleaner", layout="centered")

# st.title("📄 Excel / PDF / Image Data Cleaner")
# st.write("Upload your file and download cleaned Excel")

# uploaded_file = st.file_uploader(
#     "Upload Excel / PDF / Image",
#     type=["xlsx", "pdf", "jpg", "jpeg", "png"]
# )

# if uploaded_file:
#     os.makedirs("input", exist_ok=True)
#     os.makedirs("output", exist_ok=True)

#     input_path = os.path.join("input", uploaded_file.name)
#     with open(input_path, "wb") as f:
#         f.write(uploaded_file.getbuffer())

#     if uploaded_file.name.endswith(".xlsx"):
#         df = pd.read_excel(input_path)
#     elif uploaded_file.name.endswith(".pdf"):
#         df = pdf_to_df(input_path)
#     else:
#         df = image_to_df(input_path)

#     if df.empty:
#         st.error("No table found in file")
#     else:
#         df = clean_dataframe(df)
#         df = translate_hindi_df(df)
#         df.drop_duplicates(inplace=True)

#         output_file = f"cleaned_{uploaded_file.name}.xlsx"
#         output_path = os.path.join("output", output_file)
#         df.to_excel(output_path, index=False)

#         with open(output_path, "rb") as f:
#             st.download_button(
#                 label="⬇ Download Cleaned Excel",
#                 data=f,
#                 file_name=output_file,
#                 mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
#             )
