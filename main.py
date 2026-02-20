import os
import re
import pandas as pd
import pytesseract
import pdfplumber
from PIL import Image


import cv2
import numpy as np

# import pytesseract

# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

import easyocr

reader = easyocr.Reader(['en'], gpu=False)


# ================= HINDI TO ENGLISH =================
from googletrans import Translator
from indic_transliteration import sanscript
from indic_transliteration.sanscript import transliterate

translator = Translator()
DEVANAGARI_REGEX = re.compile(r"[\u0900-\u097F]")

def is_hindi(text):
    return isinstance(text, str) and bool(DEVANAGARI_REGEX.search(text))

def transliterate_hindi(text):
    try:
        return transliterate(text, sanscript.DEVANAGARI, sanscript.ITRANS).title()
    except Exception:
        return text

def translate_hindi(text):
    if not text or len(str(text)) < 4:
        return text
    try:
        translated = translator.translate(text, src="hi", dest="en").text
        return translated if not is_hindi(translated) else transliterate_hindi(text)
    except Exception:
        return transliterate_hindi(text)

def translate_hindi_df(df):
    df = df.copy()
    cache = {}
    for col in df.columns:
        if df[col].dtype == object:
            for i, val in df[col].items():
                if is_hindi(val):
                    if val not in cache:
                        cache[val] = translate_hindi(val)
                    df.at[i, col] = cache[val]
    return df

# ================= PINCODE MASTER =================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PINCODE_FILE = os.path.join(BASE_DIR, "allStateData.csv")

pin_df = pd.read_csv(PINCODE_FILE, header=None, dtype=str)
pin_df = pin_df[[4, 7, 8]]
pin_df.columns = ["pincode", "district", "state"]

pin_df["pincode"] = pin_df["pincode"].astype(str).str.strip()
pin_df = pin_df[pin_df["pincode"].str.fullmatch(r"\d{6}")]
pin_df = pin_df.drop_duplicates(subset="pincode", keep="first")

# ✅ CRITICAL FIX
PINCODE_LOOKUP = (
    pin_df
    .set_index("pincode")[["state", "district"]]
    .to_dict("index")
)

# ================= HELPERS =================
def normalize_phone(val):
    digits = re.sub(r"\D", "", str(val)) if val else ""
    return digits[-10:] if len(digits) >= 10 else ""

def clean_pincode(val):
    if not val:
        return ""
    m = re.search(r"\b\d{6}\b", str(val))
    return m.group(0) if m else ""

# ================= CLEAN DATAFRAME =================
# def clean_dataframe(df):
#     df = df.copy()

#     col_map = {c: re.sub(r"[^a-z0-9]", "", c.lower()) for c in df.columns}

#     pin_cols = [c for c, n in col_map.items() if "pin" in n]
#     state_cols = [c for c, n in col_map.items() if n == "state"]
#     dist_cols = [c for c, n in col_map.items() if "district" in n]

#     # Normalize phone numbers
#     for col, cname in col_map.items():
#         if "phone" in cname or "mobile" in cname:
#             df[col] = df[col].apply(normalize_phone)

#     if not pin_cols:
#         return df

#     pcol = pin_cols[0]
#     df[pcol] = df[pcol].apply(clean_pincode)

#     state_col = state_cols[0] if state_cols else "State"
#     dist_col = dist_cols[0] if dist_cols else "District"

#     if state_col not in df.columns:
#         df[state_col] = ""
#     if dist_col not in df.columns:
#         df[dist_col] = ""

#     for i, pin in df[pcol].items():
#         info = PINCODE_LOOKUP.get(pin)
#         if info:
#             if not str(df.at[i, state_col]).strip():
#                 df.at[i, state_col] = info["state"]
#             if not str(df.at[i, dist_col]).strip():
#                 df.at[i, dist_col] = info["district"]

#     return df

def clean_dataframe(df):
    df = df.copy()

    # ✅ Convert all column names to string first
    df.columns = df.columns.map(str)

    # Normalize column names
    col_map = {
        c: re.sub(r"[^a-z0-9]", "", str(c).lower())
        for c in df.columns
    }

    pin_cols = [c for c, n in col_map.items() if "pin" in n]
    state_cols = [c for c, n in col_map.items() if n == "state"]
    dist_cols = [c for c, n in col_map.items() if "district" in n]

    # Normalize phone numbers
    for col, cname in col_map.items():
        if "phone" in cname or "mobile" in cname:
            df[col] = df[col].apply(normalize_phone)

    # If no pincode column found, just return cleaned dataframe
    if not pin_cols:
        return df

    pcol = pin_cols[0]
    df[pcol] = df[pcol].apply(clean_pincode)

    state_col = state_cols[0] if state_cols else "State"
    dist_col = dist_cols[0] if dist_cols else "District"

    if state_col not in df.columns:
        df[state_col] = ""
    if dist_col not in df.columns:
        df[dist_col] = ""

    for i, pin in df[pcol].items():
        info = PINCODE_LOOKUP.get(pin)
        if info:
            if not str(df.at[i, state_col]).strip():
                df.at[i, state_col] = info["state"]
            if not str(df.at[i, dist_col]).strip():
                df.at[i, dist_col] = info["district"]

    return df


# ================= PDF / IMAGE =================
def pdf_to_df(file):
    tables = []
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            table = page.extract_table()
            if table:
                tables.append(pd.DataFrame(table[1:], columns=table[0]))
    return pd.concat(tables, ignore_index=True) if tables else pd.DataFrame()



# def image_to_df(file):
#     file_bytes = np.asarray(bytearray(file.read()), dtype=np.uint8)
#     img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

#     gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
#     thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)[1]

#     text = pytesseract.image_to_string(thresh, config="--psm 6")

#     lines = [line.strip() for line in text.split("\n") if line.strip()]

#     data = []

#     for line in lines:
#         parts = line.split()

#         if len(parts) >= 4:

#             # Remove row numbers if present
#             if parts[0].isdigit():
#                 parts = parts[1:]

#             customer_id = parts[0]
#             region = parts[-1]
#             gender = parts[-2]
#             customer = " ".join(parts[1:-2])

#             data.append([customer_id, customer, gender, region])

#     if not data:
#         return pd.DataFrame()

#     df = pd.DataFrame(
#         data,
#         columns=["Customer ID", "Customer", "Gender", "Region"]
#     )

#     return df

# def image_to_df(file):

#     # Convert uploaded file to OpenCV image
#     file_bytes = np.asarray(bytearray(file.read()), dtype=np.uint8)
#     img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

#     if img is None:
#         return pd.DataFrame()

#     # Preprocessing
#     gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
#     gray = cv2.GaussianBlur(gray, (3, 3), 0)

#     # Proper threshold fix
#     _, thresh = cv2.threshold(gray, 170, 255, cv2.THRESH_BINARY)

#     # OCR
#     text = pytesseract.image_to_string(thresh, config="--psm 6")

#     # Split into lines
#     lines = [line.strip() for line in text.split("\n") if line.strip()]

#     if not lines:
#         return pd.DataFrame()

#     table = []

#     for line in lines:
#         words = line.split()

#         # Skip ribbon/menu noise (very small lines)
#         if len(words) < 2:
#             continue

#         table.append(words)

#     if not table:
#         return pd.DataFrame()

#     # Prevent 70+ column explosion
#     max_cols = min(max(len(r) for r in table), 12)

#     cleaned_table = []
#     for row in table:
#         row = row[:max_cols]
#         row += [""] * (max_cols - len(row))
#         cleaned_table.append(row)

#     df = pd.DataFrame(cleaned_table)

#     return df

def image_to_df(file):

    import numpy as np
    import pandas as pd
    import cv2

    file_bytes = np.asarray(bytearray(file.read()), dtype=np.uint8)
    img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

    if img is None:
        return pd.DataFrame()

    h, w, _ = img.shape

    # Crop top ribbon
    cropped = img[int(h * 0.25):h, :]

    results = reader.readtext(cropped)

    words = []

    for (bbox, text, prob) in results:
        if prob > 0.5:
            x = bbox[0][0]
            y = bbox[0][1]
            words.append((y, x, text.strip()))

    if not words:
        return pd.DataFrame()

    # Sort by Y then X
    words.sort(key=lambda x: (x[0], x[1]))

    # Group into rows
    rows = []
    current_row = []
    last_y = None

    for y, x, text in words:
        if last_y is None or abs(y - last_y) < 20:
            current_row.append((x, text))
        else:
            rows.append(current_row)
            current_row = [(x, text)]
        last_y = y

    if current_row:
        rows.append(current_row)

    # Collect all X positions
    all_x = []
    for row in rows:
        for x, _ in row:
            all_x.append(x)

    if not all_x:
        return pd.DataFrame()

    # Cluster X positions dynamically
    all_x.sort()
    columns = []

    threshold = 40  # column gap sensitivity

    for x in all_x:
        placed = False
        for col in columns:
            if abs(col - x) < threshold:
                placed = True
                break
        if not placed:
            columns.append(x)

    columns.sort()

    # Build structured table
    table = []

    for row in rows:
        row_data = [""] * len(columns)
        for x, text in row:
            for i, col_x in enumerate(columns):
                if abs(col_x - x) < threshold:
                    row_data[i] = text
                    break
        table.append(row_data)

    df = pd.DataFrame(table)

    # Remove empty rows
    df = df.dropna(how="all")
    df = df[df.apply(lambda r: any(str(x).strip() != "" for x in r), axis=1)]

    return df.reset_index(drop=True)










































#iske uper or feature wala code 

# import os
# import re
# import pandas as pd
# import pytesseract
# import pdfplumber
# from PIL import Image

# # ================= HINDI TO ENGLISH =================
# from googletrans import Translator
# from indic_transliteration import sanscript
# from indic_transliteration.sanscript import transliterate

# translator = Translator()
# DEVANAGARI_REGEX = re.compile(r"[\u0900-\u097F]")

# def is_hindi(text):
#     return isinstance(text, str) and bool(DEVANAGARI_REGEX.search(text))

# def transliterate_hindi(text):
#     try:
#         return transliterate(text, sanscript.DEVANAGARI, sanscript.ITRANS).title()
#     except Exception:
#         return text

# def translate_hindi(text):
#     if not text or len(str(text)) < 4:
#         return text
#     try:
#         translated = translator.translate(text, src="hi", dest="en").text
#         return translated if not is_hindi(translated) else transliterate_hindi(text)
#     except Exception:
#         return transliterate_hindi(text)

# def translate_hindi_df(df):
#     df = df.copy()
#     cache = {}

#     for col in df.columns:
#         if df[col].dtype == object:
#             for i, val in df[col].items():
#                 if is_hindi(val):
#                     if val not in cache:
#                         cache[val] = translate_hindi(val)
#                     df.at[i, col] = cache[val]
#     return df

# # ================= PATH SETUP =================
# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# PINCODE_FILE = os.path.join(BASE_DIR, "allStateData.csv")

# # ================= LOAD PINCODE MASTER =================
# pin_df = pd.read_csv(PINCODE_FILE, header=None, dtype=str)

# PIN_COL = 4
# DIST_COL = 7
# STATE_COL = 8

# pin_df = pin_df[[PIN_COL, DIST_COL, STATE_COL]]
# pin_df.columns = ["pincode", "district", "state"]

# pin_df["pincode"] = pin_df["pincode"].astype(str).str.strip()
# pin_df = pin_df[pin_df["pincode"].str.fullmatch(r"\d{6}")]
# pin_df = pin_df.drop_duplicates(subset="pincode", keep="first")

# PINCODE_LOOKUP = pin_df.set_index("pincode")

# # ================= HELPERS =================
# def normalize_phone(val):
#     digits = re.sub(r"\D", "", str(val)) if val else ""
#     return digits[-10:] if len(digits) >= 10 else ""

# def clean_pincode(val):
#     if not val:
#         return ""
#     m = re.search(r"\b\d{6}\b", str(val))
#     return m.group(0) if m else ""

# # ================= CLEAN DATAFRAME (FINAL SAFE VERSION) =================
# def clean_dataframe(df):
#     df = df.copy()

#     col_map = {c: re.sub(r"[^a-z0-9]", "", c.lower()) for c in df.columns}

#     pin_cols = [c for c, n in col_map.items() if "pin" in n]
#     state_cols = [c for c, n in col_map.items() if n == "state"]
#     dist_cols = [c for c, n in col_map.items() if "district" in n]

#     # Normalize phone numbers
#     for col, cname in col_map.items():
#         if "phone" in cname or "mobile" in cname:
#             df[col] = df[col].apply(normalize_phone)

#     if not pin_cols:
#         return df

#     pcol = pin_cols[0]
#     df[pcol] = df[pcol].apply(clean_pincode)

#     # Decide state/district columns
#     state_col = state_cols[0] if state_cols else "State"
#     dist_col = dist_cols[0] if dist_cols else "District"

#     if state_col not in df.columns:
#         df[state_col] = ""

#     if dist_col not in df.columns:
#         df[dist_col] = ""

#     # Fill state/district ONLY when empty AND pincode valid
#     for i, pin in df[pcol].items():
#         if pin in PINCODE_LOOKUP.index:
#             if not str(df.at[i, state_col]).strip():
#                 df.at[i, state_col] = PINCODE_LOOKUP.loc[pin, "state"]
#             if not str(df.at[i, dist_col]).strip():
#                 df.at[i, dist_col] = PINCODE_LOOKUP.loc[pin, "district"]

#     return df

# # ================= PDF TABLE TO DF =================
# def pdf_to_df(path):
#     tables = []
#     with pdfplumber.open(path) as pdf:
#         for page in pdf.pages:
#             table = page.extract_table()
#             if table:
#                 tables.append(pd.DataFrame(table[1:], columns=table[0]))
#     return pd.concat(tables, ignore_index=True) if tables else pd.DataFrame()

# # ================= IMAGE TABLE TO DF =================
# def image_to_df(path):
#     data = pytesseract.image_to_data(
#         Image.open(path),
#         output_type=pytesseract.Output.DATAFRAME
#     )
#     data = data.dropna(subset=["text"])

#     rows = {}
#     for _, row in data.iterrows():
#         key = (row["block_num"], row["line_num"])
#         rows.setdefault(key, []).append(row["text"])

#     return pd.DataFrame({"pincode": [" ".join(v) for v in rows.values()]})






































# import os
# import re
# import pandas as pd
# import pytesseract
# import pdfplumber
# from PIL import Image

# # ================= PATH SETUP =================
# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# INPUT_DIR = os.path.join(BASE_DIR, "input")
# OUTPUT_DIR = os.path.join(BASE_DIR, "output")
# PINCODE_FILE = os.path.join(BASE_DIR, "allStateData.csv")

# os.makedirs(OUTPUT_DIR, exist_ok=True)

# # Uncomment if needed
# # pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# # ================= LOAD PINCODE MASTER =================
# pin_df = pd.read_csv(PINCODE_FILE, header=None, dtype=str)

# # Fixed structure of your CSV
# PIN_COL = 4
# DIST_COL = 7
# STATE_COL = 8

# pin_df = pin_df[[PIN_COL, DIST_COL, STATE_COL]]
# pin_df.columns = ["pincode", "district", "state"]

# pin_df["pincode"] = pin_df["pincode"].astype(str).str.strip()
# pin_df = pin_df[pin_df["pincode"].str.isdigit() & (pin_df["pincode"].str.len() == 6)]
# pin_df = pin_df.drop_duplicates(subset="pincode", keep="first")

# PINCODE_LOOKUP = pin_df.set_index("pincode")[["state", "district"]].to_dict("index")

# print(f"✔ Loaded {len(PINCODE_LOOKUP)} pincodes")

# # ================= PHONE NORMALIZATION =================
# def normalize_phone(val):
#     if val is None:
#         return ""
#     digits = re.sub(r"\D", "", str(val))
#     if len(digits) >= 10:
#         return digits[-10:]
#     return ""

# # ================= PINCODE CLEAN =================
# def clean_pincode(val):
#     if val is None:
#         return ""
#     val = str(val).strip()
#     return val if val.isdigit() and len(val) == 6 else ""

# # ================= CLEAN DATAFRAME =================
# def clean_dataframe(df):
#     df = df.copy()

#     # Normalize column names (for detection only)
#     col_map = {c: re.sub(r"[^a-z0-9]", "", c.lower()) for c in df.columns}

#     # 🔥 DROP CITY COLUMN COMPLETELY
#     for col, cname in col_map.items():
#         if cname.startswith("city"):
#             df.drop(columns=[col], inplace=True)
#             break

#     # 📞 PHONE NORMALIZATION
#     for col, cname in col_map.items():
#         if "phone" in cname or "mobile" in cname:
#             df[col] = df[col].apply(normalize_phone)

#     # 📍 PINCODE → STATE & DISTRICT
#     pin_cols = [c for c, cname in col_map.items() if "pin" in cname]
#     if not pin_cols:
#         return df

#     pcol = pin_cols[0]
#     df[pcol] = df[pcol].apply(clean_pincode)

#     df["State"] = ""
#     df["District"] = ""

#     for i, pin in df[pcol].items():
#         if pin in PINCODE_LOOKUP:
#             df.at[i, "State"] = PINCODE_LOOKUP[pin]["state"]
#             df.at[i, "District"] = PINCODE_LOOKUP[pin]["district"]

#     return df

# # ================= PDF TABLE TO DF =================
# def pdf_to_df(path):
#     tables = []
#     with pdfplumber.open(path) as pdf:
#         for page in pdf.pages:
#             table = page.extract_table()
#             if table:
#                 tables.append(pd.DataFrame(table[1:], columns=table[0]))
#     return pd.concat(tables, ignore_index=True) if tables else pd.DataFrame()

# # ================= IMAGE TABLE TO DF =================
# def image_to_df(path):
#     data = pytesseract.image_to_data(
#         Image.open(path),
#         output_type=pytesseract.Output.DATAFRAME
#     )
#     data = data.dropna(subset=["text"])

#     rows = {}
#     for _, row in data.iterrows():
#         key = (row["block_num"], row["line_num"])
#         rows.setdefault(key, []).append(row["text"])

#     table = [" ".join(v) for v in rows.values()]
#     return pd.DataFrame({"pincode": table})

# # ================= MAIN PROCESS =================
# def process_files():
#     for file in os.listdir(INPUT_DIR):
#         path = os.path.join(INPUT_DIR, file)

#         try:
#             if file.lower().endswith(".xlsx"):
#                 print(f"Processing Excel: {file}")
#                 df = pd.read_excel(path)

#             elif file.lower().endswith(".pdf"):
#                 print(f"Processing PDF: {file}")
#                 df = pdf_to_df(path)

#             elif file.lower().endswith((".jpg", ".jpeg", ".png")):
#                 print(f"Processing Image: {file}")
#                 df = image_to_df(path)

#             else:
#                 continue

#             if df.empty:
#                 print("⚠ No table found")
#                 continue

#             df = clean_dataframe(df)
#             df.drop_duplicates(inplace=True)

#             output_path = os.path.join(
#                 OUTPUT_DIR, f"cleaned_{os.path.splitext(file)[0]}.xlsx"
#             )
#             df.to_excel(output_path, index=False)

#             print(f"✅ Saved: {output_path}")

#         except Exception as e:
#             print(f"❌ Failed {file}: {e}")

# # ================= RUN =================
# if __name__ == "__main__":
#     process_files()


