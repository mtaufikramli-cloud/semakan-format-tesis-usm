import base64
import io
import re
from fpdf import FPDF
from PIL import Image
import pymupdf as fitz
import streamlit as st
import streamlit.components.v1 as components
from PIL import Image, ImageDraw

# =========================================================================
# 🌐 KAMUS TERJEMAHAN BAHASA (I18N)
# =========================================================================
TEXT_I18N = {
    "BM": {
        "report_title": "Laporan Format: Muka Surat {page_num}",
        "warning_header": "[AMARAN] Dikesan {count} Isu Format:",
        "no_issue": "✅ Tiada isu format dikesan pada muka surat ini.",
        "status_ok": "[OK] STATUS: SEMPURNA / TIADA ISU FORMAT",
        "margin_top": "Teks melanggar Margin Atas {limit}mm: '{text}' (Kedudukan semasa: {val:.1f}mm dari tepi atas)",
        "margin_bottom": "Teks melanggar Margin Bawah {limit}mm: '{text}' (Kedudukan semasa: {val:.1f}mm dari tepi bawah)",
        "margin_left": "Teks melanggar Margin Kiri {limit}mm: '{text}' (Kedudukan semasa: {val:.1f}mm dari tepi kiri)",
        "margin_right": "Teks melanggar Margin Kanan {limit}mm: '{text}' (Kedudukan semasa: {val:.1f}mm dari tepi kanan)",
        "font_issue": "Jenis font '{font_name}' tidak dibenarkan pada teks: '{text}'",
        "pdf_no_issues": "Tiada isu format dikesan. Tesis mematuhi piawaian!",
        "pdf_col_page": "Muka Surat",
        "pdf_col_details": "Butiran Isu Format",
        "pdf_main_title": "Laporan Semakan Format Tesis",
        "pdf_total_pages": "Jumlah Muka Surat Diperiksa: {total_pages}",
        "landscape_page_num": "Kedudukan Nombor Muka Surat Salah: Nombor '{num}' dikesan di BAHAGIAN BAWAH halaman Landscape. Mengikut piawaian USM, nombor muka surat mestilah diletakkan di SEBELAH KIRI.",
        "chapter_title_same_line": "Tajuk Bab: '{text}' ditulis pada baris yang sama. 'CHAPTER/BAB' dan tajuk bab (contoh: INTRODUCTION) mestilah dipisahkan dengan ENTER (baris baharu).",
        "chapter_same_y_level": "Tajuk Bab: '{text}' dan '{snippet}' berada pada baris yang sama. Sila tekan ENTER untuk meletakkan tajuk bab di bawah.",
        "table_line_margin_top": "Garisan Jadual/Bingkai melanggar Margin Atas {limit}mm ({val:.1f}mm dikesan).",
        "title_page_month_year": "Muka Surat Tajuk (M/S 1-2): Bulan dan Tahun penyerahan tidak dikesan.",
        "missing_page_num": "Nombor muka surat tidak dikesan di {location}.",
        "loc_landscape": "sebelah kiri/atas",
        "loc_portrait": "bahagian bawah tengah",
        "ack_missing_ii": "Penghargaan / Acknowledgement: Muka surat ini wajib diletakkan nombor muka surat 'ii'.",
        "ack_max_one_page": "Penghargaan / Acknowledgement: Dihadkan kepada 1 muka surat sahaja.",
        "toc_missing_iii": "Kandungan / Table of Contents: Muka surat awal TOC wajib bermula dengan nombor muka surat 'iii'.",
        "toc_invalid_sub": "Kandungan / Table of Contents: Sub-pembahagian tajuk mestilah menggunakan kurungan, contoh: 1.2.1(a) atau 1.2.1(a)(i).",
        "abstract_bm_label": "ABSTRAK (BM)",
        "abstract_en_label": "ABSTRACT (EN)",
        "abstract_max_words": "{type}: Panjang teks melebihi had 400 perkataan ({count} perkataan dikesan).",
        "abstract_single_para": "{type}: Teks hendaklah ditulis dalam SATU PERENGGAN sahaja.",
        "abstract_indent": "{type}: Baris pertama perenggan hendaklah di-indent (indented).",
        "ref_spacing_issue": "Rujukan / References: Mesti menggunakan Single-spacing dalam entri dan Double-spacing antara entri rujukan.",
        "appendix_divider_pagenum": "Lampiran / Appendices: Muka surat pembatas 'LAMPIRAN / APPENDICES' TIDAK BOLEH diletakkan nombor muka surat.",
        "appendix_invalid_label": "Lampiran / Appendices: Lampiran mestilah dilabel mengikut abjad (contoh: Lampiran A, Appendix B).",
        "chapter_heading_not_bold": "Tajuk Seksyen/Bab mesti BOLD: '{text}...'",
        "chapter_heading_not_centered": "Tajuk Seksyen/Bab mesti di TENGAH (Centered): '{text}...'",
        "chapter_heading_not_single_spaced": "Tajuk Seksyen/Bab mesti SINGLE SPACING: '{text}...'",
        "font_size_too_small": "Saiz font terlalu kecil ({size}pt): '{text}...'",
        "font_size_non_standard": "Saiz font tidak piawai ({size}pt): '{text}...'",
        "table_caption_position_error": "Kedudukan Tajuk Jadual Salah / Tiada Jadual Di Bawah: '{text}...'",
        "table_caption_split_format": "Format Tajuk Jadual Terpisah Baris: '{text}' (Perlu sebaris dengan penerangan)",
        "figure_caption_position_error": "Kedudukan Tajuk Rajah Salah (Mesti Di Bawah Rajah): '{text}...'",
        "title_page_pagenum_forbidden": "Title Page / Muka Surat Tajuk: Nombor muka surat TIDAK BOLEH dipaparkan.",
        "declaration_pagenum_forbidden": "Pengakuan / Declaration: Nombor muka surat TIDAK BOLEH dipaparkan.",
        "missing_page_num": "Nombor muka surat tidak dikesan di {location}.",
        "loc_landscape": "sebelah kiri/atas",
        "loc_portrait": "bahagian bawah tengah",
        "ui_review_preview_title": "🔍 Mod Semakan & Pratonton Visual",
        "ui_issues_found": "⚠️ Ada Isu: {count}",
        "ui_status_ok": "✅ Baik / Disemak",
        "ui_page_label": "Muka Surat {num}{tag} - ({status})",
        "ui_preview_caption": "Pratonton MS {num}",
        "ui_no_errors_page": "Muka surat ini bebas daripada ralat format.",
        "ui_detected_issues_title": "**Senarai Isu Dikesan:**",
        "ui_bypass_issue": "Abaikan (Bypass Isu #{num})",
        "ui_issue_label": "Isu #{num}",
        "ui_bypass_all_page": "☑️ **Abaikan Semua Isu Muka Surat Ini (Bypass All)**",

    },
    "EN": {
        "report_title": "Format Report: Page {page_num}",
        "warning_header": "[WARNING] Detected {count} Format Issue(s):",
        "no_issue": "✅ No format issues detected on this page.",
        "status_ok": "[OK] STATUS: PERFECT / NO FORMAT ISSUES",
        "margin_top": "Text violates Top Margin {limit}mm: '{text}' (Current position: {val:.1f}mm from top)",
        "margin_bottom": "Text violates Bottom Margin {limit}mm: '{text}' (Current position: {val:.1f}mm from bottom)",
        "margin_left": "Text violates Left Margin {limit}mm: '{text}' (Current position: {val:.1f}mm from left)",
        "margin_right": "Text violates Right Margin {limit}mm: '{text}' (Current position: {val:.1f}mm from right)",
        "font_issue": "Font type '{font_name}' is not allowed on text: '{text}'",
        "pdf_no_issues": "No format issues detected. Thesis complies with standards!",
        "pdf_col_page": "Page Number",
        "pdf_col_details": "Format Issue Details",
        "pdf_main_title": "Thesis Format Checking Report",
        "pdf_total_pages": "Total Pages Checked: {total_pages}",
        "landscape_page_num": "Incorrect Page Number Position: Number '{num}' detected at the BOTTOM of a Landscape page. According to USM standards, page numbers must be placed on the LEFT side.",
        "chapter_title_same_line": "Chapter Title: '{text}' is written on the same line. 'CHAPTER/BAB' and the chapter title (e.g., INTRODUCTION) must be separated by ENTER (new line).",
        "chapter_same_y_level": "Chapter Title: '{text}' and '{snippet}' are on the same line. Please press ENTER to move the chapter title below.",
        "table_line_margin_top": "Table Line/Border violates Top Margin {limit}mm ({val:.1f}mm detected).",
        "title_page_month_year": "Title Page (Page 1-2): Month and Year of submission not detected.",
        "missing_page_num": "Page number not detected at {location}.",
        "loc_landscape": "top/left side",
        "loc_portrait": "bottom center",
        "ack_missing_ii": "Acknowledgement / Penghargaan: This page must be numbered with page number 'ii'.",
        "ack_max_one_page": "Acknowledgement / Penghargaan: Restricted to 1 page only.",
        "toc_missing_iii": "Table of Contents / Kandungan: The initial TOC page must start with page number 'iii'.",
        "toc_invalid_sub": "Table of Contents / Kandungan: Subsection divisions must use parentheses, e.g., 1.2.1(a) or 1.2.1(a)(i).",
        "abstract_bm_label": "ABSTRAK (BM)",
        "abstract_en_label": "ABSTRACT (EN)",
        "abstract_max_words": "{type}: Text length exceeds the 400-word limit ({count} words detected).",
        "abstract_single_para": "{type}: Text must be written in a SINGLE PARAGRAPH only.",
        "abstract_indent": "{type}: The first line of the paragraph must be indented.",
        "ref_spacing_issue": "References / Rujukan: Must use Single-spacing within entries and Double-spacing between reference entries.",
        "appendix_divider_pagenum": "Appendices / Lampiran: The 'APPENDICES' divider page MUST NOT contain a page number.",
        "appendix_invalid_label": "Appendices / Lampiran: Appendices must be labeled alphabetically (e.g., Appendix A, Appendix B).",
        "chapter_heading_not_bold": "Section/Chapter Heading must be BOLD: '{text}...'",
        "chapter_heading_not_centered": "Section/Chapter Heading must be CENTERED: '{text}...'",
        "chapter_heading_not_single_spaced": "Section/Chapter Heading must be SINGLE SPACED: '{text}...'",
        "font_size_too_small": "Font size is too small ({size}pt): '{text}...'",
        "font_size_non_standard": "Non-standard font size ({size}pt): '{text}...'",
        "table_caption_position_error": "Incorrect Table Caption Position / No Table Below: '{text}...'",
        "table_caption_split_format": "Split Table Caption Format: '{text}' (Must be on the same line as the description)",
        "figure_caption_position_error": "Incorrect Figure Caption Position (Must Be Below Figure): '{text}...'",
        "title_page_pagenum_forbidden": "Title Page: Page number MUST NOT be displayed.",
        "declaration_pagenum_forbidden": "Declaration Page: Page number MUST NOT be displayed.",
        "missing_page_num": "Page number not detected at {location}.",
        "loc_landscape": "top/left side",
        "loc_portrait": "bottom center",
        "ui_review_preview_title": "🔍 Review Mode & Visual Preview",
        "ui_issues_found": "⚠️ Issues Found: {count}",
        "ui_status_ok": "✅ Clear / Reviewed",
        "ui_page_label": "Page {num}{tag} - ({status})",
        "ui_preview_caption": "Page {num} Preview",
        "ui_no_errors_page": "This page is free from formatting errors.",
        "ui_detected_issues_title": "**List of Detected Issues:**",
        "ui_bypass_issue": "Ignore (Bypass Issue #{num})",
        "ui_issue_label": "Issue #{num}",
        "ui_bypass_all_page": "☑️ **Bypass All Issues on This Page**",

    }
}

# 1. Takrifkan Fungsi Footer di Bahagian Atas app.py
def paparkan_footer():
    st.markdown("---")
    st.markdown("""
        <div style="text-align: center; color: #4b5563; font-size: 0.85rem; line-height: 1.6; background-color: #f9fafb; padding: 15px; border-radius: 8px; border: 1px solid #e5e7eb;">
            <p style="margin-bottom: 4px; font-weight: bold; color: #1f2937;">
                © 2026 Ts. Muhammad Taufik Ramli / KV Nibong Tebal. Hak Cipta Terpelihara (All Rights Reserved).
            </p>
            <p style="margin-bottom: 4px;">
                📍 Program Teknologi Elektronik, Kolej Vokasional Nibong Tebal, Jalan Bukit Panchor, 14300 Nibong Tebal, Pulau Pinang
            </p>
            <p style="margin-bottom: 0;">
                📧 Hubungi Sokongan: <a href="mailto:mtaufikramli@gmail.com" style="color: #2563eb; text-decoration: none; font-weight: 500;">mtaufikramli@gmail.com</a>
            </p>
        </div>
    """, unsafe_allow_html=True)

def generate_combined_visual_report(annotated_pdf_bytes, all_pages_errors_list, ignored_errors,
                                     margin_left_mm=40, margin_right_mm=25, 
                                     margin_top_mm=25, margin_bottom_mm=25):
    # Buka PDF berkotak merah ralat
    annotated_doc = fitz.open("pdf", annotated_pdf_bytes)
    combined_doc = fitz.open()

    # Saiz A4 Landscape
    A4_L_WIDTH = 841.89
    A4_L_HEIGHT = 595.28

    # Kanvas Kiri Tesis
    thesis_rect = fitz.Rect(15, 20, 407.3, 575)

    for p_num in range(len(annotated_doc)):
        new_page = combined_doc.new_page(width=A4_L_WIDTH, height=A4_L_HEIGHT)

        # -----------------------------------------------------------------
        # 📌 1. TEKAP TESIS (LENGKAP DENGAN KOTAK MERAH ERROR)
        # -----------------------------------------------------------------
        new_page.show_pdf_page(thesis_rect, annotated_doc, p_num)

        # -----------------------------------------------------------------
        # 📌 2. LUKIS GARISAN MARGIN PUTUS-PUTUS MERAH LEMBUT (FAINT RED)
        # -----------------------------------------------------------------
        scale_x = thesis_rect.width / 595.28
        scale_y = thesis_rect.height / 841.89

        m_left_pt = margin_left_mm * 2.83465
        m_right_pt = (210 - margin_right_mm) * 2.83465
        m_top_pt = margin_top_mm * 2.83465
        m_bottom_pt = (297 - margin_bottom_mm) * 2.83465

        x_left = thesis_rect.x0 + (m_left_pt * scale_x)
        x_right = thesis_rect.x0 + (m_right_pt * scale_x)
        y_top = thesis_rect.y0 + (m_top_pt * scale_y)
        y_bottom = thesis_rect.y0 + (m_bottom_pt * scale_y)

        shape_margin = new_page.new_shape()
        shape_margin.draw_line(fitz.Point(x_left, thesis_rect.y0), fitz.Point(x_left, thesis_rect.y1))
        shape_margin.draw_line(fitz.Point(x_right, thesis_rect.y0), fitz.Point(x_right, thesis_rect.y1))
        shape_margin.draw_line(fitz.Point(thesis_rect.x0, y_top), fitz.Point(thesis_rect.x1, y_top))
        shape_margin.draw_line(fitz.Point(thesis_rect.x0, y_bottom), fitz.Point(thesis_rect.x1, y_bottom))
        
        shape_margin.finish(color=(0.95, 0.45, 0.45), dashes="[3 3]", stroke_opacity=0.55, width=0.6)
        shape_margin.commit()

        # Bingkai kelabu nipis luar kertas
        shape_border = new_page.new_shape()
        shape_border.draw_rect(thesis_rect)
        shape_border.finish(color=(0.8, 0.8, 0.8), width=0.5)
        shape_border.commit()

        # -----------------------------------------------------------------
        # 📌 3. GARISAN PEMISAH TEGAK (CENTER DIVIDER)
        # -----------------------------------------------------------------
        shape_divider = new_page.new_shape()
        shape_divider.draw_line(fitz.Point(420, 15), fitz.Point(420, 580))
        shape_divider.finish(color=(0.7, 0.7, 0.7), dashes="[4 4]", width=1)
        shape_divider.commit()

        # -----------------------------------------------------------------
        # 📌 4. KANVAS KANAN: LAPORAN ISU FORMAT (KETINGGIAN DINAMIK)
        # -----------------------------------------------------------------
        raw_issues = all_pages_errors_list[p_num] if p_num < len(all_pages_errors_list) else []
        active_issues = [
            iss for iss in raw_issues 
            if (iss.get("id") or f"{p_num}_{iss.get('msg', '')}") not in ignored_errors
        ]

        # 1. Bina tajuk laporan muka surat mengikut bahasa pilihan (BM/EN)
        title_text = TEXT_I18N[lang_code]["report_title"].format(page_num=p_num + 1)

        # 2. Masukkan ke dalam PDF
        new_page.insert_text(
            fitz.Point(435, 35), 
            title_text, 
            fontsize=13, 
            fontname="helv", 
            color=(0.1, 0.1, 0.1)
        )

        if not active_issues:
            # Dapatkan mesej status mengikut bahasa pilihan (BM/EN)
            text_ok = TEXT_I18N[lang_code]["status_ok"]

            new_page.insert_text(
                fitz.Point(435, 65), 
                text_ok, 
                fontsize=11, 
                fontname="helv", 
                color=(0.06, 0.72, 0.5)
            )
        else:
            # 1. Bina ayat header amaran mengikut pilihan bahasa
            text_header = TEXT_I18N[lang_code]["warning_header"].format(count=len(active_issues))

            # 2. Masukkan ke dalam PDF
            new_page.insert_text(
                fitz.Point(435, 65), 
                text_header, 
                fontsize=10, 
                fontname="helv", 
                color=(0.88, 0.11, 0.28)
            )

            y_pos = 85
            for idx, issue in enumerate(active_issues, 1):
                # Ambil mesej daripada pelbagai nama kunci yang mungkin digunakan
                msg_text = issue.get("msg") or issue.get("message") or issue.get("text") or str(issue)
                msg_clean = str(msg_text).replace("*", "")
                text_content = f"{idx}. {msg_clean}"

                # 📌 Kira ketinggian petak secara dinamik mengikut panjang ayat
                # Anggaran ~65 karakter setiap baris pada lebar petak 385pt
                estimated_lines = max(1, (len(text_content) // 60) + 1)
                box_height = max(32, (estimated_lines * 13) + 10)

                box_rect = fitz.Rect(435, y_pos, 820, y_pos + box_height)
                
                # Lukis petak latar kelabu
                box_shape = new_page.new_shape()
                box_shape.draw_rect(box_rect)
                box_shape.finish(color=(0.85, 0.85, 0.85), fill=(0.97, 0.97, 0.97), width=0.5)
                box_shape.commit()
                
                # Masukkan teks dengan ruang margin dalaman (padding)
                inner_rect = fitz.Rect(441, y_pos + 5, 814, y_pos + box_height - 3)
                new_page.insert_textbox(
                    inner_rect, 
                    text_content, 
                    fontsize=8.5, 
                    fontname="helv", 
                    color=(0.2, 0.2, 0.2)
                )

                y_pos += box_height + 8  # Jarak ke petak seterusnya

                if y_pos > 550:
                    break

    pdf_bytes = combined_doc.tobytes()
    combined_doc.close()
    annotated_doc.close()
    return pdf_bytes

# 📌 INIKAN INITIALIZATION BERSAMA PERISAI SESSION STATE
if "ignored_errors" not in st.session_state:
    st.session_state.ignored_errors = set()

# Inisialisasi wajib di awal skrip app.py (di luar mana-mana fungsi):
for key in ["ignored_errors", "report_pdf_bytes", "annotated_pdf_bytes"]:
    if key not in st.session_state:
        st.session_state[key] = set() if key == "ignored_errors" else None

def draw_dashed_line(draw, p1, p2, color, width=1, dash_len=8, space_len=5):
    """Fungsi pembantu melukis garisan putus-putus"""
    x1, y1 = p1
    x2, y2 = p2
    if y1 == y2:  # Garisan Melintang (Horizontal)
        x = x1
        while x < x2:
            draw.line([(x, y1), (min(x + dash_len, x2), y1)], fill=color, width=width)
            x += dash_len + space_len
    elif x1 == x2:  # Garisan Menegak (Vertical)
        y = y1
        while y < y2:
            draw.line([(x1, y), (x1, min(y + dash_len, y2))], fill=color, width=width)
            y += dash_len + space_len

def add_margin_overlay(doc_page, dpi=120, is_landscape=False):
    # 1. Hasilkan imej asal & tukar ke mod RGBA
    pix = doc_page.get_pixmap(dpi=dpi)
    base_img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples).convert("RGBA")
    
    # 2. Hasilkan lapisan lutsinar (Overlay Layer)
    overlay = Image.new("RGBA", base_img.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(overlay)
    
    # 3. Warna Merah Lutsinar (Alpha=80 untuk bayang-bayang)
    red_transparent = (255, 0, 0, 80) 
    
    # Nisbah mm ke piksel
    px_per_mm = 2.83465 * (dpi / 72.0)
    w_px, h_px = base_img.size
    
    # 📌 PENETAPAN MARGIN TEPAT PIAWAIAN USM:
    # Portrait : Kiri = 40mm (Jilid), Atas/Bawah/Kanan = 25mm
    # Landscape: Atas = 40mm (Jilid), Kiri/Bawah/Kanan = 25mm
    if is_landscape:
        m_top = 40
        m_left = 25   # 👈 Dibaiki: 25mm untuk Landscape
    else:
        m_top = 25
        m_left = 40   # 👈 40mm khas jilid sebelah kiri Portrait
        
    m_bottom = 25
    m_right = 25
    
    top_y = m_top * px_per_mm
    bottom_y = h_px - (m_bottom * px_per_mm)
    left_x = m_left * px_per_mm
    right_x = w_px - (m_right * px_per_mm)
    
    # 4. Lukis 4 Garisan Margin Putus-putus
    draw_dashed_line(draw, (0, top_y), (w_px, top_y), color=red_transparent, width=2)       # Top
    draw_dashed_line(draw, (0, bottom_y), (w_px, bottom_y), color=red_transparent, width=2) # Bottom
    draw_dashed_line(draw, (left_x, 0), (left_x, h_px), color=red_transparent, width=2)     # Left
    draw_dashed_line(draw, (right_x, 0), (right_x, h_px), color=red_transparent, width=2)   # Right
    
    # 5. Gabungkan imej asal dengan lapisan garisan bayang-bayang
    combined = Image.alpha_composite(base_img, overlay)
    return combined.convert("RGB")
# ==========================================
# ⚙️ TETAPAN AWAL APLIKASI STREAMLIT
# ==========================================
st.set_page_config(
    page_title="Semakan Format Tesis USM",
    layout="wide",
    page_icon="📄"
)

st.markdown("""
    <style>
        /* 1. Smooth Scroll */
        html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
            scroll-behavior: smooth !important;
        }

        /* 2. 🎨 STYLING SIDEBAR PREMIUM (THEME UNGU USM) */
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #f5f3ff 0%, #faf5ff 100%) !important;
            border-right: 1px solid #e9d5ff !important;
        }

        /* Teks & Tajuk dalam Sidebar */
        section[data-testid="stSidebar"] h1, 
        section[data-testid="stSidebar"] h2, 
        section[data-testid="stSidebar"] h3, 
        section[data-testid="stSidebar"] h4,
        section[data-testid="stSidebar"] label,
        section[data-testid="stSidebar"] .stMarkdown p {
            color: #4c1d95 !important;
            font-weight: 700 !important;
        }

        /* Kotak Input & Selectbox dalam Sidebar */
        section[data-testid="stSidebar"] div[data-baseweb="input"],
        section[data-testid="stSidebar"] div[data-baseweb="select"] {
            background-color: #ffffff !important;
            border-radius: 10px !important;
            border: 1px solid #d8b4fe !important;
            box-shadow: 0 2px 6px rgba(107, 33, 168, 0.04) !important;
        }

        /* Butang Log Out dalam Sidebar */
        section[data-testid="stSidebar"] button {
            background-color: #ffffff !important;
            color: #dc2626 !important;
            border: 1px solid #fca5a5 !important;
            border-radius: 10px !important;
            font-weight: 700 !important;
            box-shadow: 0 2px 8px rgba(220, 38, 38, 0.08) !important;
            transition: all 0.3s ease !important;
        }

        section[data-testid="stSidebar"] button:hover {
            background-color: #fef2f2 !important;
            border-color: #ef4444 !important;
            color: #b91c1c !important;
            transform: translateY(-1px);
        }
    </style>
    <div id="top-anchor"></div>
""", unsafe_allow_html=True)

PASSWORD_RAHSIA = "USM2026"
APP_VERSION = "v1.2.1"

# Papar versi dan butang info di Sidebar
col_v1, col_v2 = st.sidebar.columns([3, 1])

with col_v1:
    st.caption(f"📌 **Versi Sistem:** {APP_VERSION}")

with col_v2:
    with st.popover("ℹ️ Info"):
        st.markdown(f"### 📋 Log Kemaskini ({APP_VERSION})")
        st.markdown("""
        **v1.2.1**
        * **Garisan Margin Visual Lembut:** Melukis 4 garisan margin putus-putus merah pudar (*faint red*) pada kanvas visual tesis persis paparan *live preview*.
        * **Paparan Teks Isu Dinamik:** Membaiki isu teks ralat terpotong pada kad laporan kanan dengan pengiraan ketinggian petak secara dinamik.
        * **Kotak Merah Ralat PDF:** Memastikan semua petak ralat merah pada teks ditekap 100% lengkap pada visual tesis kanvas kiri.
        * **Nama Fail Muat Turun Dinamik:** Fail laporan PDF yang didownload kini secara automatik mengikut nama fail tesis asal (`Laporan_Gabungan_<Nama_Fail_Asal>.pdf`).

        ---

        **v1.2.0**
        * **Penapis Kata Kerja Tajuk (*Narrative Verb Filter*):**
          * Mengelakkan ralat palsu Tajuk Rajah/Jadual apabila ayat bermula dengan kata kerja (*shows, presents, summarizes, depicts*).
        * **Semakan Font Kritis:**
          * Mengetatkan pengesanan font tidak sah (contoh: Cambria / Cambria-Italic) walaupun untuk frasa/perkataan pendek.
        * **Fungsi *Bypass All* Per Muka Surat:**
          * Menambah *master checkbox* di bahagian bawah setiap muka surat untuk mengabaikan semua ralat serentak.
        * **Kiraan Isu Dinamik & Pembaikan UI:**
          * Tajuk expander memaparkan jumlah ralat aktif secara *real-time* (contoh: `⚠️ Ada Isu: 4`).
          * Membaiki ralat duplikasi paparan muka surat.
        """)

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False


def logout():
    st.session_state.authenticated = False
    st.rerun()


if not st.session_state.authenticated:
    
    # =========================================================================
    # 🎨 1. CSS REKA BENTUK PREMIUM (USM PURPLE & GOLD ACCENTS)
    # =========================================================================
    st.markdown("""
        <style>
        /* Gradient Tajuk Utama */
        .main-header {
            text-align: center;
            font-size: 2.2rem;
            font-weight: 800;
            background: linear-gradient(135deg, #4c1d95 0%, #6b21a8 50%, #d97706 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-top: 5px;
            margin-bottom: 2px;
        }
        
        .sub-header {
            text-align: center;
            color: #64748b;
            font-size: 0.9rem;
            font-weight: 500;
            margin-bottom: 25px;
        }

        /* Kad Kad Log Masuk Top Header */
        .login-card-header {
            background: #ffffff;
            padding: 22px 25px 12px 25px;
            border-radius: 16px 16px 0 0;
            border: 1px solid #e2e8f0;
            border-bottom: none;
            box-shadow: 0 10px 25px -5px rgba(107, 33, 168, 0.08);
            border-top: 5px solid #6b21a8;
            text-align: center;
        }

        .login-title {
            color: #1e293b;
            font-size: 1.3rem;
            font-weight: 700;
            margin-bottom: 4px;
        }

        .login-subtitle {
            color: #64748b;
            font-size: 0.85rem;
        }

        /* Styling Kad Form & Butang Submit */
        div[data-testid="stForm"] {
            border-radius: 0 0 16px 16px !important;
            border: 1px solid #e2e8f0 !important;
            border-top: none !important;
            box-shadow: 0 10px 25px -5px rgba(107, 33, 168, 0.08) !important;
            background-color: #ffffff !important;
            padding: 5px 25px 25px 25px !important;
        }

        div[data-testid="stForm"] button {
            background: linear-gradient(135deg, #6b21a8 0%, #581c87 100%) !important;
            color: #ffffff !important;
            font-weight: 600 !important;
            font-size: 0.95rem !important;
            border-radius: 10px !important;
            border: none !important;
            box-shadow: 0 4px 14px rgba(107, 33, 168, 0.3) !important;
            transition: all 0.3s ease !important;
        }

        div[data-testid="stForm"] button:hover {
            background: linear-gradient(135deg, #7e22ce 0%, #6b21a8 100%) !important;
            box-shadow: 0 6px 18px rgba(107, 33, 168, 0.45) !important;
            transform: translateY(-1px);
        }

        /* Kad Penafian Modern */
        .disclaimer-card {
            background: #fffbe0;
            border-left: 4px solid #f59e0b;
            padding: 18px 22px;
            border-radius: 12px;
            color: #78350f;
            font-size: 0.88rem;
            line-height: 1.6;
            box-shadow: 0 4px 12px rgba(245, 158, 11, 0.08);
            margin-top: 20px;
        }
        </style>
    """, unsafe_allow_html=True)

    # =========================================================================
    # 📌 2. TAJUK UTAMA (CENTERED GRADIENT)
    # =========================================================================
    st.markdown('<div class="main-header">🎓 Semakan Format Tesis USM</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="sub-header">📌 Versi Sistem: {APP_VERSION} | Universiti Sains Malaysia</div>', unsafe_allow_html=True)

    # =========================================================================
    # 🔒 3. KAD LOG MASUK CENTERED (GUNAKAN FORM & PASSWORD_RAHSIA ABANG)
    # =========================================================================
    col_left, col_center, col_right = st.columns([0.8, 2, 0.8])

    with col_center:
        st.markdown("""
            <div class="login-card-header">
                <div class="login-title">🔒 Log Masuk Akses</div>
                <div class="login-subtitle">Masukkan kata laluan akses untuk memulakan semakan</div>
            </div>
        """, unsafe_allow_html=True)

        with st.form("login_form"):
            password_input = st.text_input(
                "Masukkan Kata Laluan Akses:",
                type="password",
                placeholder="••••••••••••",
                label_visibility="collapsed"
            )
            submit_button = st.form_submit_button(
                "🔑 Log Masuk Akses", use_container_width=True
            )

            if submit_button:
                if password_input == PASSWORD_RAHSIA:
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.error("🔑 Kata laluan salah. Sila cuba lagi!")

    # =========================================================================
    # ⚠️ KAD PENAFIAN (DISCLAIMER) MODERN & LENGKAP
    # =========================================================================
    col_d1, col_d2, col_d3 = st.columns([0.3, 3.4, 0.3])
    with col_d2:
        st.markdown("""
            <div class="disclaimer-card">
                <strong style="font-size:0.95rem; color:#92400e;">⚠️ Penafian (Disclaimer) & Panduan Penggunaan:</strong><br><br>
                1. <strong>Sistem Bantu Semak Otomatik:</strong> Aplikasi ini dibangunkan sebagai <strong>alat bantuan awal</strong> untuk mengesan ralat format utama secara pantas.<br>
                2. <strong>Sifat Fail PDF:</strong> Semakan berasaskan teks PDF digital asli. Fail imbasan (<em>scanned document</em>) atau gambar tanpa lapisan OCR mungkin tidak dapat dikesan secara tepat.<br>
                3. <strong>Kelulusan Rasmi & Semakan Akhir:</strong> Keputusan semakan aplikasi ini <strong>bukan penentu mutlak</strong>. Pengguna tetap bertanggungjawab membuat semakan manual akhir merujuk <em>Garis Panduan Penulisan Tesis USM</em> rasmi.<br>
                4. <strong>Kerahsiaan Data & Fail:</strong> Fail PDF diproses secara <em>in-memory</em> sahaja dan <strong>tidak disimpan secara kekal</strong> dalam mana-mana pelayan.<br>
                5. <strong>Tanggungjawab Pengguna:</strong> Pembangun sistem tidak bertanggungjawab atas sebarang penolakan atau isu format semasa penyerahan rasmi tesis kepada IPS USM.
            </div>
        """, unsafe_allow_html=True)

    # ==================== FOOTER HAK CIPTA ====================
    paparkan_footer()

    st.stop()

# ==================== SIDEBAR & TETAPAN ====================
with st.sidebar:
    # 1. BUTANG LOG OUT
    if st.button("🚪 Log Out", type="secondary", use_container_width=True):
        logout()
        
    st.markdown("---")

    # 🌐 2. PILIHAN BAHASA LAPORAN (DI ATAS TETAPAN TEMPLAT)
    report_lang_choice = st.selectbox(
        "🌐 Bahasa Laporan / Language",
        ["Bahasa Melayu (BM)", "English (EN)"]
    )
    # Setkan kod bahasa untuk digunakan dalam skrip (BM atau EN)
    lang_code = "EN" if "English" in report_lang_choice else "BM"

    #st.markdown("---")

    # ⚙️ 3. TETAPAN TEMPLAT TESIS
    st.header("⚙️ Tetapan Templat Tesis")

    default_left, default_right, default_top, default_bottom = 40.0, 25.0, 25.0, 25.0
    default_fonts = [
        "Times New Roman",
        "TimesNewRoman",
        "Arial",
        "Helvetica",
        "TeXGyreTermes",
        "TeXGyreTermesX",
        "TeX Gyre Termes",
    ]

    preset = st.selectbox(
        "Pilih Templat Universiti",
        ["USM (Universiti Sains Malaysia)", "Custom (Manual)"],
    )

    if preset == "USM (Universiti Sains Malaysia)":
        default_left, default_right, default_top, default_bottom = 40.0, 25.0, 25.0, 25.0
        default_fonts = [
            "Times New Roman",
            "TimesNewRoman",
            "Arial",
            "Helvetica",
            "TeXGyreTermes",
            "TeXGyreTermesX",
            "TeX Gyre Termes",
        ]
    else:
        default_left, default_right, default_top, default_bottom = 40.0, 25.0, 25.0, 25.0
        default_fonts = ["Times New Roman", "Arial"]

    margin_left_mm = st.number_input(
        "Margin Kiri (mm)", min_value=10.0, max_value=60.0, value=default_left, step=1.0
    )
    margin_right_mm = st.number_input(
        "Margin Kanan (mm)", min_value=10.0, max_value=60.0, value=default_right, step=1.0
    )
    margin_top_mm = st.number_input(
        "Margin Atas (mm)", min_value=10.0, max_value=60.0, value=default_top, step=1.0
    )
    margin_bottom_mm = st.number_input(
        "Margin Bawah (mm)", min_value=10.0, max_value=60.0, value=default_bottom, step=1.0
    )

    allowed_fonts = st.multiselect(
        "Jenis Font Dibenarkan",
        [
            "Times New Roman",
            "TimesNewRoman",
            "Arial",
            "Calibri",
            "Garamond",
            "Helvetica",
            "TeX Gyre Termes",
            "TeXGyreTermes",
            "TeXGyreTermesX",
        ],
        default=default_fonts,
    )

    semak_caption = st.checkbox(
        "Aktifkan Semakan Format Tajuk Jadual & Rajah",
        value=True,
        help="Semak format tajuk jadual dan tajuk rajah mengikut saiz, jenis font, dan susunan."
    )

    abaikan_teks_dalam_gambar = st.sidebar.checkbox(
        "Abaikan Teks Dalam Gambar / Rajah",
        value=True,
        help="Abaikan ralat font untuk label atau teks yang bertindih di atas gambar/rajah."
    )

    abaikan_appendix = st.checkbox(
        "Abaikan Semakan Font pada Lampiran (Appendix)",
        value=True,
        help="Abaikan semakan jenis dan saiz font untuk muka surat bahagian Lampiran."
    )

    abaikan_pagenum_appendix = st.sidebar.checkbox(
        "Abaikan Semakan No. M/S di Lampiran (Appendices)",
        value=True,
        help="Abaikan semakan nombor muka surat bermula dari tajuk Lampiran utama."
    )

# CONVERSION CONSTANTS
MM_TO_PT = 72 / 25.4
MARGIN_LEFT_PT = margin_left_mm * MM_TO_PT
MARGIN_RIGHT_PT = margin_right_mm * MM_TO_PT
MARGIN_TOP_PT = margin_top_mm * MM_TO_PT
MARGIN_BOTTOM_PT = margin_bottom_mm * MM_TO_PT

MATH_SYMBOL_FONTS = [
    "cambriamath", "symbol", "mtextra", "math", 
    "wingdings", "webdings", "msmincho", "segoeui-symbol"
]

def is_roman_numeral(val_str):
    """Fungsi menyemak secara dinamik sama ada perkataan ialah nombor Roman valid"""
    val_str = val_str.lower().strip()
    if not val_str:
        return False
    roman_pattern = r"^M{0,4}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})$"
    return bool(re.match(roman_pattern, val_str, re.IGNORECASE))

TABLE_PREFIX_REGEX = re.compile(r"^\s*(Table|Jadual)\s+\d+(\.\d+)*", re.IGNORECASE)
FIGURE_PREFIX_REGEX = re.compile(r"^\s*(Figure|Rajah)\s+\d+(\.\d+)*", re.IGNORECASE)
IN_TEXT_CITATION_REGEX = re.compile(r"^\s*(Figure|Rajah|Table|Jadual)\s+\d+(\.\d+)*\.\s", re.IGNORECASE)
DOT_LEADER_REGEX = re.compile(r"\.{3,}\s*\d+|\b\d+\s*$", re.IGNORECASE)

VERB_KEYWORDS_REGEX = re.compile(
    r"\b("
    r"shows?|showing|showed|"
    r"presents?|presenting|presented|"
    r"summarizes?|summarised|summarising|summarize|summarise|summary|"
    r"illustrates?|illustrating|illustrated|"
    r"depicts?|depicting|depicted|"
    r"lists?|listing|listed|"
    r"compares?|comparing|compared|"
    r"indicates?|indicating|indicated|"
    r"displays?|displaying|displayed|"
    r"describes?|describing|described|"
    r"provides?|providing|provided|"
    r"menunjukkan|menyenaraikan|mencatatkan|memaparkan|menggambarkan|merumuskan|membandingkan|menyediakan|memberikan"
    r")\b",
    re.IGNORECASE
)

def generate_pdf_report(filtered_errors, total_pages):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    # 1. Dapatkan teks tajuk & subtajuk mengikut bahasa (BM/EN)
    main_title = TEXT_I18N[lang_code]["pdf_main_title"]
    sub_info = TEXT_I18N[lang_code]["pdf_total_pages"].format(total_pages=total_pages)

    # 2. Tajuk Utama
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, main_title, new_x="LMARGIN", new_y="NEXT", align="C")

    # 3. Subtajuk Info
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 6, sub_info, new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(5)

    if not filtered_errors:
        pdf.set_font("Helvetica", "B", 12)
        # Dapatkan mesej tiada isu
        msg_perfect = TEXT_I18N[lang_code]["no_issue"]
        pdf.cell(0, 10, msg_perfect, new_x="LMARGIN", new_y="NEXT", align="C")
    else:
        pdf.set_font("Helvetica", "B", 11)
        # Dapatkan tajuk kolum jadual dinamik
        col_page = TEXT_I18N[lang_code]["pdf_col_page"]
        col_details = TEXT_I18N[lang_code]["pdf_col_details"]
        
        pdf.cell(30, 8, col_page, border=1, align="C")
        pdf.cell(160, 8, col_details, border=1, align="C", new_x="LMARGIN", new_y="NEXT")

        pdf.set_font("Helvetica", "", 9)
        for item in filtered_errors:
            page_str = f"MS {item['page']}"
            issue_str = item["msg"].replace("*", "")
            
            x_start = pdf.get_x()
            y_start = pdf.get_y()
            pdf.cell(30, 8, page_str, border=1, align="C")
            pdf.set_xy(x_start + 30, y_start)
            # fpdf2 mengendalikan layout multi_cell dengan lebih baik
            pdf.multi_cell(160, 8, issue_str, border=1, new_x="LMARGIN", new_y="NEXT")

    # Dalam fpdf2, pdf.output() terus memulangkan bytearray/bytes secara terus
    return bytes(pdf.output())

def generate_annotated_thesis(doc_input, all_pages_errors, ignored_set):
    # Optimasi ingatan menggunakan tobytes()
    annotated_doc = fitz.open(stream=doc_input.tobytes(), filetype="pdf")

    for page_num, errors in enumerate(all_pages_errors):
        page = annotated_doc[page_num]
        for i, err in enumerate(errors):
            err_id = f"p{page_num+1}_{i}"
            if err.get("bbox") and err_id not in ignored_set:
                page.draw_rect(err["bbox"], color=(1, 0, 0), width=1.5)

    out_bytes = annotated_doc.tobytes()
    annotated_doc.close()
    return out_bytes


def create_download_button_html(file_bytes, filename, button_text, color="#2563eb"):
    b64 = base64.b64encode(file_bytes).decode()
    href = f"data:application/pdf;base64,{b64}"
    return f"""
    <a href="{href}" download="{filename}" style="text-decoration: none;">
        <div style="
            background-color: {color};
            color: white;
            padding: 12px 20px;
            text-align: center;
            border-radius: 8px;
            font-weight: bold;
            font-size: 15px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            transition: 0.3s;
            cursor: pointer;
            margin-top: 10px;">
            {button_text}
        </div>
    </a>
    """

# =========================================================================
# 🎨 CSS KEMASKINI PREMIUM (TAJUK BESAR & BUTANG KONTRAST TINGGI)
# =========================================================================
st.markdown("""
    <style>
    /* 1. Tajuk Utama BESAR & MANTAP */
    .main-header-large {
        text-align: center;
        font-size: 2.8rem !important;
        font-weight: 900 !important;
        background: linear-gradient(135deg, #4c1d95 0%, #7e22ce 50%, #d97706 100%);
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        margin-top: 10px !important;
        margin-bottom: 6px !important;
        line-height: 1.25 !important;
        letter-spacing: -0.5px;
    }
    
    .sub-header-large {
        text-align: center;
        color: #64748b !important;
        font-size: 1.05rem !important;
        font-weight: 600 !important;
        margin-bottom: 35px !important;
    }

    /* 2. Kad & Kotak Dropzone Upload */
    .upload-card-header {
        background: #ffffff;
        padding: 22px 28px 12px 28px;
        border-radius: 16px 16px 0 0;
        border: 1px solid #e2e8f0;
        border-bottom: none;
        border-top: 5px solid #6b21a8;
        box-shadow: 0 10px 25px -5px rgba(107, 33, 168, 0.08);
    }

    .upload-title {
        color: #1e293b;
        font-size: 1.25rem;
        font-weight: 800;
        margin-bottom: 4px;
    }

    .upload-subtitle {
        color: #64748b;
        font-size: 0.9rem;
    }

    /* Styling Dropzone Container */
    section[data-testid="stFileUploaderDropzone"] {
        background-color: #faf5ff !important;
        border: 2px dashed #9333ea !important;
        border-radius: 0 0 16px 16px !important;
        padding: 30px 20px !important;
        box-shadow: 0 10px 25px -5px rgba(107, 33, 168, 0.08) !important;
        transition: all 0.3s ease !important;
    }

    section[data-testid="stFileUploaderDropzone"]:hover {
        background-color: #f3e8ff !important;
        border-color: #6b21a8 !important;
    }

    /* 3. PEMBAIKAN BUTANG UPLOAD (TULISAN PUTIH TERANG - TIDAK TENGGELAM) */
    section[data-testid="stFileUploaderDropzone"] button {
        background: linear-gradient(135deg, #6b21a8 0%, #581c87 100%) !important;
        border-radius: 10px !important;
        padding: 8px 22px !important;
        border: none !important;
        box-shadow: 0 4px 14px rgba(107, 33, 168, 0.35) !important;
    }

    /* PAKSA TEKS & IKON JADI PUTIH TERANG (PINTAS SEBAB STREAMLIT) */
    section[data-testid="stFileUploaderDropzone"] button,
    section[data-testid="stFileUploaderDropzone"] button *,
    section[data-testid="stFileUploaderDropzone"] button p,
    section[data-testid="stFileUploaderDropzone"] button span,
    section[data-testid="stFileUploaderDropzone"] button div {
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important; /* KUNCI UNTUK SELESAIKAN ISU TULISAN GELAP */
        font-weight: 700 !important;
        font-size: 0.95rem !important;
        opacity: 1 !important;
    }

    section[data-testid="stFileUploaderDropzone"] button:hover {
        background: linear-gradient(135deg, #7e22ce 0%, #6b21a8 100%) !important;
        box-shadow: 0 6px 18px rgba(107, 33, 168, 0.5) !important;
        transform: translateY(-1px);
    }

    /* Teks arahan sebelah butang (200MB per file • PDF) */
    section[data-testid="stFileUploaderDropzone"] [data-testid="stMarkdownContainer"] p {
        color: #581c87 !important;
        font-weight: 600 !important;
    }
    </style>
""", unsafe_allow_html=True)

# =========================================================================
# 📌 TAJUK UTAMA (BESAR & KEMAS)
# =========================================================================
st.markdown('<div class="main-header-large">🎓 Sistem Semakan Format Tesis USM</div>', unsafe_allow_html=True)
st.markdown(f'<div class="sub-header-large">📌 Versi Sistem: {APP_VERSION} | Modul Semakan Automatik USM Standard</div>', unsafe_allow_html=True)

# =========================================================================
# 📤 KAD MUAT NAIK FAIL (MANTAP & TEKS PUTIH CLEAR)
# =========================================================================
st.markdown("""
    <div class="upload-card-header">
        <div class="upload-title">📤 Muat Naik Fail PDF Tesis</div>
        <div class="upload-subtitle">Sila pilih atau seret fail PDF tesis untuk diproses oleh sistem semakan.</div>
    </div>
""", unsafe_allow_html=True)

uploaded_file = st.file_uploader(
    "Muat Naik Fail PDF Tesis", 
    type=["pdf"], 
    label_visibility="collapsed"
)

# =========================================================================
# ⚙️ 4. LOGIK PEMPROSESAN FAIL PDF (KEKALKAN LOGIK ASAL ABANG)
# =========================================================================
if uploaded_file is not None:
    # 📌 Gunakan .getvalue() mengekalkan data PDF
    pdf_bytes = uploaded_file.getvalue()
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")

    # 📌 SEMAKAN 1: Buka PDF jika dikunci dengan Kata Laluan (Password)
    if doc.is_encrypted:
        password = st.text_input("🔒 PDF ini dilindungi kata laluan. Sila masukkan password:", type="password")
        
        if password:
            # Cuba buka PDF guna password yang dimasukkan
            if doc.authenticate(password):
                st.success("🔓 Kata laluan betul! Memproses tesis...")
            else:
                st.error("❌ Kata laluan salah. Sila masukkan kata laluan yang betul.")
                st.stop()
        else:
            st.warning("⚠️ Sila masukkan kata laluan di atas untuk meneruskan semakan.")
            st.stop()

    # 📌 SEMAKAN 2: Pastikan dokumen mempunyai muka surat
    if len(doc) == 0:
        st.error("❌ Fail PDF ini kosong atau rosak.")
        st.stop()

    st.success(f"Fail berjaya dimuat naik! Jumlah muka surat: {len(doc)}")

    if "ignored_errors" not in st.session_state:
        st.session_state.ignored_errors = set()
    if "report_pdf_bytes" not in st.session_state:
        st.session_state.report_pdf_bytes = None
    if "annotated_pdf_bytes" not in st.session_state:
        st.session_state.annotated_pdf_bytes = None

    def toggle_bypass(err_id):
        # 📌 Perisai Tambahan: Auto-create jika session_state hilang lepas clear cache
        if "ignored_errors" not in st.session_state:
            st.session_state.ignored_errors = set()

        if err_id in st.session_state.ignored_errors:
            st.session_state.ignored_errors.remove(err_id)
        else:
            st.session_state.ignored_errors.add(err_id)

        st.session_state.report_pdf_bytes = None
        st.session_state.annotated_pdf_bytes = None
        st.rerun()

    detected_issues = []
    all_pages_errors_list = []
    is_previous_list_page = False
    in_appendix_section = False

    for page_num in range(len(doc)):
        page = doc[page_num]
        rect = page.rect
        blocks = page.get_text("dict")["blocks"]
        images_info = page.get_image_info()
        drawings = page.get_drawings()

        full_page_text = page.get_text()
        page_text_lower = full_page_text.lower()

        is_appendix_page = any(
            k in page_text_lower
            for k in ["appendix", "appendices", "lampiran"]
        )

        has_list_header = any(
            k in page_text_lower
            for k in [
                "list of tables",
                "list of figures",
                "senarai jadual",
                "senarai rajah",
                "table of contents",
                "kandungan",
            ]
        )

        has_dot_leaders = bool(DOT_LEADER_REGEX.search(full_page_text))
        is_list_page = has_list_header or (is_previous_list_page and has_dot_leaders)
        is_previous_list_page = is_list_page

        # 📌 1. SEMAK ORIENTASI SEBENAR (AMBIL KIRA ROTASI INTERNAL PDF)
        if page.rotation in (90, 270):
            is_landscape = rect.height > rect.width
        else:
            is_landscape = rect.width > rect.height

        page_errors = []

        # -----------------------------------------------------------------
        # 📌 DEFINISI MARGIN USM SEBENAR (1mm ≈ 2.83465 pt)
        # -----------------------------------------------------------------
        MARGIN_25MM_PT = 25 * 2.83465  # ~70.87 pt
        MARGIN_40MM_PT = 40 * 2.83465  # ~113.39 pt

        if is_landscape:
            # LANDSCAPE: Top 40mm (sebab ruang jilid), Left/Right/Bottom 25mm
            cur_m_top = MARGIN_40MM_PT
            cur_m_bottom = rect.height - MARGIN_25MM_PT
            cur_m_left = MARGIN_25MM_PT
            cur_m_right = rect.width - MARGIN_25MM_PT
            top_limit_label = "40mm"
            limit_mm = 40
        else:
            # PORTRAIT: Top 25mm, Left 40mm (sebab ruang jilid), Right/Bottom 25mm
            cur_m_top = MARGIN_25MM_PT
            cur_m_bottom = rect.height - MARGIN_25MM_PT
            cur_m_left = MARGIN_40MM_PT
            cur_m_right = rect.width - MARGIN_25MM_PT
            top_limit_label = "25mm"
            limit_mm = 25

        # -----------------------------------------------------------------
        # PASS 1: PRE-SCANNING NOMBOR MUKA SURAT (LANDSCAPE LEFT SHIELD)
        # -----------------------------------------------------------------
        pagenum_rects = []
        has_pagenum_found = False

        # Kumpul semua shape/kotak yang ada fill
        filled_shapes = [
            path["rect"] for path in page.get_drawings() 
            if path.get("fill") is not None and path.get("rect")
        ]

        page_dict = page.get_text("dict")

        for b in page_dict.get("blocks", []):
            if "lines" not in b:
                continue
            for line in b["lines"]:
                for span in line.get("spans", []):
                    span_color = span.get("color", 0)

                    # Tapis teks berwarna putih
                    if span_color == 16777215:
                        continue 

                    word_str = span.get("text", "").strip()
                    clean_w = re.sub(r"[^a-zA-Z0-9]", "", word_str.lower())

                    is_valid_num = (clean_w.isdigit() and len(clean_w) <= 3) or is_roman_numeral(clean_w)

                    if is_valid_num and clean_w:
                        s_bbox = fitz.Rect(span["bbox"])
                        wx0, wy0, wx1, wy1 = s_bbox.x0, s_bbox.y0, s_bbox.x1, s_bbox.y1

                        # 📌 1. TAPIS KOTAK PUTIH HANYA DI ZON BAWAH (TRIK HIDE NO BAWAH PELAJAR)
                        is_at_bottom_zone = wy0 > (rect.height - 100)
                        if is_at_bottom_zone:
                            is_covered_by_shape = any(
                                shape.intersects(s_bbox) or shape.contains(s_bbox) 
                                for shape in filled_shapes
                            )
                            if is_covered_by_shape:
                                continue  # Skip nombor bawah yang ditutup kotak putih!

                        # 📌 2. ZON MARGIN SAH (LONGGARKAN KIRI LANDSCAPE KEPADA 110PT)
                        left_margin_limit = 110 if is_landscape else 70
                        is_in_margin_zone = (
                            wx0 < left_margin_limit or 
                            wx1 > (rect.width - 70) or 
                            wy0 < 70 or 
                            wy1 > (rect.height - 70)
                        )

                        if is_in_margin_zone:
                            has_pagenum_found = True
                            pagenum_rects.append(fitz.Rect(wx0 - 5, wy0 - 5, wx1 + 5, wy1 + 5))

                            # Amaran hanya diberi jika nombor di bawah TIDAK DITUTUP kotak (memang terdedah)
                            if is_landscape and is_at_bottom_zone:
                                # 1. Bina mesej amaran berdasarkan bahasa pilihan (BM/EN)
                                msg_landscape = TEXT_I18N[lang_code]["landscape_page_num"].format(num=word_str)

                                page_errors.append({
                                    "msg": msg_landscape,
                                    "bbox": (wx0, wy0, wx1, wy1),
                                })
        # -----------------------------------------------------------------
        # 📌 SEMAKAN TAJUK BAB (PERISAI PENGESANAN TOC MATS/MULTI-PAGE)
        # -----------------------------------------------------------------
        # 1. Semak tajuk TOC
        has_toc_header = any(k in full_page_text.upper() for k in ["TABLE OF CONTENTS", "SENARAI KANDUNGAN"])
        
        # 2. Pengesan Muka Surat Sambungan TOC: Kira jumlah garisan bertitik (...) dalam halaman ini
        dot_leaders_count = len(re.findall(r'[\.\…]{3,}', full_page_text)) + len(re.findall(r'\.\s*\.\s*\.', full_page_text))
        
        # Jika ada tajuk TOC ATAU ada sekurang-kurangnya 3 garisan bertitik -> INI HALAMAN TOC!
        is_toc_page = has_toc_header or (dot_leaders_count >= 3)

        if not is_toc_page:
            blocks = page.get_text("blocks")
            chapter_blocks = []

            for b in blocks:
                clean_btext = " ".join(b[4].split()).strip()
                if clean_btext:
                    chapter_blocks.append({
                        "text": clean_btext,
                        "x0": b[0], "y0": b[1], "x1": b[2], "y1": b[3],  # 📌 Ditambah semula untuk elak KeyError
                        "bbox": (b[0], b[1], b[2], b[3])
                    })

            for item in chapter_blocks:
                text = item["text"]

                # 📌 PERISAI TEKS NARATIF PERENGGAN (Contoh: "In Chapter 3, we discuss...")
                is_paragraph_sentence = text.endswith(".") or len(text.split()) > 12
                is_not_uppercase_heading = not re.search(r'^(CHAPTER|BAB)\s+\d+', text)

                if is_paragraph_sentence or is_not_uppercase_heading:
                    continue

                # KES TAJUK BAB SEBENAR (Hanya disemak di luar muka surat TOC)
                if re.search(r'^(CHAPTER|BAB)\s+(\d+|[IVXLCDM]+)\s+[A-Z0-9\s\:\-\&\(\)]{2,}$', text):
                    # 1. Bina mesej ralat mengikut bahasa pilihan (BM/EN)
                    msg_chapter = TEXT_I18N[lang_code]["chapter_title_same_line"].format(text=text)

                    page_errors.append({
                        "msg": msg_chapter,
                        "bbox": item["bbox"],
                    })
                    break

                # KES 2: Jika 'CHAPTER 1' & 'INTRODUCTION' berasingan tapi di paras Y yang sama
                elif re.match(r'^(CHAPTER|BAB)\s+(\d+|[IVXLCDM]+)$', text):
                    for other_item in chapter_blocks:
                        if item == other_item:
                            continue
                        
                        same_y_level = abs(item["y0"] - other_item["y0"]) < 15
                        is_on_right = other_item["x0"] >= item["x1"] - 10

                        if same_y_level and is_on_right:
                            clean_title_snippet = other_item["text"][:25]
                            
                            # 1. Bina mesej ralat mengikut bahasa pilihan (BM/EN)
                            msg_y_level = TEXT_I18N[lang_code]["chapter_same_y_level"].format(
                                text=text, 
                                snippet=clean_title_snippet
                            )

                            page_errors.append({
                                "msg": msg_y_level,
                                "bbox": item["bbox"],
                            })
                            break

        # -----------------------------------------------------------------
        # 📌 PEMURNIAN: DETEKSI MUKA SURAT TAJUK / KULIT (TITLE PAGE)
        # -----------------------------------------------------------------
        is_page_1_or_2 = page_num in [0, 1]
        has_usm_keyword = "UNIVERSITI SAINS MALAYSIA" in full_page_text.upper()
        has_fulfilment = ("THESIS SUBMITTED IN FULFILMENT" in full_page_text.upper() or 
                          "TESIS DISERAHKAN BAGI MEMENUHI" in full_page_text.upper())
        
        is_title_or_cover = is_page_1_or_2 and (has_usm_keyword or has_fulfilment or page_num == 0)

        # -----------------------------------------------------------------
        # 📌 SEMAKAN MARGIN (DIBALUT: DIABAIKAN JIKA MUKA SURAT TAJUK)
        # -----------------------------------------------------------------
        if not is_title_or_cover:
            top_margin_violations = []

            # 1. SEMAK SEMUA BLOK TEKS
            for block in page.get_text("blocks"):
                bx0, by0, bx1, by1, btext = block[0], block[1], block[2], block[3], block[4]
                block_rect = fitz.Rect(bx0, by0, bx1, by1)

                is_pagenum_block = any(block_rect.intersects(p_rect) for p_rect in pagenum_rects)

                clean_btext = btext.strip()
                is_pure_num = bool(re.search(r'^\s*\d{1,4}\s*$', clean_btext)) or is_roman_numeral(re.sub(r"[^a-zA-Z0-9]", "", clean_btext.lower()))
                in_margin_zone = (bx0 < 70 or bx1 > (rect.width - 70) or by0 < 70 or by0 > (rect.height - 70))

                if is_pagenum_block or (is_pure_num and in_margin_zone) or not clean_btext:
                    continue

                # Semak jika melanggar garisan margin atas
                if by0 < (cur_m_top - 2.0):
                    actual_y_mm = round(by0 / 2.83465, 1)
                    clean_snippet = " ".join(btext.split())[:35]
                    
                    top_margin_violations.append({
                        "y0": by0,
                        "msg": TEXT_I18N[lang_code]["margin_top"].format(
                            limit=limit_mm, 
                            text=clean_snippet, 
                            val=actual_y_mm
                        ),
                        "bbox": (bx0, by0, bx1, by1),
                    })

            # 2. SEMAK GARISAN JADUAL / VECTOR DRAWINGS
            for path in page.get_drawings():
                d_rect = path.get("rect")
                if d_rect:
                    dy0 = d_rect[1]
                    if dy0 < (cur_m_top - 2.0) and dy0 > 30.0:
                        # 1. Kira nilai kedudukan dalam mm
                        actual_y_mm = round(dy0 / 2.83465, 1)

                        # 2. Bina mesej amaran berdasarkan bahasa pilihan (BM/EN)
                        msg_table_top = TEXT_I18N[lang_code]["table_line_margin_top"].format(
                            limit=40, 
                            val=actual_y_mm
                        )

                        top_margin_violations.append({
                            "y0": dy0,
                            "msg": msg_table_top,
                            "bbox": d_rect,
                        })

            # 3. LAPORKAN ELEMEN PALING ATAS (Y0 PALING KECIL)
            if top_margin_violations:
                top_margin_violations.sort(key=lambda x: x["y0"])
                highest_violation = top_margin_violations[0]
                
                page_errors.append({
                    "msg": highest_violation["msg"],
                    "bbox": highest_violation["bbox"],
                })

        # -----------------------------------------------------------------
        # 📌 PEMURNIAN PINTAR: DETEKSI JENIS MUKA SURAT BERDASARKAN KANDUNGAN
        # -----------------------------------------------------------------
        is_page_1_or_2 = page_num in [0, 1]
        
        # Pengesanan Muka Surat Cover / Title Page (Mestilah berada di Page 1 atau 2 SAHAJA)
        has_usm_keyword = "UNIVERSITI SAINS MALAYSIA" in full_page_text.upper()
        has_fulfilment = ("THESIS SUBMITTED IN FULFILMENT" in full_page_text.upper() or 
                          "TESIS DISERAHKAN BAGI MEMENUHI" in full_page_text.upper())
        
        # 📌 KEMASKINI: Muka surat 1 (page_num == 0) automatik dianggap Title/Cover Page
        is_title_or_cover = is_page_1_or_2 and (has_usm_keyword or has_fulfilment or page_num == 0)

        # Pengesanan Declaration Page
        declaration_kw = ["DECLARATION", "PENGAKUAN", "I HEREBY DECLARE", "SAYA DENGAN INI MENGAKU"]
        is_declaration_page = any(kw in full_page_text.upper() for kw in declaration_kw) and not is_title_or_cover

        # -----------------------------------------------------------------
        # 1. SEMAKAN NOMBOR MUKA SURAT (LARANG DI COVER & TITLE PAGE / PAGE 1 & 2)
        # -----------------------------------------------------------------
        if (is_title_or_cover or is_declaration_page) and has_pagenum_found:
            page_type_label = "Title/Cover Page" if is_title_or_cover else "Declaration Page"
            page_errors.append({
                "msg": f"{page_type_label}: Nombor muka surat TIDAK BOLEH dipaparkan.",
                "bbox": None,
            })

        # -----------------------------------------------------------------
        # 2. SEMAKAN BULAN DAN TAHUN (HANYA UNTUK PAGE 1 & 2)
        # -----------------------------------------------------------------
        if is_title_or_cover and page_num == 1:
            month_year_pattern = re.compile(
                r"\b(JANUARY|FEBRUARY|MARCH|APRIL|MAY|JUNE|JULY|AUGUST|SEPTEMBER|OCTOBER|NOVEMBER|DECEMBER|"
                r"JANUARI|FEBRUARI|MAC|MEI|JUN|JULAI|OGOS|SEPTEMBER|OKTOBER|DISEMBER)\s+20\d{2}\b",
                re.IGNORECASE
            )
            if not month_year_pattern.search(full_page_text):
                # 1. Bina mesej ralat mengikut bahasa pilihan (BM/EN)
                msg_month_year = TEXT_I18N[lang_code]["title_page_month_year"]

                page_errors.append({
                    "msg": msg_month_year,
                    "bbox": None,
                })

        # -----------------------------------------------------------------
        # 3. SYARAT PENGEQUALIAN & SEMAKAN UNTUK PAGE BIASA (PAGE 3+)
        # -----------------------------------------------------------------
        page_text_lower = full_page_text.lower()
        is_other_exempted = any(
            k in page_text_lower for k in ["list of publications", "publication", "penerbitan"]
        )

        # 📌 DETEKSI MUKA SURAT PEMISAH UTAMA (APPENDICES / LAMPIRAN)
        # Hanya mengecualikan pemisah utama "APPENDICES" / "LAMPIRAN", bukan "APPENDIX A"
        full_text_upper = full_page_text.upper()
        is_appendices_header = "APPENDICES" in full_text_upper or "LAMPIRAN" in full_text_upper

        skip_pagenum_check = (
            is_page_1_or_2
            or is_title_or_cover 
            or is_declaration_page
            or is_appendices_header  # 👈 DIPAKSA SKIP UNTUK MUKA SURAT PEMISAH APPENDICES
            or (in_appendix_section and abaikan_pagenum_appendix) 
            or is_other_exempted
        )

        # Muka Surat 3 ke atas (Acknowledgement dan seterusnya) WAJIB ada nombor muka surat
        if not skip_pagenum_check and not has_pagenum_found:
            # 1. Dapatkan label lokasi mengikut orientasi dan bahasa
            if is_landscape:
                loc_label = TEXT_I18N[lang_code]["loc_landscape"]
            else:
                loc_label = TEXT_I18N[lang_code]["loc_portrait"]

            # 2. Bina mesej amaran dinamik
            msg_missing_num = TEXT_I18N[lang_code]["missing_page_num"].format(location=loc_label)

            page_errors.append({
                "msg": msg_missing_num,
                "bbox": None,
            })

        # -----------------------------------------------------------------
        # 📌 SEMAKAN KHAS: ACKNOWLEDGEMENT (M/S ii & HAD 1 MUKA SURAT)
        # -----------------------------------------------------------------
        ack_kw = ["ACKNOWLEDGEMENT", "ACKNOWLEDGEMENTS", "PENGHARGAAN"]
        is_ack_page = any(kw in full_page_text.upper() for kw in ack_kw)

        if is_ack_page:
            # 1. Pastikan bernombor muka surat 'ii' (Romawi)
            has_ii_pagenum = "II" in full_page_text.upper().split() or has_pagenum_found
            if not has_ii_pagenum:
                # 1. Dapatkan mesej ralat dinamik (BM/EN)
                msg_ack = TEXT_I18N[lang_code]["ack_missing_ii"]

                page_errors.append({
                    "msg": msg_ack,
                    "bbox": None,
                })

            # 2. Amaran jika teks terlalu panjang (Garis panduan USM: Had 1 muka surat)
            word_count = len(full_page_text.split())
            if word_count > 450:  # Anggaran purata patah perkataan penuh 1 muka surat
                # 1. Dapatkan mesej ralat dinamik (BM/EN)
                msg_ack_limit = TEXT_I18N[lang_code]["ack_max_one_page"]

                page_errors.append({
                    "msg": msg_ack_limit,
                    "bbox": None,
                })

        # -----------------------------------------------------------------
        # 📌 SEMAKAN KHAS: TABLE OF CONTENTS (TOC)
        # -----------------------------------------------------------------
        toc_kw = ["TABLE OF CONTENTS", "KANDUNGAN"]
        is_toc_page = any(kw in full_page_text.upper() for kw in toc_kw)

        if is_toc_page:
            # 1. Semak penomboran muka surat bermula dengan 'iii' (Romawi)
            has_iii_pagenum = "III" in full_page_text.upper().split() or has_pagenum_found
            if not has_iii_pagenum and page_num == 3:  # Muka surat ke-4 dalam dokumen (indeks 3)
                msg_toc_iii = TEXT_I18N[lang_code]["toc_missing_iii"]
                page_errors.append({
                    "msg": msg_toc_iii,
                    "bbox": None,
                })

            # 2. Semak Format Hierarki Penomboran Sub-seksyen (Contoh: 1.2.1(a) atau 1.2.1(a)(i))
            invalid_sub_pattern = re.compile(r"\b\d+\.\d+\.\d+[a-z]\b")
            if invalid_sub_pattern.search(full_page_text):
                msg_toc_sub = TEXT_I18N[lang_code]["toc_invalid_sub"]
                page_errors.append({
                    "msg": msg_toc_sub,
                    "bbox": None,
                })

        # -----------------------------------------------------------------
        # 📌 SEMAKAN KHAS: ABSTRAK (BAHASA MALAYSIA) & ABSTRACT (ENGLISH)
        # -----------------------------------------------------------------
        is_bm_abstrak = "ABSTRAK" in full_page_text.upper() and "ABSTRACT" not in full_page_text.upper()
        is_en_abstract = "ABSTRACT" in full_page_text.upper()

        if is_bm_abstrak or is_en_abstract:
            # Label jenis abstrak
            abstrak_type = TEXT_I18N[lang_code]["abstract_bm_label"] if is_bm_abstrak else TEXT_I18N[lang_code]["abstract_en_label"]

            # 1. Semak Had Perkataan (Maksimum 400 perkataan)
            words = full_page_text.split()
            word_count = len(words)
            if word_count > 420:  # Toleransi 20 perkataan untuk tajuk
                msg_words = TEXT_I18N[lang_code]["abstract_max_words"].format(
                    type=abstrak_type, 
                    count=word_count
                )
                page_errors.append({
                    "msg": msg_words,
                    "bbox": None,
                })

            # 2. Semak Syarat Satu Perenggan (Single Paragraph Check)
            paragraphs = [p.strip() for p in full_page_text.split("\n\n") if len(p.strip()) > 50]
            if len(paragraphs) > 1:
                msg_single = TEXT_I18N[lang_code]["abstract_single_para"].format(type=abstrak_type)
                page_errors.append({
                    "msg": msg_single,
                    "bbox": None,
                })

            # 3. Semak Indentasi Baris Pertama (First Line Indented) - FIX
            is_real_abstract_page = (
                ("ABSTRAK" in full_page_text.upper() or "ABSTRACT" in full_page_text.upper())
                and not is_toc_page 
                and not is_ref_page
                and "HTTP" not in full_page_text.upper()  # Elak pautan web rujukan
            )

            if is_real_abstract_page:
                abstrak_header_seen = False
                first_para_line = None

                for block in blocks:
                    if "lines" in block:
                        for line in block["lines"]:
                            line_str = "".join([s["text"] for s in line["spans"]]).strip()
                            
                            # 1. Pastikan melepasi perkataan/tajuk "ABSTRAK" dahulu
                            if line_str.upper() in ["ABSTRAK", "ABSTRACT"]:
                                abstrak_header_seen = True
                                continue
                            
                            # 2. Ambil baris perenggan HANYA SELEPAS tajuk ABSTRAK ditemui
                            if abstrak_header_seen and len(line_str) > 30 and not line_str.startswith("http"):
                                first_para_line = line
                                break
                        if first_para_line:
                            break

                if first_para_line:
                    lx0 = first_para_line["bbox"][0]
                    # Indent mesti sekurang-kurangnya 10pt dari margin kiri
                    if lx0 < (cur_m_left + 10.0):
                        msg_indent = TEXT_I18N[lang_code]["abstract_indent"].format(type=abstrak_type)
                        page_errors.append({
                            "msg": msg_indent,
                            "bbox": first_para_line["bbox"],
                        })

        # =================================================================
        # 🔴 TAMPAL KOD REFERENCES & APPENDICES TEPAT DI SINI 🔴
        # =================================================================
        # -----------------------------------------------------------------
        # 📌 SEMAKAN KHAS: REFERENCES / RUJUKAN
        # -----------------------------------------------------------------
        is_ref_page = "REFERENCES" in full_page_text.upper() or "RUJUKAN" in full_page_text.upper()

        if is_ref_page and not is_toc_page:
            lines_y = []
            for b in blocks:
                if "lines" in b:
                    for l in b["lines"]:
                        lines_y.append(l["bbox"][1])

            if len(lines_y) > 2:
                gaps = [round(lines_y[i+1] - lines_y[i], 1) for i in range(len(lines_y)-1)]
                has_varying_gaps = any(g > 18.0 for g in gaps) and any(g <= 14.0 for g in gaps)
                if not has_varying_gaps and len(gaps) > 5:
                    # 1. Dapatkan mesej ralat dinamik (BM/EN)
                    msg_ref_spacing = TEXT_I18N[lang_code]["ref_spacing_issue"]

                    page_errors.append({
                        "msg": msg_ref_spacing,
                        "bbox": None,
                    })

        # -----------------------------------------------------------------
        # 📌 SEMAKAN KHAS: APPENDICES / LAMPIRAN (DIJAMIN KUNCI TOC)
        # -----------------------------------------------------------------
        # Kesan jika muka surat ini adalah bahagian Senarai Kandungan (TOC)
        is_toc_context = (
            is_toc_page 
            or "LIST OF PUBLICATIONS" in full_page_text.upper()
            or "TABLE OF CONTENTS" in full_page_text.upper()
            or "SENARAI KANDUNGAN" in full_page_text.upper()
        )

        # Jalankan semakan HANYA jika BUKAN dalam Senarai Kandungan
        if not is_toc_context:
            lines = [line.strip() for line in full_page_text.split("\n") if line.strip()]
            
            # 📌 Cari jika ada BARIS TAJUK yang bermula dengan APPENDIX / LAMPIRAN (Tajuk ringkas < 10 perkataan)
            appendix_heading_line = None
            for line in lines:
                if re.match(r'^(APPENDIX|LAMPIRAN)\b', line, re.IGNORECASE) and len(line.split()) < 10:
                    appendix_heading_line = line
                    break

            is_cover_appendix = len(full_page_text.strip().split()) <= 5 and "APPENDICES" in full_page_text.upper()

            # 1. Semak Muka Surat Pembatas 'APPENDICES'
            if is_cover_appendix and has_pagenum_found:
                msg_appendix_divider = TEXT_I18N[lang_code]["appendix_divider_pagenum"]
                page_errors.append({
                    "msg": msg_appendix_divider,
                    "bbox": None,
                })

            # 2. Semak Label Lampiran HANYA jika ia adalah BARIS TAJUK (Abaikan sebutan dalam perenggan)
            elif appendix_heading_line:
                has_valid_alphabet_label = bool(re.match(r'^(APPENDIX|LAMPIRAN)\s+[A-Z0-9]', appendix_heading_line, re.IGNORECASE))
                
                if not has_valid_alphabet_label:
                    msg_appendix_label = TEXT_I18N[lang_code]["appendix_invalid_label"]
                    page_errors.append({
                        "msg": msg_appendix_label,
                        "bbox": None,
                    })

        # PASS 2: SEMAKAN MARGIN & TEKS
        prev_line_text = ""  # 📌 Track baris sebelumnya untuk kesan line wrap

        for b in blocks:
            if "lines" in b:
                for line in b["lines"]:
                    full_line_text = "".join(
                        [s["text"] for s in line["spans"]]
                    ).strip()

                    if not full_line_text:
                        continue

                    # 📌 1. Semak adakah baris ini sambungan ayat dari baris atas
                    is_sentence_continuation = False
                    if prev_line_text:
                        clean_prev = prev_line_text.strip()
                        # Jika baris atas TIDAK diakhiri dengan [. : ; ! ?], maksudnya ayat perenggan belum habis!
                        if clean_prev and clean_prev[-1] not in [".", ":", ";", "!", "?"]:
                            is_sentence_continuation = True

                    # Simpan teks baris ini untuk semakan baris seterusnya
                    prev_line_text = full_line_text

                    clean_line_upper = full_line_text.strip().upper()

                    # -----------------------------------------------------------------
                    # 🔴 ABAIKAN SEMAKAN TAJUK DALAM TOC & REFERENCES
                    # -----------------------------------------------------------------
                    is_toc_entry = bool(DOT_LEADER_REGEX.search(full_line_text))
                    is_current_toc_page = is_toc_page or "TABLE OF CONTENTS" in full_page_text.upper() or "KANDUNGAN" in full_page_text.upper()
                    is_current_ref_page = is_ref_page or "REFERENCES" in full_page_text.upper() or "RUJUKAN" in full_page_text.upper()

                    TARGET_SECTION_TITLES = [
                        "TITLE PAGE", "DECLARATION", "DECLARATION PAGE", "PENGAKUAN", "HALAMAN PENGAKUAN",
                        "ACKNOWLEDGEMENTS", "ACKNOWLEDGEMENT", "PENGHARGAAN", "TABLE OF CONTENTS", "KANDUNGAN", 
                        "LIST OF TABLES", "SENARAI JADUAL", "LIST OF FIGURES", "SENARAI RAJAH", 
                        "LIST OF PLATES", "SENARAI PLAT", "LIST OF SYMBOLS", "SENARAI SIMBOL",
                        "LIST OF ABBREVIATIONS", "SENARAI SINGKATAN", "ABSTRAK", "ABSTRACT", 
                        "REFERENCES", "APPENDIX", "LAMPIRAN"
                    ]

                    if is_current_toc_page or is_current_ref_page or is_toc_entry:
                        is_chapter_title = False
                        is_prelim_title = False
                    else:
                        is_chapter_title = (
                            bool(re.match(r"^(CHAPTER|BAB)\s+\d+", clean_line_upper)) 
                            and not is_list_page
                        )
                        is_prelim_title = clean_line_upper in TARGET_SECTION_TITLES

                    # -----------------------------------------------------------------
                    # 📌 SEMAKAN TAJUK BAB / SEKSYEN (DENGAN PENAPIS OUTLINE & FORMAT)
                    # -----------------------------------------------------------------
                    h_x0, h_y0, h_x1, h_y1 = line["bbox"]

                    # 1. Tapis ayat perenggan biasa
                    is_narrative_sentence = (
                        bool(VERB_KEYWORDS_REGEX.search(full_line_text))
                        or full_line_text.strip().endswith(".")
                        or len(full_line_text.split()) > 8
                    )

                    # 2. 📌 SYARAT BAHARU: Tapis format ringkasan outline (ada titik bertindih ':' atau bukan ALL CAPS)
                    # Example outline: "Chapter 3: Research Methodology" -> Diabaikan
                    has_colon_after_chapter = bool(re.search(r"^(chapter|bab)\s+\d+\s*:", full_line_text, re.IGNORECASE))
                    is_not_uppercase = not full_line_text.strip().isupper()

                    # 3. Tajuk Bab Utama SEBENAR mesti berada di bahagian atas M/S (y0 < 200 pt)
                    is_top_of_page = h_y0 < 200.0

                    # Gabungkan semua syarat penafian outline
                    is_valid_main_chapter = (
                        (is_chapter_title or is_prelim_title)
                        and is_top_of_page
                        and not is_narrative_sentence
                        and not has_colon_after_chapter
                        and not is_not_uppercase
                    )

                    if is_valid_main_chapter:
                        first_span = line["spans"][0]
                        heading_font = first_span["font"].lower()
                        heading_size = round(first_span["size"], 1)
                        text_snippet = full_line_text[:30]

                        # 1. Semak Bold
                        is_bold = "bold" in heading_font or "black" in heading_font
                        if not is_bold:
                            msg_bold = TEXT_I18N[lang_code]["chapter_heading_not_bold"].format(text=text_snippet)
                            page_errors.append({
                                "msg": msg_bold,
                                "bbox": line["bbox"],
                            })

                        # 2. Semak Jajaran Tengah (Centered)
                        line_center_x = (h_x0 + h_x1) / 2
                        printable_center_x = (cur_m_left + cur_m_right) / 2
                        TOLERANCE_PT = 20.0
                        
                        if abs(line_center_x - printable_center_x) > TOLERANCE_PT:
                            msg_center = TEXT_I18N[lang_code]["chapter_heading_not_centered"].format(text=text_snippet)
                            page_errors.append({
                                "msg": msg_center,
                                "bbox": line["bbox"],
                            })

                        # 3. Semak Single Spacing
                        line_height = h_y1 - h_y0
                        if heading_size > 0 and (line_height / heading_size) > 1.4:
                            msg_spacing = TEXT_I18N[lang_code]["chapter_heading_not_single_spaced"].format(text=text_snippet)
                            page_errors.append({
                                "msg": msg_spacing,
                                "bbox": line["bbox"],
                            })

                    # =================================================================
                    # 💥 TAMPAL KOD BAHARU DI SINI (GELUNG SEMAKAN FONT & SAIZ TEKS)
                    # =================================================================
                    for span in line["spans"]:
                        text = span["text"].strip()
                        size = round(span["size"], 1)
                        font_name = span["font"]
                        bbox = span["bbox"]

                        if not text:
                            continue

                        x0, y0, x1, y1 = bbox

                        # 📌 SEMAKAN JENIS & SAIZ FONT
                        skip_font_check = in_appendix_section or (abaikan_appendix and is_appendix_page)

                        if not skip_font_check:
                            font_name_clean = font_name.lower().replace(" ", "")
                            
                            # 1. Tapis simbol matematik
                            is_math_font = any(
                                mf in font_name_clean for mf in MATH_SYMBOL_FONTS
                            )

                            # 2. Tapis teks dalam gambar
                            is_inside_image = False
                            if abaikan_teks_dalam_gambar and images_info:
                                text_center_x = (x0 + x1) / 2
                                text_center_y = (y0 + y1) / 2
                                for img in images_info:
                                    img_bbox = img["bbox"]
                                    if (img_bbox[0] <= text_center_x <= img_bbox[2]) and \
                                       (img_bbox[1] <= text_center_y <= img_bbox[3]):
                                        is_inside_image = True
                                        break

                            # 3. Semakan Pengesanan Font Tidak Sah (Cambria dll.)
                            if not is_math_font and not is_inside_image:
                                font_matched = any(
                                    f.lower().replace(" ", "") in font_name_clean for f in allowed_fonts
                                )

                                clean_word_len = len(re.sub(r'[^a-zA-Z0-9]', '', text))

                                # Kesan font tidak dibenarkan jika aksara >= 2
                                if not font_matched and clean_word_len >= 2:
                                    # 1. Potong teks pendek untuk paparan
                                    text_snippet = text[:25]
                                    
                                    # 2. Jana mesej ralat dinamik (BM/EN)
                                    msg_font = TEXT_I18N[lang_code]["font_issue"].format(
                                        font_name=font_name, 
                                        text=text_snippet
                                    )

                                    page_errors.append({
                                        "msg": msg_font,
                                        "bbox": bbox,
                                    })

                                # Semakan saiz font
                                if clean_word_len >= 3:
                                    snippet = text[:25]
                                    
                                    # 1. Semakan Saiz Terlalu Kecil
                                    if size < 7.5:
                                        msg_small = TEXT_I18N[lang_code]["font_size_too_small"].format(
                                            size=size, 
                                            text=snippet
                                        )
                                        page_errors.append({
                                            "msg": msg_small,
                                            "bbox": bbox,
                                        })
                                        
                                    # 2. Semakan Saiz Tidak Piawai
                                    elif 12.8 < size < 17.5 and not (is_chapter_title or is_prelim_title):
                                        msg_non_standard = TEXT_I18N[lang_code]["font_size_non_standard"].format(
                                            size=size, 
                                            text=snippet
                                        )
                                        page_errors.append({
                                            "msg": msg_non_standard,
                                            "bbox": bbox,
                                        })

                    # -----------------------------------------------------------------
                    # 📌 SEMAKAN TAJUK JADUAL & RAJAH (STRICT CAPTION CHECK)
                    # -----------------------------------------------------------------
                    if semak_caption and not is_list_page and not is_sentence_continuation:
                        
                        # 1. Tapis Ayat Perenggan yang mengandungi Kata Kerja (Action Verbs)
                        NARRATIVE_VERB_REGEX = r"^\s*(Table|Jadual|Figure|Rajah)\s+\d+[\d\.\-a-zA-Z\(\)]*\s+(presents|shows|summarizes|illustrates|depicts|indicates|displays|lists|gives|compares|provides|highlights|demonstrates|contains|was|is|were|are|can|should|will|includes|exhibits|reveals|outlines|according|refers|described|seen|shown)\b"
                        is_narrative_sentence = bool(re.search(NARRATIVE_VERB_REGEX, full_line_text, re.IGNORECASE))

                        # 2. Semak jika baris ini hanyalah rujukan ayat biasa
                        is_dot_leader_line = bool(DOT_LEADER_REGEX.search(full_line_text)) if 'DOT_LEADER_REGEX' in globals() else False
                        is_in_text_citation = bool(IN_TEXT_CITATION_REGEX.match(full_line_text)) if 'IN_TEXT_CITATION_REGEX' in globals() else False

                        is_table_caption_start = bool(re.match(r"^\s*(Table|Jadual)\s+\d+(\.\d+)*", full_line_text, re.IGNORECASE))
                        is_figure_caption_start = bool(re.match(r"^\s*(Figure|Rajah)\s+\d+(\.\d+)*", full_line_text, re.IGNORECASE))

                        # HANYA semak jika BUKAN ayat perenggan (is_narrative_sentence == False)
                        if not (is_narrative_sentence or is_dot_leader_line or is_current_toc_page or is_current_ref_page):
                            line_y0, line_y1 = line["bbox"][1], line["bbox"][3]

                            # A. TAJUK JADUAL (TABLE) - Mesti di ATAS Jadual
                            if is_table_caption_start and not is_in_text_citation:
                                has_structure_below = False
                                for d in drawings:
                                    d_y0 = d["rect"][1]
                                    if 0 < (d_y0 - line_y1) < 80:
                                        has_structure_below = True
                                        break

                                if not has_structure_below:
                                    msg_tbl_pos = TEXT_I18N[lang_code]["table_caption_position_error"].format(text=full_line_text[:35])
                                    page_errors.append({
                                        "msg": msg_tbl_pos,
                                        "bbox": line["bbox"],
                                    })

                                clean_title_text = full_line_text.strip()
                                if re.match(r"^(Table|Jadual)\s+\d+(\.\d+)*\.?$", clean_title_text, re.IGNORECASE):
                                    msg_tbl_split = TEXT_I18N[lang_code]["table_caption_split_format"].format(text=clean_title_text)
                                    page_errors.append({
                                        "msg": msg_tbl_split,
                                        "bbox": line["bbox"],
                                    })

                            # B. TAJUK RAJAH (FIGURE) - Mesti di BAWAH Rajah
                            elif is_figure_caption_start and not is_in_text_citation:
                                image_above_close = False
                                image_below_close = False

                                if images_info:
                                    for img in images_info:
                                        img_y0, img_y1 = img["bbox"][1], img["bbox"][3]
                                        if 0 < (line_y0 - img_y1) < 60:
                                            image_above_close = True
                                        if 0 < (img_y0 - line_y1) < 40:
                                            image_below_close = True

                                if image_below_close and not image_above_close:
                                    msg_fig_pos = TEXT_I18N[lang_code]["figure_caption_position_error"].format(text=full_line_text[:35])
                                    page_errors.append({
                                        "msg": msg_fig_pos,
                                        "bbox": line["bbox"],
                                    })

        # =========================================================================
        # BAHAGIAN 3/3: SEMAKAN NOMBOR MUKA SURAT & ANTARAMUKA USER (UI STREAMLIT)
        # =========================================================================
        # -----------------------------------------------------------------
        # SEMAKAN KEHADIRAN NOMBOR MUKA SURAT
        # -----------------------------------------------------------------
        if not in_appendix_section:
            lines = [line.strip().upper() for line in full_page_text.split("\n") if line.strip()]
            for line in lines:
                if (line.startswith("APPENDIX") or line.startswith("LAMPIRAN")) and len(line) < 60:
                    in_appendix_section = True
                    break

        is_other_exempted = any(
            k in page_text_lower for k in ["list of publications", "publication", "penerbitan"]
        )

        # -----------------------------------------------------------------
        # SEMAKAN KHAS NOMBOR MUKA SURAT PRELIMINARIES (USM)
        # Syarat: Title Page (m/s 1) & Declaration (m/s 2) TIDAK BOLEH dipaparkan nombor m/s.
        # -----------------------------------------------------------------
        declaration_keywords = [
            "DECLARATION", "DECLARATION PAGE", "PENGAKUAN", "HALAMAN PENGAKUAN",
            "I HEREBY DECLARE THAT", "SAYA DENGAN INI MENGAKU BAHAWA"
        ]
        is_declaration_page = any(
            kw in full_page_text.upper() for kw in declaration_keywords
        )

        # 1. Semak ralat jika nombor M/S terpapar pada Title Page (m/s 1)
        if page_num == 0 and has_pagenum_found:
            msg_title_forbidden = TEXT_I18N[lang_code]["title_page_pagenum_forbidden"]
            page_errors.append({
                "msg": msg_title_forbidden,
                "bbox": None,
            })

        # 2. Semak ralat jika nombor M/S terpapar pada Declaration Page (m/s 2)
        if (is_declaration_page or page_num == 1) and has_pagenum_found:
            msg_decl_forbidden = TEXT_I18N[lang_code]["declaration_pagenum_forbidden"]
            page_errors.append({
                "msg": msg_decl_forbidden,
                "bbox": None,
            })

        # -----------------------------------------------------------------
        # SEMAKAN KEHADIRAN NOMBOR MUKA SURAT (MUKA SURAT 3 DAN KE ATAS)
        # -----------------------------------------------------------------
        if not in_appendix_section:
            lines = [line.strip().upper() for line in full_page_text.split("\n") if line.strip()]
            for line in lines:
                if (line.startswith("APPENDIX") or line.startswith("LAMPIRAN")) and len(line) < 60:
                    in_appendix_section = True
                    break

        is_other_exempted = any(
            k in page_text_lower for k in ["list of publications", "publication", "penerbitan"]
        )

        # Halaman 1 (Title) dan Halaman 2 (Declaration) dikecualikan daripada amaran tiada nombor
        skip_pagenum_check = (
            page_num < 2 
            or (in_appendix_section and abaikan_pagenum_appendix) 
            or is_other_exempted
        )

        if not skip_pagenum_check and not has_pagenum_found:
            # 1. Dapatkan label lokasi mengikut orientasi dan bahasa
            loc_label = (
                TEXT_I18N[lang_code]["loc_landscape"] 
                if is_landscape 
                else TEXT_I18N[lang_code]["loc_portrait"]
            )

            # 2. Bina mesej ralat dinamik
            msg_missing_num = TEXT_I18N[lang_code]["missing_page_num"].format(location=loc_label)

            page_errors.append({
                "msg": msg_missing_num,
                "bbox": None,
            })

        # Nyah-duplikasi ralat mengikut mesej (message deduplication)
        unique_page_errors = []
        seen_msgs = set()
        for e in page_errors:
            if e["msg"] not in seen_msgs:
                seen_msgs.add(e["msg"])
                unique_page_errors.append(e)

        # Simpan ralat mengikut muka surat
        all_pages_errors_list.append(unique_page_errors)

        # Kumpul ralat aktif untuk laporan (Saring yang tidak di-ignore/bypass)
        for i, err in enumerate(unique_page_errors):
            err_id = f"p{page_num+1}_{i}"
            if err_id not in st.session_state.ignored_errors:
                detected_issues.append({"page": page_num + 1, "msg": err["msg"], "bbox": err.get("bbox")})


    # =========================================================================
    # 📄 SEKSYEN JANA & MUAT TURUN DOKUMEN
    # =========================================================================
    st.markdown("---")
    st.subheader("📄 Jana & Muat Turun Dokumen Akhir")

    st.write(
        f"Jumlah isu aktif yang disahkan untuk dilaporkan: **{len(detected_issues)} isu**"
    )

    if st.button(
        "⚙️ Jana Dokumen PDF Akhir",
        type="primary",
        use_container_width=True,
    ):
        with st.spinner("Menjana fail PDF Gabungan (Visual + Laporan)... Sila tunggu sebentar."):
            # 1. Jana PDF berkotak merah ralat
            annotated_pdf_bytes = generate_annotated_thesis(
                doc, all_pages_errors_list, st.session_state.ignored_errors
            )
            
            # 2. Hantar ke fungsi gabungan beserta nilai margin
            st.session_state.combined_pdf_bytes = generate_combined_visual_report(
                annotated_pdf_bytes, 
                all_pages_errors_list, 
                st.session_state.ignored_errors,
                margin_left_mm=margin_left_mm,
                margin_right_mm=margin_right_mm,
                margin_top_mm=margin_top_mm,
                margin_bottom_mm=margin_bottom_mm
            )

        st.success("Fail PDF Gabungan telah sedia untuk dimuat turun!")

    # =========================================================================
    # 📥 BUTANG MUAT TURUN PDF GABUNGAN
    # =========================================================================
    if st.session_state.get("combined_pdf_bytes") is not None:
        st.write("")  # Ruang kosong pemisah

        # 📌 Bina nama fail dinamik mengambil nama asal fail PDF
        file_name_out = f"Laporan_Gabungan_{uploaded_file.name}" if uploaded_file else "Laporan_Gabungan_Visual_Tesis_USM.pdf"

        # Gunakan nama fail dinamik dalam fungsi HTML download button
        btn_html_combined = create_download_button_html(
            st.session_state.combined_pdf_bytes,
            file_name_out,
            "📥 Muat Turun Laporan PDF Gabungan (Visual Kiri + Isu Kanan)",
            color="#059669",  # Warna Hijau Tema
        )
        st.markdown(btn_html_combined, unsafe_allow_html=True)

    # =========================================================================
    # 🔍 PRATONTON VISUAL PER MUKA SURAT (KOD BERSIH TANPA DUPLIKASI)
    # =========================================================================
    st.markdown("---")
    st.subheader(TEXT_I18N[lang_code]["ui_review_preview_title"])

    for page_num in range(len(doc)):
        unique_page_errors = all_pages_errors_list[page_num]
        is_landscape = doc[page_num].rect.width > doc[page_num].rect.height
        tag_landscape = " [Landscape]" if is_landscape else ""

        # 1. Kira bilangan isu yang belum di-bypass
        active_errors_count = sum(
            1 for i, _ in enumerate(unique_page_errors)
            if f"p{page_num+1}_{i}" not in st.session_state.ignored_errors
        )

        # 2. Set status label mengikut jumlah isu aktif (Dinamik)
        if active_errors_count > 0:
            status_str = TEXT_I18N[lang_code]["ui_issues_found"].format(count=active_errors_count)
        else:
            status_str = TEXT_I18N[lang_code]["ui_status_ok"]

        # 3. Label Expander Dinamik
        expander_title = TEXT_I18N[lang_code]["ui_page_label"].format(
            num=page_num + 1,
            tag=tag_landscape,
            status=status_str
        )

        with st.expander(expander_title):
            col_img, col_details = st.columns([1, 1])
            doc_page = doc[page_num]

            # Lukis kotak merah ralat
            for i, err in enumerate(unique_page_errors):
                err_id = f"p{page_num+1}_{i}"
                if (
                    err.get("bbox")
                    and err_id not in st.session_state.ignored_errors
                ):
                    doc_page.draw_rect(
                        err["bbox"], color=(1, 0, 0), width=1.5
                    )

            pix = doc_page.get_pixmap(dpi=120)
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

            # Kolum Kiri: Pratonton Gambar (Dengan Garisan Margin Samar)
            with col_img:
                img_with_guides = add_margin_overlay(doc_page, dpi=120, is_landscape=is_landscape)
                
                preview_caption = TEXT_I18N[lang_code]["ui_preview_caption"].format(num=page_num + 1)
                
                st.image(
                    img_with_guides,
                    caption=preview_caption,
                    use_container_width=True,
                )

            # Kolum Kanan: Senarai Isu & Master Checkbox
            with col_details:
                if not unique_page_errors:
                    st.success(TEXT_I18N[lang_code]["ui_no_errors_page"])
                else:
                    st.write(TEXT_I18N[lang_code]["ui_detected_issues_title"])

                    page_err_ids = []
                    for i, err in enumerate(unique_page_errors):
                        err_id = f"p{page_num+1}_{i}"
                        page_err_ids.append(err_id)
                        is_ignored = err_id in st.session_state.ignored_errors

                        # 🟢 SUSUN SEBELAH-MENYEBELAH (RAPAT & KEMAS)
                        c_check, c_text = st.columns([0.25, 0.75])
                        
                        with c_check:
                            st.checkbox(
                                TEXT_I18N[lang_code]["ui_bypass_issue"].format(num=i+1),
                                key=f"cb_{err_id}",
                                value=is_ignored,
                                on_change=toggle_bypass,
                                args=(err_id,),
                            )

                        with c_text:
                            # text_input yang read-only: Boleh select, copy, dan jarak sangat rapat
                            st.text_input(
                                TEXT_I18N[lang_code]["ui_issue_label"].format(num=i+1),
                                value=err['msg'],
                                key=f"txt_{err_id}",
                                label_visibility="collapsed",
                                disabled=True
                            )

                    st.divider()

                    all_bypassed = all(
                        eid in st.session_state.ignored_errors for eid in page_err_ids
                    )

                    def toggle_bypass_all_page(err_ids, p_num):
                        # 📌 1. Perisai KeyError: Guna .get() dengan nilai lalai False
                        key = f"cb_all_p{p_num+1}"
                        is_all_checked = st.session_state.get(key, False)

                        # 📌 2. Perisai AttributeError: Auto-create jika hilang lepas clear cache
                        if "ignored_errors" not in st.session_state:
                            st.session_state.ignored_errors = set()

                        # Kemaskini status bypass untuk semua isu dalam muka surat ini
                        for eid in err_ids:
                            if is_all_checked:
                                st.session_state.ignored_errors.add(eid)
                                st.session_state[f"cb_{eid}"] = True
                            else:
                                st.session_state.ignored_errors.discard(eid)
                                st.session_state[f"cb_{eid}"] = False

                        # 📌 3. Reset cache laporan supaya PDF baharu dijana
                        st.session_state.report_pdf_bytes = None
                        st.session_state.annotated_pdf_bytes = None

                    # Widget Checkbox UI
                    st.checkbox(
                        TEXT_I18N[lang_code]["ui_bypass_all_page"],
                        key=f"cb_all_p{page_num+1}",
                        value=all_bypassed,
                        on_change=toggle_bypass_all_page,
                        args=(page_err_ids, page_num),
                    )

    # ==================== BUTANG KEMBALI KE ATAS ====================
    st.markdown("---")
    components.html(
        """
        <div style="text-align: center; font-family: sans-serif;">
            <button id="scrollToTopBtn" style="
                padding: 10px 24px;
                background-color: #ffffff;
                color: #31333F;
                border: 1px solid #d4d6db;
                border-radius: 8px;
                font-weight: 600;
                cursor: pointer;
                box-shadow: 0px 2px 4px rgba(0,0,0,0.05);
                transition: all 0.2s ease;
            ">
                ⬆️ Kembali ke Atas
            </button>
        </div>

        <script>
        const btn = document.getElementById('scrollToTopBtn');
        btn.addEventListener('click', function() {
            const mainDoc = window.parent.document;
            const mainContainer = mainDoc.querySelector('[data-testid="stMain"]') 
                                || mainDoc.querySelector('.main') 
                                || window.parent;
            
            mainContainer.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
        </script>
        """,
        height=70
    )

paparkan_footer()
