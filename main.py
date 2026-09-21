import os
import re
import io
import pandas as pd
import numpy as np
import pdfplumber
import streamlit as st

import cv2

from rapidfuzz import fuzz, process
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

import easyocr

from googletrans import Translator
from indic_transliteration import sanscript
from indic_transliteration.sanscript import transliterate

os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PINCODE_FILE = os.path.join(BASE_DIR, "allStateData.csv")
DEVANAGARI_REGEX = re.compile(r"[ऀ-ॿ]")


# ================= OCR (lazy, cached) =================
@st.cache_resource
def load_reader():
    return easyocr.Reader(['en'], gpu=False)


# ================= HINDI -> ENGLISH =================
translator = Translator()


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
def _load_pincode_lookup():
    pin_df = pd.read_csv(PINCODE_FILE, header=None, dtype=str)
    pin_df = pin_df[[4, 7, 8]]
    pin_df.columns = ["pincode", "district", "state"]

    pin_df["pincode"] = pin_df["pincode"].astype(str).str.strip()
    pin_df = pin_df[pin_df["pincode"].str.fullmatch(r"\d{6}")]
    pin_df = pin_df.drop_duplicates(subset="pincode", keep="first")

    return pin_df.set_index("pincode")[["state", "district"]].to_dict("index")


PINCODE_LOOKUP = _load_pincode_lookup()


# ================= UNIVERSAL FIELD DETECTION =================
# Header keywords span common vocabularies across retail, healthcare, real
# estate, finance/accounting, HR, education, logistics and government forms,
# so the same detector works regardless of which industry a sheet came from.
FIELD_KEYWORDS = {
    "name": ["fullname", "name", "customername", "clientname", "contactperson",
             "employeename", "studentname", "patientname", "applicant", "personname",
             "ownername", "candidatename", "membername", "owner", "tenant", "landlord"],
    "phone": ["phone", "mobile", "contact", "telephone", "tel", "cell", "whatsapp",
              "phoneno", "mobileno", "contactno"],
    "email": ["email", "mail", "emailid", "emailaddress"],
    "address": ["address", "addr", "location", "street", "locality", "area", "landmark"],
    "city": ["city", "town", "village"],
    "district": ["district", "taluka", "tehsil"],
    "state": ["state", "province"],
    "country": ["country", "nation"],
    "pincode": ["pincode", "pinno", "pin", "zipcode", "zip", "postalcode"],
    "company": ["company", "organisation", "organization", "firm", "business",
                "employer", "vendor", "supplier", "enterprise"],
    "designation": ["designation", "jobtitle", "role", "position", "occupation"],
    "gender": ["gender", "sex"],
    "age": ["age"],
    "dob": ["dob", "dateofbirth", "birthdate"],
    "date": ["date", "createdon", "updatedon", "joiningdate", "invoicedate",
             "orderdate", "duedate", "timestamp", "deliverydate"],
    "amount": ["amount", "price", "cost", "salary", "revenue", "total", "fee",
               "charge", "balance", "payment", "invoiceamount", "budget",
               "turnover", "mrp", "rate"],
    "gst": ["gstin", "gstnumber", "gst"],
    "pan": ["pannumber", "pancard", "pan"],
    "aadhaar": ["aadhaar", "aadhar", "uidai", "uid"],
    "website": ["website", "url", "weblink", "site"],
    "product": ["productname", "itemname", "product", "item", "sku", "material"],
    "quantity": ["quantity", "qty", "units", "stock"],
    "category": ["category", "segment", "department", "class", "type"],
    "status": ["status", "stage"],
    "id": ["referenceno", "serialno", "id", "code", "regno", "rollno"],
}

# Extra vocabulary per industry, merged on top of FIELD_KEYWORDS when a
# preset is selected. Lets the same engine give sharper detection on a
# sheet's typical layout without hardcoding any single industry by default.
INDUSTRY_KEYWORDS = {
    "Retail / E-commerce": {
        "product": ["variant", "brand", "barcode"],
        "quantity": ["cartons", "unitssold"],
        "amount": ["sellingprice", "discount", "taxamount", "mrp"],
        "status": ["orderstatus", "paymentstatus", "deliverystatus", "returnstatus"],
    },
    "Healthcare": {
        "name": ["patientname", "doctorname"],
        "diagnosis": ["diagnosis", "disease", "symptom", "treatment", "medicine", "dosage", "ward"],
        "id": ["patientid", "mrno", "opdno", "ipdno"],
        "date": ["admissiondate", "dischargedate", "appointmentdate"],
        "blood_group": ["bloodgroup", "bloodtype"],
        "amount": ["billamount", "consultationfee", "insuranceamount"],
    },
    "Real Estate": {
        "property_type": ["propertytype", "plottype", "unittype", "bhk"],
        "amount": ["propertyvalue", "rent", "deposit", "emi", "maintenance"],
        "address": ["projectname", "builder", "society", "tower"],
        "quantity": ["carpetarea", "builtuparea", "sqft", "plotarea"],
        "date": ["possessiondate", "registrationdate"],
        "id": ["reranumber", "surveyno", "khatanumber"],
    },
    "HR / Payroll": {
        "id": ["employeeid", "empid", "staffid"],
        "amount": ["ctc", "grosssalary", "netsalary", "basicpay", "hra", "pf", "esic", "bonus"],
        "date": ["joiningdate", "relievingdate"],
        "designation": ["grade", "band", "level"],
    },
    "Education": {
        "id": ["rollno", "admissionno", "studentid", "enrollmentno"],
        "name": ["studentname", "fathername", "mothername", "guardianname"],
        "grade": ["grade", "marks", "percentage", "cgpa", "class", "section", "semester"],
        "date": ["admissiondate", "examdate"],
        "amount": ["feeamount", "scholarship"],
    },
    "Logistics": {
        "id": ["trackingid", "awbnumber", "consignmentno", "shipmentid"],
        "name": ["drivername", "consignee", "consignor"],
        "address": ["origin", "destination", "warehouse", "pickuplocation", "deliverylocation"],
        "date": ["pickupdate", "dispatchdate"],
        "amount": ["freight", "shippingcost"],
        "status": ["shipmentstatus"],
    },
}

INDUSTRY_PRESETS = ["Generic (Auto-detect)"] + list(INDUSTRY_KEYWORDS.keys())

# Field types beyond the generic set that only show up once an industry
# preset adds their keywords; cleaned the same way as other free-text fields.
_TEXT_FIELD_TYPES = ("address", "company", "designation", "city", "country",
                      "product", "category", "status", "diagnosis",
                      "property_type", "blood_group", "grade")


def _keywords_for(industry=None):
    if not industry or industry not in INDUSTRY_KEYWORDS:
        return FIELD_KEYWORDS
    merged = {k: list(v) for k, v in FIELD_KEYWORDS.items()}
    for ftype, extra in INDUSTRY_KEYWORDS[industry].items():
        merged.setdefault(ftype, [])
        merged[ftype] = list(dict.fromkeys(merged[ftype] + extra))
    return merged


VALUE_PATTERNS = {
    "email": re.compile(r"^[^@\s]+@[^@\s]+\.[a-zA-Z]{2,}$"),
    "gst": re.compile(r"^\d{2}[A-Z]{5}\d{4}[A-Z]{1}[A-Z\d]{1}Z[A-Z\d]{1}$", re.I),
    "pan": re.compile(r"^[A-Z]{5}\d{4}[A-Z]$", re.I),
    "aadhaar": re.compile(r"^\d{4}\s?\d{4}\s?\d{4}$"),
    "pincode": re.compile(r"^\d{6}$"),
    "website": re.compile(r"^(https?://|www\.)", re.I),
    "phone": re.compile(r"^\+?\d[\d\s\-()]{8,14}\d$"),
}


def _normalize_header(col):
    return re.sub(r"[^a-z0-9]", "", str(col).lower())


def detect_field_types(df, sample_size=25, industry=None):
    """Map each column to a semantic field type: header-keyword matching
    first (fast, works for any industry's naming convention), falling back to
    sampled-value pattern sniffing when a header is unlabeled or abbreviated.
    Pass `industry` (one of INDUSTRY_PRESETS) to add that industry's extra
    vocabulary on top of the generic keyword set.
    """
    if df is None or df.empty:
        return {}

    keywords_sorted = {
        ftype: sorted(kws, key=len, reverse=True)
        for ftype, kws in _keywords_for(industry).items()
    }

    mapping = {}
    normalized = {c: _normalize_header(c) for c in df.columns}

    for col, norm in normalized.items():
        best_type, best_len = None, 0
        for ftype, keywords in keywords_sorted.items():
            for kw in keywords:
                if kw in norm and len(kw) > best_len:
                    best_type, best_len = ftype, len(kw)
        if best_type:
            mapping[col] = best_type

    for col in df.columns:
        if col in mapping:
            continue
        sample = df[col].dropna().astype(str).head(sample_size)
        if sample.empty:
            continue
        for ftype, pattern in VALUE_PATTERNS.items():
            hits = sample.apply(lambda v: bool(pattern.match(v.strip())))
            if len(hits) and hits.mean() >= 0.6:
                mapping[col] = ftype
                break

    return mapping


def get_column(field_map, ftype):
    for col, t in field_map.items():
        if t == ftype:
            return col
    return None


# ================= NORMALIZERS =================
def normalize_phone(val):
    if pd.isna(val):
        return ""
    digits = re.sub(r"\D", "", str(val))
    return digits[-10:] if len(digits) >= 10 else ""


def normalize_text(val):
    if pd.isna(val):
        return ""
    if not isinstance(val, str):
        val = str(val)
    return re.sub(r"\s+", " ", val.strip())


def normalize_email(val):
    if pd.isna(val):
        return ""
    return str(val).strip().lower()


def title_case_name(val):
    if pd.isna(val):
        return val
    text = str(val).strip()
    if not text:
        return val
    return " ".join(w.capitalize() for w in text.split())


def clean_pincode(val):
    if pd.isna(val):
        return ""
    m = re.search(r"\b\d{6}\b", str(val))
    return m.group(0) if m else ""


def clean_amount(val):
    if pd.isna(val):
        return np.nan
    s = str(val).strip()
    if not s:
        return np.nan
    # Drop any leading currency word/symbol ("Rs.", "INR", "$", "₹", ...) so its
    # own punctuation (e.g. the period in "Rs.") can't be mistaken for a decimal point.
    s = re.sub(r"^[^\d\-]+", "", s)
    s = re.sub(r"[^\d.\-]", "", s)
    if s.count(".") > 1:
        # a thousands-separator style value can still leave extra dots; keep
        # only the last one as the decimal separator
        head, _, tail = s.rpartition(".")
        s = head.replace(".", "") + "." + tail
    if s in ("", "-", "."):
        return np.nan
    try:
        return float(s)
    except ValueError:
        return np.nan


# ================= UNIVERSAL DATAFRAME CLEANER =================
def clean_dataframe(df, industry=None):
    """Industry-agnostic cleaner. Auto-detects what each column represents
    (name/phone/email/address/pincode/amount/date/GST/PAN/... regardless of
    the sheet's origin industry) and applies the matching normalization, so
    it works on any Excel/CSV file without hardcoded column names. Pass
    `industry` (one of INDUSTRY_PRESETS) to sharpen detection for that
    industry's typical sheet layout.
    """
    if df is None or df.empty:
        return df

    df = df.copy()
    df.columns = df.columns.map(lambda c: str(c).strip())

    df = df.dropna(axis=0, how="all")
    df = df.dropna(axis=1, how="all")
    if df.empty:
        return df

    field_map = detect_field_types(df, industry=industry)

    pin_col = get_column(field_map, "pincode")
    state_col = get_column(field_map, "state")
    dist_col = get_column(field_map, "district")

    for col, ftype in field_map.items():
        try:
            if ftype == "phone":
                df[col] = df[col].apply(normalize_phone)
            elif ftype == "email":
                df[col] = df[col].apply(normalize_email)
            elif ftype == "name":
                df[col] = df[col].apply(title_case_name)
            elif ftype in _TEXT_FIELD_TYPES:
                df[col] = df[col].apply(normalize_text)
            elif ftype == "pincode":
                df[col] = df[col].apply(clean_pincode)
            elif ftype == "amount":
                df[col] = df[col].apply(clean_amount)
            elif ftype in ("date", "dob"):
                df[col] = pd.to_datetime(df[col], errors="coerce", dayfirst=True)
            elif ftype in ("gst", "pan", "aadhaar"):
                df[col] = df[col].astype(str).str.strip().str.upper().replace("NAN", "")
        except Exception:
            # a single unexpected column should never break the whole file
            continue

    for col in df.columns:
        if df[col].dtype == object:
            df[col] = df[col].apply(lambda v: v.strip() if isinstance(v, str) else v)

    # Pincode -> State/District enrichment (works for any industry's sheet)
    if pin_col:
        if not state_col:
            state_col = "State"
            df[state_col] = ""
        if not dist_col:
            dist_col = "District"
            df[dist_col] = ""

        for i, pin in df[pin_col].items():
            info = PINCODE_LOOKUP.get(pin)
            if info:
                if not str(df.at[i, state_col]).strip():
                    df.at[i, state_col] = info["state"]
                if not str(df.at[i, dist_col]).strip():
                    df.at[i, dist_col] = info["district"]

    return df


# ================= DATA QUALITY & VALIDATION =================
# Checked against the *original* value (not the cleaned one) so the report
# reflects what was actually in the source file.
VALIDATION_PATTERNS = {
    "email": re.compile(r"^[^@\s]+@[^@\s]+\.[a-zA-Z]{2,}$"),
    "gst": re.compile(r"^\d{2}[A-Z]{5}\d{4}[A-Z]{1}[A-Z\d]{1}Z[A-Z\d]{1}$", re.I),
    "pan": re.compile(r"^[A-Z]{5}\d{4}[A-Z]$", re.I),
    "aadhaar": re.compile(r"^\d{4}\s?\d{4}\s?\d{4}$"),
    "pincode": re.compile(r"^\d{6}$"),
    "website": re.compile(r"^(https?://|www\.)", re.I),
}


def _is_valid_value(value, ftype):
    if ftype == "phone":
        return len(normalize_phone(value)) == 10
    pattern = VALIDATION_PATTERNS.get(ftype)
    if pattern is None:
        return True
    return bool(pattern.match(str(value).strip()))


def data_quality_report(df, industry=None):
    """Per-column data-quality summary (missing %, detected type, invalid
    count) plus a row-level detail of invalid values for structured fields
    (email/phone/pincode/GST/PAN/Aadhaar/website) — read-only, doesn't modify
    the data, so it works as a pre-cleaning inspection for any file.
    """
    if df is None or df.empty:
        return pd.DataFrame(), pd.DataFrame()

    field_map = detect_field_types(df, industry=industry)
    total_rows = len(df)
    checkable_types = set(VALIDATION_PATTERNS) | {"phone"}

    summary_rows = []
    invalid_rows = []

    for col in df.columns:
        ftype = field_map.get(col, "unrecognized")
        is_blank = df[col].isna() | (df[col].astype(str).str.strip() == "")
        missing = int(is_blank.sum())
        missing_pct = round(missing / total_rows * 100, 1) if total_rows else 0.0

        invalid_count = 0
        if ftype in checkable_types:
            non_blank = df.loc[~is_blank, col]
            valid_mask = non_blank.apply(lambda v: _is_valid_value(v, ftype))
            invalid_count = int((~valid_mask).sum())
            for idx in non_blank.index[~valid_mask]:
                invalid_rows.append({
                    "row_index": idx, "column": col, "field_type": ftype,
                    "value": df.at[idx, col],
                })

        summary_rows.append({
            "Column": col,
            "Detected Type": ftype,
            "Missing": missing,
            "Missing %": missing_pct,
            "Invalid": invalid_count,
        })

    return pd.DataFrame(summary_rows), pd.DataFrame(invalid_rows)


# ================= FORMAT CONVERSION =================
def dataframe_to_bytes(df, fmt):
    """Serializes a DataFrame to bytes in the requested format.
    Returns (bytes, mime_type, file_extension). fmt is one of xlsx/csv/json.
    """
    buf = io.BytesIO()
    fmt = fmt.lower()

    if fmt == "xlsx":
        df.to_excel(buf, index=False, engine="openpyxl")
        mime = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    elif fmt == "csv":
        buf.write(df.to_csv(index=False).encode("utf-8"))
        mime = "text/csv"
    elif fmt == "json":
        buf.write(df.to_json(orient="records", indent=2, date_format="iso").encode("utf-8"))
        mime = "application/json"
    else:
        raise ValueError(f"Unsupported format: {fmt}")

    buf.seek(0)
    return buf, mime, fmt


def read_all_sheets_raw(file):
    """Reads every sheet of a workbook without merging them, for use cases
    (like splitting a workbook) that need each sheet kept separate."""
    sheets = pd.read_excel(file, sheet_name=None)
    return {name: d for name, d in sheets.items() if not d.dropna(how="all").empty}


def build_multi_sheet_excel(named_dataframes):
    """Combines {sheet_name: DataFrame} into a single in-memory .xlsx workbook."""
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        for name, d in named_dataframes.items():
            safe_name = re.sub(r"[\[\]:*?/\\]", "_", str(name))[:31] or "Sheet1"
            d.to_excel(writer, sheet_name=safe_name, index=False)
    buf.seek(0)
    return buf


# ================= FILE READERS =================
def read_any_excel(file):
    """Reads every sheet of a workbook (not just the first) so multi-sheet
    files aren't silently truncated, tagging rows with their source sheet
    when a workbook has more than one populated sheet.
    """
    sheets = pd.read_excel(file, sheet_name=None)
    populated = {name: d for name, d in sheets.items() if not d.dropna(how="all").empty}

    if not populated:
        return pd.DataFrame()
    if len(populated) == 1:
        return next(iter(populated.values()))

    frames = []
    for name, d in populated.items():
        d = d.copy()
        d["__sheet__"] = name
        frames.append(d)
    return pd.concat(frames, ignore_index=True)


def read_any_table(file):
    """Reads xlsx (all sheets) or csv (utf-8 with latin1 fallback) into one DataFrame."""
    name = file.name.lower()
    if name.endswith(".xlsx"):
        return read_any_excel(file)
    try:
        return pd.read_csv(file, encoding="utf-8")
    except UnicodeDecodeError:
        file.seek(0)
        return pd.read_csv(file, encoding="latin1")


def pdf_to_df(file):
    tables = []
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            table = page.extract_table()
            if table:
                tables.append(pd.DataFrame(table[1:], columns=table[0]))
    return pd.concat(tables, ignore_index=True) if tables else pd.DataFrame()


def image_to_df(file):
    reader = load_reader()

    file_bytes = np.asarray(bytearray(file.read()), dtype=np.uint8)
    img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

    if img is None:
        return pd.DataFrame()

    results = reader.readtext(img)
    if not results:
        return pd.DataFrame()

    boxes = []
    for (bbox, text, conf) in results:
        if conf < 0.4:
            continue
        x_min = min(p[0] for p in bbox)
        y_min = min(p[1] for p in bbox)
        boxes.append({"text": text.strip(), "x": x_min, "y": y_min})

    boxes = sorted(boxes, key=lambda b: b["y"])

    rows = []
    current_row = []
    last_y = None
    row_threshold = 20

    for box in boxes:
        if last_y is None or abs(box["y"] - last_y) < row_threshold:
            current_row.append(box)
        else:
            rows.append(current_row)
            current_row = [box]
        last_y = box["y"]

    if current_row:
        rows.append(current_row)

    table_data = []
    for row in rows:
        row_sorted = sorted(row, key=lambda b: b["x"])
        table_data.append([cell["text"] for cell in row_sorted])

    df = pd.DataFrame(table_data)
    df.reset_index(drop=True, inplace=True)
    return df


# ================= CROSS-FILE DEDUP (Match & Remove) =================
def enterprise_dedup_engine(df_ref, df_target, name_threshold=90, match_fields=("phone", "email", "name")):
    """Removes rows from df_target that match df_ref on phone, email, or a
    fuzzy name match. Column roles are auto-detected per file (not hardcoded),
    and phone/email matching is vectorized; fuzzy name matching uses
    rapidfuzz's C-accelerated cdist instead of a nested Python loop.
    `match_fields` controls which of phone/email/name are checked, and
    `name_threshold` (0-100) controls the fuzzy-name-match sensitivity.
    """
    df_ref = df_ref.copy()
    df_target = df_target.copy()

    field_ref = detect_field_types(df_ref)
    field_tgt = detect_field_types(df_target)

    name1, name2 = get_column(field_ref, "name"), get_column(field_tgt, "name")
    phone1, phone2 = get_column(field_ref, "phone"), get_column(field_tgt, "phone")
    email1, email2 = get_column(field_ref, "email"), get_column(field_tgt, "email")

    remove_index = set()
    report = []

    if "phone" in match_fields and phone1 and phone2:
        ref_phones = set(df_ref[phone1].apply(normalize_phone)) - {""}
        tgt_phones = df_target[phone2].apply(normalize_phone)
        hit = tgt_phones.isin(ref_phones) & (tgt_phones != "")
        for i in df_target.index[hit]:
            remove_index.add(i)
            report.append((i, "Phone Match"))

    if "email" in match_fields and email1 and email2:
        ref_emails = set(df_ref[email1].apply(normalize_email)) - {""}
        tgt_emails = df_target[email2].apply(normalize_email)
        hit = tgt_emails.isin(ref_emails) & (tgt_emails != "")
        for i in df_target.index[hit]:
            if i not in remove_index:
                remove_index.add(i)
                report.append((i, "Email Match"))

    if "name" in match_fields and name1 and name2:
        remaining = [i for i in df_target.index if i not in remove_index]
        ref_names = [n for n in df_ref[name1].apply(normalize_text).tolist() if n]

        if remaining and ref_names:
            tgt_names = df_target.loc[remaining, name2].apply(normalize_text).tolist()
            non_empty = [(pos, n) for pos, n in enumerate(tgt_names) if n]

            if non_empty:
                positions, names_only = zip(*non_empty)
                scores = process.cdist(names_only, ref_names, scorer=fuzz.token_sort_ratio, workers=-1)
                best_scores = scores.max(axis=1)

                for pos, score in zip(positions, best_scores):
                    if score >= name_threshold:
                        i = remaining[pos]
                        remove_index.add(i)
                        report.append((i, f"Name Similar {int(score)}"))

    cleaned = df_target.drop(index=list(remove_index))
    report_df = pd.DataFrame(report, columns=["row_index", "reason"])
    if not report_df.empty:
        report_df = report_df.sort_values("row_index").reset_index(drop=True)

    return cleaned, report_df


# ================= SELF-FILE DEDUP (AI Smart Dedup) =================
def ultra_fast_dedup(df, similarity_threshold=0.92, match_fields=("phone", "email", "name")):
    """Removes duplicate rows within a single file: exact phone/email
    duplicates (vectorized) plus near-duplicate names via TF-IDF + cosine
    similarity. Column roles are auto-detected, so this works on any sheet.
    `match_fields` controls which of phone/email/name are checked, and
    `similarity_threshold` (0-1) controls the name-similarity sensitivity.
    """
    df = df.copy()

    field_map = detect_field_types(df)
    name_col = get_column(field_map, "name") if "name" in match_fields else None
    phone_col = get_column(field_map, "phone") if "phone" in match_fields else None
    email_col = get_column(field_map, "email") if "email" in match_fields else None

    if phone_col:
        df["_phone"] = df[phone_col].apply(normalize_phone)
    if email_col:
        df["_email"] = df[email_col].apply(normalize_email)
    if name_col:
        df["_name"] = df[name_col].apply(normalize_text)

    remove = set()
    report = []

    if "_phone" in df.columns:
        dup = df[df["_phone"] != ""].duplicated("_phone", keep="first")
        for idx in df[dup].index:
            remove.add(idx)
            report.append((idx, "Phone Duplicate"))

    if "_email" in df.columns:
        dup = df[df["_email"] != ""].duplicated("_email", keep="first")
        for idx in df[dup].index:
            if idx not in remove:
                remove.add(idx)
                report.append((idx, "Email Duplicate"))

    if "_name" in df.columns:
        names = df["_name"].fillna("").tolist()
        non_empty_idx = [i for i, n in enumerate(names) if n.strip()]

        if len(non_empty_idx) > 1:
            vectorizer = TfidfVectorizer().fit_transform([names[i] for i in non_empty_idx])
            sim = cosine_similarity(vectorizer)

            for a in range(len(non_empty_idx)):
                for b in range(a + 1, len(non_empty_idx)):
                    if sim[a, b] > similarity_threshold:
                        j = df.index[non_empty_idx[b]]
                        if j not in remove:
                            remove.add(j)
                            report.append((j, "Name Similarity"))

    cleaned_df = df.drop(index=list(remove))
    cleaned_df = cleaned_df.drop(columns=["_phone", "_email", "_name"], errors="ignore")

    report_df = pd.DataFrame(report, columns=["row_index", "reason"])
    if not report_df.empty:
        report_df = report_df.sort_values("row_index").reset_index(drop=True)

    return cleaned_df, report_df
