"""
DataFlow Pro — Automated Test Suite & PDF Report Generator
Tests all core modules: field detection, normalizers, cleaners, dedup, file readers, UI health
"""
import os
import sys
import time
import traceback
import datetime
import io
import pandas as pd
import numpy as np
import requests

# Ensure the project dir is on path
BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)

from main import (
    detect_field_types,
    get_column,
    normalize_phone,
    normalize_email,
    normalize_text,
    title_case_name,
    clean_pincode,
    clean_amount,
    clean_dataframe,
    enterprise_dedup_engine,
    ultra_fast_dedup,
    is_hindi,
    read_any_table,
    PINCODE_LOOKUP,
)

# ===== Test Framework =====
results = []  # list of (section, test_name, status, detail)

def record(section, name, passed, detail=""):
    results.append((section, name, "PASS" if passed else "FAIL", detail))

# ===== 1. FIELD DETECTION TESTS =====
section = "Field Detection Engine"

# Test 1.1: Standard column headers
df_test = pd.DataFrame({
    "Customer Name": ["Alice"],
    "Mobile No": ["9876543210"],
    "Email Address": ["a@b.com"],
    "Pin Code": ["110001"],
    "Total Amount": ["500"],
    "Order Date": ["01-01-2024"],
})
fm = detect_field_types(df_test)
record(section, "Detects 'name' from 'Customer Name'", fm.get("Customer Name") == "name", f"Got: {fm.get('Customer Name')}")
record(section, "Detects 'phone' from 'Mobile No'", fm.get("Mobile No") == "phone", f"Got: {fm.get('Mobile No')}")
record(section, "Detects 'email' from 'Email Address'", fm.get("Email Address") == "email", f"Got: {fm.get('Email Address')}")
record(section, "Detects 'pincode' from 'Pin Code'", fm.get("Pin Code") == "pincode", f"Got: {fm.get('Pin Code')}")
record(section, "Detects 'amount' from 'Total Amount'", fm.get("Total Amount") == "amount", f"Got: {fm.get('Total Amount')}")
record(section, "Detects 'date' from 'Order Date'", fm.get("Order Date") == "date", f"Got: {fm.get('Order Date')}")

# Test 1.2: Value-pattern fallback
df_pat = pd.DataFrame({
    "Col_A": ["test@example.com", "user@mail.in", "a@b.org"],
    "Col_B": ["110001", "400001", "560001"],
})
fm2 = detect_field_types(df_pat)
record(section, "Value-pattern fallback detects email", fm2.get("Col_A") == "email", f"Got: {fm2.get('Col_A')}")
record(section, "Value-pattern fallback detects pincode", fm2.get("Col_B") == "pincode", f"Got: {fm2.get('Col_B')}")

# Test 1.3: Empty DataFrame
fm3 = detect_field_types(pd.DataFrame())
record(section, "Empty DF returns empty mapping", fm3 == {}, f"Got: {fm3}")

# ===== 2. NORMALIZER TESTS =====
section = "Normalizers"

record(section, "normalize_phone extracts 10 digits", normalize_phone("+91-98765-43210") == "9876543210")
record(section, "normalize_phone handles NaN", normalize_phone(np.nan) == "")
record(section, "normalize_phone short number", normalize_phone("12345") == "")

record(section, "normalize_email lowercases", normalize_email("  Test@MAIL.Com  ") == "test@mail.com")
record(section, "normalize_email handles NaN", normalize_email(np.nan) == "")

record(section, "normalize_text strips & collapses spaces", normalize_text("  hello   world  ") == "hello world")
record(section, "normalize_text handles NaN", normalize_text(np.nan) == "")

record(section, "title_case_name capitalizes", title_case_name("john doe") == "John Doe")
record(section, "title_case_name handles NaN", pd.isna(title_case_name(np.nan)))

record(section, "clean_pincode extracts 6-digit", clean_pincode("PIN: 110001 area") == "110001")
record(section, "clean_pincode rejects bad input", clean_pincode("abcdef") == "")

record(section, "clean_amount parses Rs.1,500.50", clean_amount("Rs.1,500.50") == 1500.50)
record(section, "clean_amount returns NaN for junk", np.isnan(clean_amount("abc")))

# ===== 3. CLEAN DATAFRAME TESTS =====
section = "DataFrame Cleaner"

df_dirty = pd.DataFrame({
    "Name": ["  john doe  ", "ALICE smith", np.nan],
    "Phone": ["+91-9876543210", "  1234567890  ", "abc"],
    "Email": ["  Test@Mail.COM  ", "user@test.in", np.nan],
    "Pincode": ["110001", "400001", "xyz"],
    "Amount": ["Rs.1,500", "2000.50", "abc"],
})

df_clean = clean_dataframe(df_dirty)
record(section, "Name title-cased", df_clean["Name"].iloc[0] == "John Doe")
record(section, "Phone normalized to 10 digits", df_clean["Phone"].iloc[0] == "9876543210")
record(section, "Email lowercased", df_clean["Email"].iloc[0] == "test@mail.com")
record(section, "Pincode cleaned", df_clean["Pincode"].iloc[0] == "110001")
record(section, "Amount parsed to float", df_clean["Amount"].iloc[0] == 1500.0)

# Pincode enrichment
record(section, "State auto-filled from pincode", "State" in df_clean.columns or any("state" in c.lower() for c in df_clean.columns))

# ===== 4. PINCODE LOOKUP =====
section = "Pincode Lookup"

record(section, "Lookup has entries", len(PINCODE_LOOKUP) > 10000, f"Count: {len(PINCODE_LOOKUP)}")
info_110001 = PINCODE_LOOKUP.get("110001")
record(section, "110001 maps to Delhi", info_110001 is not None and "Delhi" in str(info_110001.get("state", "")), f"Got: {info_110001}")

# ===== 5. SELF-FILE DEDUP (AI Smart Dedup) =====
section = "AI Smart Dedup"

df_dup = pd.DataFrame({
    "Customer Name": ["Alice Smith", "Bob Jones", "Alice Smith", "Carol White", "alice smith"],
    "Phone": ["9876543210", "8765432109", "9876543210", "7654321098", "1111111111"],
    "Email": ["alice@test.com", "bob@test.com", "alice@test.com", "carol@test.com", "alice2@test.com"],
})

cleaned, report = ultra_fast_dedup(df_dup)
record(section, "Removes phone duplicates", len(cleaned) < len(df_dup), f"Before: {len(df_dup)}, After: {len(cleaned)}")
record(section, "Report lists reasons", not report.empty and "reason" in report.columns)
record(section, "At least 1 duplicate found", len(report) >= 1, f"Found: {len(report)}")

# ===== 6. CROSS-FILE DEDUP (Match & Remove) =====
section = "Match & Remove Engine"

df_ref = pd.DataFrame({
    "Name": ["Alice Smith", "Bob Jones"],
    "Phone": ["9876543210", "8765432109"],
    "Email": ["alice@test.com", "bob@test.com"],
})

df_tgt = pd.DataFrame({
    "Name": ["Alice Smith", "Carol White", "Dave Brown"],
    "Phone": ["9876543210", "7654321098", "6543210987"],
    "Email": ["alice@test.com", "carol@test.com", "dave@test.com"],
})

cleaned_tgt, match_report = enterprise_dedup_engine(df_ref, df_tgt)
record(section, "Removes matching row (Alice)", len(cleaned_tgt) < len(df_tgt))
record(section, "Non-matching rows kept", len(cleaned_tgt) >= 2, f"Remaining: {len(cleaned_tgt)}")
record(section, "Report generated", not match_report.empty)

# ===== 7. HINDI DETECTION =====
section = "Hindi Detection"

record(section, "Detects Hindi text", is_hindi("नमस्ते दुनिया") == True)
record(section, "English text not Hindi", is_hindi("Hello World") == False)
record(section, "None/empty safe", is_hindi("") == False)

# ===== 8. UI / SERVER HEALTH =====
section = "UI & Server Health"

try:
    resp = requests.get("http://localhost:8501", timeout=10)
    record(section, "Streamlit server responds 200", resp.status_code == 200, f"Status: {resp.status_code}")
    record(section, "HTML page served", "<!DOCTYPE html>" in resp.text[:200])
except Exception as e:
    record(section, "Server reachable", False, str(e))

try:
    health = requests.get("http://localhost:8501/_stcore/health", timeout=5)
    record(section, "Streamlit health endpoint OK", health.status_code == 200, f"Response: {health.text[:50]}")
except Exception as e:
    record(section, "Health endpoint", False, str(e))

# ===== 9. CSS THEME VALIDATION =====
section = "Theme & Styling"

with open(os.path.join(BASE, "app.py"), "r", encoding="utf-8") as f:
    app_code = f.read()

record(section, "Uses Inter font family", "'Inter'" in app_code)
record(section, "Uses Space Grotesk font", "'Space Grotesk'" in app_code)
record(section, "Has glassmorphism (backdrop-filter)", "backdrop-filter: blur" in app_code)
record(section, "Purple/violet accent present", "#8b5cf6" in app_code)
record(section, "Cyan accent present", "#06b6d4" in app_code)
record(section, "Emerald accent present", "#10b981" in app_code)
record(section, "Dark background gradient", "#0a0a1a" in app_code or "#0d1117" in app_code)
record(section, "Glass-card component exists", "glass-card" in app_code)
record(section, "Hero container exists", "hero-container" in app_code)
record(section, "Feature pills exist", "feature-pills" in app_code)
record(section, "Section headers styled", "section-header" in app_code)
record(section, "Responsive media queries", "@media (max-width: 768px)" in app_code)
record(section, "No old yellow #FFD700 theme", "#FFD700" not in app_code)

# ===== 10. APP STRUCTURE =====
section = "App Structure & Sections"

record(section, "Section 1: Single File present", "Single File Processing" in app_code)
record(section, "Section 2: Batch Processing present", "Batch Processing" in app_code)
record(section, "Section 3: Data Fusion present", "Data Fusion" in app_code)
record(section, "Section 4: Precision Extract present", "Precision Extract" in app_code)
record(section, "Section 5: Match & Remove present", "Match & Remove" in app_code)
record(section, "Section 6: AI Smart Dedup present", "AI Smart Dedup" in app_code)
record(section, "Footer present", "app-footer" in app_code)
record(section, "Sidebar present", "Control Panel" in app_code)

# ===== GENERATE PDF REPORT =====
from fpdf import FPDF

class TestReport(FPDF):
    def header(self):
        self.set_fill_color(30, 27, 75)
        self.rect(0, 0, 210, 40, 'F')
        self.set_font('Helvetica', 'B', 22)
        self.set_text_color(167, 139, 250)
        self.set_y(8)
        self.cell(0, 12, 'DataFlow Pro - Test Report', align='C', new_x="LMARGIN", new_y="NEXT")
        self.set_font('Helvetica', '', 10)
        self.set_text_color(148, 163, 184)
        self.cell(0, 6, f'Generated: {datetime.datetime.now().strftime("%B %d, %Y at %I:%M %p")}', align='C', new_x="LMARGIN", new_y="NEXT")
        self.ln(12)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(100, 116, 139)
        self.cell(0, 10, f'Page {self.page_no()}/{{nb}} | DataFlow Pro v3.0', align='C')

pdf = TestReport()
pdf.alias_nb_pages()
pdf.set_auto_page_break(auto=True, margin=20)

# Summary Page
pdf.add_page()

total = len(results)
passed = sum(1 for r in results if r[2] == "PASS")
failed = sum(1 for r in results if r[2] == "FAIL")
pass_rate = (passed / total * 100) if total > 0 else 0

# Summary box
pdf.set_fill_color(15, 23, 42)
pdf.set_draw_color(139, 92, 246)
pdf.rect(15, pdf.get_y(), 180, 38, 'DF')

pdf.set_font('Helvetica', 'B', 14)
pdf.set_text_color(226, 232, 240)
pdf.set_y(pdf.get_y() + 3)
pdf.cell(0, 8, 'Test Summary', align='C', new_x="LMARGIN", new_y="NEXT")

pdf.set_font('Helvetica', '', 11)
y = pdf.get_y() + 2

# Total
pdf.set_xy(25, y)
pdf.set_text_color(148, 163, 184)
pdf.cell(40, 7, 'Total Tests:')
pdf.set_text_color(167, 139, 250)
pdf.set_font('Helvetica', 'B', 11)
pdf.cell(20, 7, str(total))

# Passed
pdf.set_xy(90, y)
pdf.set_text_color(148, 163, 184)
pdf.set_font('Helvetica', '', 11)
pdf.cell(30, 7, 'Passed:')
pdf.set_text_color(16, 185, 129)
pdf.set_font('Helvetica', 'B', 11)
pdf.cell(20, 7, str(passed))

# Failed
pdf.set_xy(145, y)
pdf.set_text_color(148, 163, 184)
pdf.set_font('Helvetica', '', 11)
pdf.cell(30, 7, 'Failed:')
pdf.set_text_color(244, 63, 94) if failed > 0 else pdf.set_text_color(16, 185, 129)
pdf.set_font('Helvetica', 'B', 11)
pdf.cell(20, 7, str(failed))

y2 = y + 10
pdf.set_xy(25, y2)
pdf.set_text_color(148, 163, 184)
pdf.set_font('Helvetica', '', 11)
pdf.cell(40, 7, 'Pass Rate:')
if pass_rate >= 90:
    pdf.set_text_color(16, 185, 129)
elif pass_rate >= 70:
    pdf.set_text_color(245, 158, 11)
else:
    pdf.set_text_color(244, 63, 94)
pdf.set_font('Helvetica', 'B', 14)
pdf.cell(30, 7, f'{pass_rate:.1f}%')

pdf.ln(20)

# Detailed Results by Section
current_section = ""
for section, name, status, detail in results:
    if section != current_section:
        current_section = section
        pdf.ln(5)
        pdf.set_fill_color(30, 27, 75)
        pdf.set_text_color(167, 139, 250)
        pdf.set_font('Helvetica', 'B', 12)
        pdf.cell(0, 9, f'  {section}', fill=True, new_x="LMARGIN", new_y="NEXT")
        pdf.ln(2)

    # Status icon
    if status == "PASS":
        pdf.set_text_color(16, 185, 129)
        icon = "[PASS]"
    else:
        pdf.set_text_color(244, 63, 94)
        icon = "[FAIL]"

    pdf.set_font('Helvetica', 'B', 9)
    pdf.cell(16, 6, icon)

    pdf.set_text_color(226, 232, 240)
    pdf.set_font('Helvetica', '', 9)
    test_text = name
    if detail:
        test_text += f"  ({detail})"
    # Truncate if too long
    if len(test_text) > 110:
        test_text = test_text[:107] + "..."
    pdf.cell(0, 6, test_text, new_x="LMARGIN", new_y="NEXT")

# ===== UI Changes Summary Page =====
pdf.add_page()

pdf.set_font('Helvetica', 'B', 16)
pdf.set_text_color(167, 139, 250)
pdf.cell(0, 10, 'UI Redesign Summary', align='C', new_x="LMARGIN", new_y="NEXT")
pdf.ln(5)

changes = [
    ("Color Theme", "Old: Black + Yellow (#FFD700) + Pink (#FF69B4) + Sky Blue (#87CEEB)\nNew: Deep Space Dark (#0a0a1a, #0d1117) + Violet (#8b5cf6) + Cyan (#06b6d4) + Emerald (#10b981)"),
    ("Typography", "Old: Orbitron + Poppins (heavy, gaming feel)\nNew: Space Grotesk + Inter + JetBrains Mono (clean, professional, tech-forward)"),
    ("Design System", "Old: Heavy gradients, thick borders, excessive animations (bounce, shake, rotate)\nNew: Glassmorphism with backdrop-filter blur, subtle borders, minimal smooth animations"),
    ("Components", "Old: feature-card grid with heavy shadows, bouncing icons\nNew: Feature pills (compact badges), glass-card containers, clean stat-cards"),
    ("Header", "Old: Giant 4.5rem Orbitron title with glowing text-shadow, 6rem bouncing emoji\nNew: Clean hero with gradient text, badge, subtle subtitle, feature pills"),
    ("Sections", "Old: Numbered but visually heavy with thick gold borders\nNew: Flex layout with gradient numbers, clean info block, subtle accent border"),
    ("Buttons", "Old: Gold/pink gradients with 50px border-radius, heavy shadows\nNew: Violet/cyan gradients with 12px radius, clean hover lift effect"),
    ("Sidebar", "Old: Same heavy gold theme\nNew: Minimal dark with sidebar-card components, clean typography"),
    ("Footer", "Old: Heavy multi-color border with gold accents\nNew: Clean glassmorphism card with muted stats"),
    ("Animations", "Old: 8+ animations (bounce-rotate, shake, pulse-glow, scan lines)\nNew: 3 subtle animations (heroFade, sectionSlide, statPop)"),
    ("Accessibility", "Old: Low contrast in some areas, distracting motion\nNew: Better contrast ratios, reduced motion, cleaner hierarchy"),
]

for title, desc in changes:
    pdf.set_fill_color(30, 27, 75)
    pdf.set_text_color(103, 232, 249)
    pdf.set_font('Helvetica', 'B', 10)
    pdf.cell(0, 7, f'  {title}', fill=True, new_x="LMARGIN", new_y="NEXT")

    pdf.set_text_color(203, 213, 225)
    pdf.set_font('Helvetica', '', 8.5)
    for line in desc.split("\n"):
        pdf.cell(0, 5, f'    {line}', new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)

# Save
output_path = os.path.join(BASE, "DataFlow_Pro_Test_Report.pdf")
pdf.output(output_path)
print(f"\n{'='*60}")
print(f"  TEST RESULTS: {passed}/{total} passed ({pass_rate:.1f}%)")
print(f"  PDF saved: {output_path}")
print(f"{'='*60}")

if failed > 0:
    print(f"\n  FAILED TESTS:")
    for s, n, st, d in results:
        if st == "FAIL":
            print(f"    [{s}] {n} — {d}")
