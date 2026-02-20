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

    

#     reader = easyocr.Reader(['en'], gpu=False)

#     # Read image
#     file_bytes = np.asarray(bytearray(file.read()), dtype=np.uint8)
#     img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

#     if img is None:
#         return pd.DataFrame()

#     gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
#     blur = cv2.GaussianBlur(gray, (3,3), 0)

#     # Adaptive threshold (better than simple threshold)
#     thresh = cv2.adaptiveThreshold(
#         blur, 255,
#         cv2.ADAPTIVE_THRESH_MEAN_C,
#         cv2.THRESH_BINARY_INV,
#         15, 4
#     )

#     # Detect horizontal lines
#     horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40,1))
#     detect_horizontal = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, horizontal_kernel)

#     # Detect vertical lines
#     vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1,40))
#     detect_vertical = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, vertical_kernel)

#     # Combine lines
#     table_mask = cv2.add(detect_horizontal, detect_vertical)

#     # Find contours (cells)
#     contours, _ = cv2.findContours(
#         table_mask,
#         cv2.RETR_TREE,
#         cv2.CHAIN_APPROX_SIMPLE
#     )

#     cells = []

#     for cnt in contours:
#         x, y, w, h = cv2.boundingRect(cnt)

#         # Filter small noise
#         if w < 40 or h < 20:
#             continue

#         cells.append((x, y, w, h))

#     if not cells:
#         return pd.DataFrame()

#     # Sort by Y then X
#     cells = sorted(cells, key=lambda b: (b[1], b[0]))

#     rows = []
#     current_row = []
#     last_y = None

#     for (x, y, w, h) in cells:
#         if last_y is None or abs(y - last_y) < 15:
#             current_row.append((x, y, w, h))
#         else:
#             rows.append(current_row)
#             current_row = [(x, y, w, h)]
#         last_y = y

#     if current_row:
#         rows.append(current_row)

#     # OCR each cell
#     table_data = []

#     for row in rows:
#         row = sorted(row, key=lambda b: b[0])
#         row_text = []

#         for (x, y, w, h) in row:
#             cell_img = img[y:y+h, x:x+w]

#             result = reader.readtext(cell_img)

#             text = " ".join([r[1] for r in result if r[2] > 0.4])

#             row_text.append(text.strip())

#         table_data.append(row_text)

#     df = pd.DataFrame(table_data)

#     # Remove fully empty rows
#     df = df[df.apply(lambda r: any(str(x).strip() != "" for x in r), axis=1)]

#     df.reset_index(drop=True, inplace=True)

#     return df

def image_to_df(file):

    

    reader = easyocr.Reader(['en'], gpu=False)

    # Read image
    file_bytes = np.asarray(bytearray(file.read()), dtype=np.uint8)
    img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

    if img is None:
        return pd.DataFrame()

    results = reader.readtext(img)

    if not results:
        return pd.DataFrame()

    # Collect boxes + text
    boxes = []
    for (bbox, text, conf) in results:
        if conf < 0.4:
            continue

        x_min = min([p[0] for p in bbox])
        y_min = min([p[1] for p in bbox])
        x_max = max([p[0] for p in bbox])
        y_max = max([p[1] for p in bbox])

        boxes.append({
            "text": text.strip(),
            "x": x_min,
            "y": y_min,
            "h": y_max - y_min
        })

    # Sort by Y first (row detection)
    boxes = sorted(boxes, key=lambda b: b["y"])

    rows = []
    current_row = []
    last_y = None
    row_threshold = 20  # controls row separation

    for box in boxes:
        if last_y is None:
            current_row.append(box)
            last_y = box["y"]
        elif abs(box["y"] - last_y) < row_threshold:
            current_row.append(box)
        else:
            rows.append(current_row)
            current_row = [box]
            last_y = box["y"]

    if current_row:
        rows.append(current_row)

    # Now sort each row by X (column order)
    table_data = []
    for row in rows:
        row_sorted = sorted(row, key=lambda b: b["x"])
        table_data.append([cell["text"] for cell in row_sorted])

    df = pd.DataFrame(table_data)

    df.reset_index(drop=True, inplace=True)

    return df









































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


