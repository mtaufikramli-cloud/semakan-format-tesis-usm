import base64
import io
import re
from fpdf import FPDF
from PIL import Image
import pymupdf as fitz
import streamlit as st
import streamlit.components.v1 as components

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
        html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
            scroll-behavior: smooth !important;
        }
    </style>
    <div id="top-anchor"></div>
""", unsafe_allow_html=True)

PASSWORD_RAHSIA = "USM2026"
APP_VERSION = "v1.2.0"

# Papar versi dan butang info di Sidebar
col_v1, col_v2 = st.sidebar.columns([3, 1])

with col_v1:
    st.caption(f"📌**Versi Sistem:** {APP_VERSION}")

with col_v2:
    with st.popover("ℹ️ Info"):
        st.markdown(f"### 📋 Log Kemaskini ({APP_VERSION})")
        st.markdown("""
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
    st.markdown("<div id='top-of-page'></div>", unsafe_allow_html=True)
    st.title("📄 Semakan Format Tesis USM")
    st.caption(f"📌 **Versi Sistem:** {APP_VERSION}")
    st.markdown("---")

    col_login, _ = st.columns([1.5, 1])
    with col_login:
        with st.form("login_form"):
            st.subheader("🔒 Log Masuk Akses")
            password_input = st.text_input(
                "Masukkan Kata Laluan Akses:", type="password"
            )
            submit_button = st.form_submit_button(
                "🔑 Log Masuk", use_container_width=True
            )

            if submit_button:
                if password_input == PASSWORD_RAHSIA:
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.error("🔑 Kata laluan salah. Sila cuba lagi!")

    st.markdown("---")
    st.warning("""
    ### ⚠️ Penafian (Disclaimer) & Panduan Penggunaan
    1. **Sistem Bantu Semak Otomatik:** Aplikasi ini dibangunkan sebagai **alat bantuan awal** untuk mengesan ralat format utama.
    2. **Kelulusan Rasmi:** Keputusan semakan aplikasi ini **bukan penentu mutlak**. Pengguna bertanggungjawab merujuk *Garis Panduan Penulisan Tesis USM* rasmi.
    3. **Kerahsiaan Fail:** Fail PDF diproses secara *in-memory* dan **tidak disimpan secara kekal**.
    """)

    # ==================== FOOTER HAK CIPTA ====================
    st.markdown("---")
    st.markdown(
        """
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
        """,
        unsafe_allow_html=True
    )

    st.stop()

# ==================== SIDEBAR & TETAPAN ====================
with st.sidebar:
    # st.caption(f"📌 **Versi:** {APP_VERSION}")
    if st.button("🚪 Log Out", type="secondary", use_container_width=True):
        logout()
    st.markdown("---")
    st.header("⚙️ Tetapan Templat Tesis")

    default_left, default_right, default_top, default_bottom = 40.0, 25.0, 25.0, 25.0
    default_fonts = ["Times New Roman", "TimesNewRoman", "Arial", "Calibri", "Garamond"]

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
            "Calibri",
            "Garamond",
        ]
    else:
        default_left, default_right, default_top, default_bottom = 38.0, 25.0, 25.0, 25.0
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
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "Laporan Semakan Format Tesis", new_x="LMARGIN", new_y="NEXT", align="C")
    
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 6, f"Jumlah Muka Surat Diperiksa: {total_pages}", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(5)

    if not filtered_errors:
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 10, "Tiada isu format dikesan. Tesis mematuhi piawaian!", new_x="LMARGIN", new_y="NEXT")
    else:
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(30, 8, "Muka Surat", border=1, align="C")
        pdf.cell(160, 8, "Butiran Isu Format", border=1, align="C", new_x="LMARGIN", new_y="NEXT")

        pdf.set_font("Helvetica", "", 9)
        for item in filtered_errors:
            page_str = f"MS {item['page']}"
            # Gantikan aksara tak disokong untuk elak FPDF encoding crash
            issue_str = item["msg"].replace("*", "").encode('latin-1', 'replace').decode('latin-1')
            
            # Gunakan multi_cell untuk elak teks terpotong
            x_start = pdf.get_x()
            y_start = pdf.get_y()
            pdf.cell(30, 8, page_str, border=1, align="C")
            pdf.set_xy(x_start + 30, y_start)
            pdf.multi_cell(160, 8, issue_str, border=1)

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


st.title("📄 Sistem Semakan Format Tesis (USM Standard)")
uploaded_file = st.file_uploader("Muat Naik Fail PDF Tesis", type=["pdf"])

if uploaded_file is not None:
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    st.success(f"Fail berjaya dimuat naik! Jumlah muka surat: {len(doc)}")

    if "ignored_errors" not in st.session_state:
        st.session_state.ignored_errors = set()
    if "report_pdf_bytes" not in st.session_state:
        st.session_state.report_pdf_bytes = None
    if "annotated_pdf_bytes" not in st.session_state:
        st.session_state.annotated_pdf_bytes = None

    def toggle_bypass(err_id):
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

        is_landscape = rect.width > rect.height
        page_errors = []

        if is_landscape:
            cur_m_top = MARGIN_LEFT_PT
            cur_m_bottom = rect.height - MARGIN_RIGHT_PT
            cur_m_left = MARGIN_TOP_PT
            cur_m_right = rect.width - MARGIN_BOTTOM_PT
        else:
            cur_m_top = MARGIN_TOP_PT
            cur_m_bottom = rect.height - MARGIN_BOTTOM_PT
            cur_m_left = MARGIN_LEFT_PT
            cur_m_right = rect.width - MARGIN_RIGHT_PT

        # PASS 1: PRE-SCANNING NOMBOR MUKA SURAT
        pagenum_bboxes = []
        has_pagenum_found = False

        words = page.get_text("words")
        for w in words:
            wx0, wy0, wx1, wy1, word_str = w[0], w[1], w[2], w[3], w[4]
            clean_w = re.sub(r"[^a-zA-Z0-9]", "", word_str.lower())

            is_valid_num = clean_w.isdigit() or is_roman_numeral(clean_w)

            if is_valid_num:
                if is_landscape:
                    if wx0 < 150 or wy0 < 120 or wy0 > (rect.height - 120):
                        has_pagenum_found = True
                        pagenum_bboxes.append((wx0, wy0, wx1, wy1))
                else:
                    if wy0 > (rect.height - 120):
                        has_pagenum_found = True
                        pagenum_bboxes.append((wx0, wy0, wx1, wy1))

        # -----------------------------------------------------------------
        # 📌 PEMURNIAN PINTAR: DETEKSI JENIS MUKA SURAT BERDASARKAN KANDUNGAN
        # -----------------------------------------------------------------
        is_page_1_or_2 = page_num in [0, 1]
        
        # Pengesanan Muka Surat Cover / Title Page (Mestilah berada di Page 1 atau 2 SAHAJA)
        has_usm_keyword = "UNIVERSITI SAINS MALAYSIA" in full_page_text.upper()
        has_fulfilment = ("THESIS SUBMITTED IN FULFILMENT" in full_page_text.upper() or 
                          "TESIS DISERAHKAN BAGI MEMENUHI" in full_page_text.upper())
        
        # HANYA anggap Title/Cover Page JIKA ia berada di Page 1 atau Page 2
        is_title_or_cover = is_page_1_or_2 and (has_usm_keyword or has_fulfilment)

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
                page_errors.append({
                    "msg": "Title Page (M/S 1-2): Bulan dan Tahun hantaran (Month and Year) tidak dikesan.",
                    "bbox": None,
                })

        # -----------------------------------------------------------------
        # 3. SYARAT PENGEQUALIAN & SEMAKAN UNTUK PAGE BIASA (PAGE 3+)
        # -----------------------------------------------------------------
        page_text_lower = full_page_text.lower()
        is_other_exempted = any(
            k in page_text_lower for k in ["list of publications", "publication", "penerbitan"]
        )

        skip_pagenum_check = (
            is_page_1_or_2
            or is_title_or_cover 
            or is_declaration_page
            or (in_appendix_section and abaikan_pagenum_appendix) 
            or is_other_exempted
        )

        # Muka Surat 3 ke atas (Acknowledgement dan seterusnya) WAJIB ada nombor muka surat
        if not skip_pagenum_check and not has_pagenum_found:
            loc_label = "sebelah kiri/atas" if is_landscape else "bahagian bawah tengah"
            page_errors.append({
                "msg": f"Nombor muka surat tidak dikesan di {loc_label}.",
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
                page_errors.append({
                    "msg": "Acknowledgement / Penghargaan: Muka surat ini wajib diletakkan nombor muka surat 'ii'.",
                    "bbox": None,
                })

            # 2. Amaran jika teks terlalu panjang (Garis panduan USM: Had 1 muka surat)
            word_count = len(full_page_text.split())
            if word_count > 450:  # Anggaran purata patah perkataan penuh 1 muka surat
                page_errors.append({
                    "msg": "Acknowledgement / Penghargaan: Dihadkan kepada 1 muka surat sahaja.",
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
                page_errors.append({
                    "msg": "Table of Contents: Muka surat awal TOC wajib bermula dengan nombor muka surat 'iii'.",
                    "bbox": None,
                })

            # 2. Semak Format Hierarki Penomboran Sub-seksyen (Contoh: 1.2.1(a) atau 1.2.1(a)(i))
            invalid_sub_pattern = re.compile(r"\b\d+\.\d+\.\d+[a-z]\b")
            if invalid_sub_pattern.search(full_page_text):
                page_errors.append({
                    "msg": "Table of Contents: Sub-pembahagian tajuk mestilah menggunakan kurungan, contoh: 1.2.1(a) atau 1.2.1(a)(i).",
                    "bbox": None,
                })

        # -----------------------------------------------------------------
        # 📌 SEMAKAN KHAS: ABSTRAK (BAHASA MALAYSIA) & ABSTRACT (ENGLISH)
        # -----------------------------------------------------------------
        is_bm_abstrak = "ABSTRAK" in full_page_text.upper() and "ABSTRACT" not in full_page_text.upper()
        is_en_abstract = "ABSTRACT" in full_page_text.upper()

        if is_bm_abstrak or is_en_abstract:
            abstrak_type = "ABSTRAK (BM)" if is_bm_abstrak else "ABSTRACT (EN)"

            # 1. Semak Had Perkataan (Maksimum 400 perkataan)
            words = full_page_text.split()
            word_count = len(words)
            if word_count > 420:  # Toleransi 20 perkataan untuk tajuk
                page_errors.append({
                    "msg": f"{abstrak_type}: Panjang teks melebihi had 400 perkataan ({word_count} perkataan dikesan).",
                    "bbox": None,
                })

            # 2. Semak Syarat Satu Perenggan (Single Paragraph Check)
            paragraphs = [p.strip() for p in full_page_text.split("\n\n") if len(p.strip()) > 50]
            if len(paragraphs) > 1:
                page_errors.append({
                    "msg": f"{abstrak_type}: Teks hendaklah ditulis dalam SATU PERENGGAN sahaja.",
                    "bbox": None,
                })

            # 3. Semak Indentasi Baris Pertama (First Line Indented)
            # 🔴 PENAMBAHAN: Pastikan betul-betul muka surat Abstrak (Bukan TOC / References / URL)
            is_real_abstract_page = (
                ("ABSTRAK" in full_page_text.upper() or "ABSTRACT" in full_page_text.upper())
                and not is_toc_page 
                and not is_ref_page
                and "HTTP" not in full_page_text.upper()  # Elak pautan web rujukan
            )

            if is_real_abstract_page:
                first_text_line = None
                for block in blocks:
                    if "lines" in block:
                        for line in block["lines"]:
                            line_str = "".join([s["text"] for s in line["spans"]]).strip()
                            
                            # Abai garisan tajuk, garisan pendek, dan entri senarai
                            if (
                                len(line_str) > 30 
                                and "ABSTRAK" not in line_str.upper() 
                                and "ABSTRACT" not in line_str.upper()
                                and not line_str.startswith("http")
                            ):
                                first_text_line = line
                                break
                    if first_text_line:
                        break

                if first_text_line:
                    lx0 = first_text_line["bbox"][0]
                    if lx0 < (cur_m_left + 10.0):
                        page_errors.append({
                            "msg": f"{abstrak_type}: Baris pertama perenggan hendaklah di-indent (indented).",
                            "bbox": first_text_line["bbox"],
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
                    page_errors.append({
                        "msg": "References: Mesti menggunakan Single-spacing dalam entri dan Double-spacing antara entri rujukan.",
                        "bbox": None,
                    })

        # -----------------------------------------------------------------
        # 📌 SEMAKAN KHAS: APPENDICES / LAMPIRAN
        # -----------------------------------------------------------------
        is_appendix_page = any(k in full_page_text.upper() for k in ["APPENDICES", "APPENDIX", "LAMPIRAN"])

        if is_appendix_page and not is_toc_page:
            is_cover_appendix = len(full_page_text.strip().split()) <= 5 and "APPENDICES" in full_page_text.upper()
            
            if is_cover_appendix and has_pagenum_found:
                page_errors.append({
                    "msg": "Appendices: Muka surat pembatas 'APPENDICES' TIDAK BOLEH diletakkan nombor muka surat.",
                    "bbox": None,
                })

            has_valid_alphabet_label = bool(re.search(r"\b(APPENDIX|LAMPIRAN)\s+[A-Z]\b", full_page_text.upper()))
            if not is_cover_appendix and not has_valid_alphabet_label:
                page_errors.append({
                    "msg": "Appendices: Lampiran mestilah dilabel mengikut abjad (contoh: Appendix A, Appendix B).",
                    "bbox": None,
                })

        # -----------------------------------------------------------------
        # 📌 3. SYARAT PENGEQUALIAN & SEMAKAN UNTUK PAGE BIASA (PAGE 3+)
        # -----------------------------------------------------------------
        page_text_lower = full_page_text.lower()
        is_other_exempted = any(
            k in page_text_lower for k in ["list of publications", "publication", "penerbitan"]
        )

        skip_pagenum_check = (
            is_page_1_or_2
            or is_title_or_cover 
            or is_declaration_page
            or (in_appendix_section and abaikan_pagenum_appendix) 
            or is_other_exempted
        )

        # Muka Surat 3 ke atas WAJIB ada nombor muka surat
        if not skip_pagenum_check and not has_pagenum_found:
            loc_label = "sebelah kiri/atas" if is_landscape else "bahagian bawah tengah"
            page_errors.append({
                "msg": f"Nombor muka surat tidak dikesan di {loc_label}.",
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
                    # 📌 SEMAKAN TAJUK BAB / SEKSYEN
                    # -----------------------------------------------------------------
                    if is_chapter_title or is_prelim_title:
                        first_span = line["spans"][0]
                        heading_font = first_span["font"].lower()
                        heading_size = round(first_span["size"], 1)
                        h_x0, h_y0, h_x1, h_y1 = line["bbox"]

                        is_bold = "bold" in heading_font or "black" in heading_font
                        if not is_bold:
                            page_errors.append({
                                "msg": f"Tajuk Seksyen/Bab mesti BOLD: '{full_line_text[:30]}...'",
                                "bbox": line["bbox"],
                            })

                        line_center_x = (h_x0 + h_x1) / 2
                        printable_center_x = (cur_m_left + cur_m_right) / 2
                        TOLERANCE_PT = 20.0
                        
                        if abs(line_center_x - printable_center_x) > TOLERANCE_PT:
                            page_errors.append({
                                "msg": f"Tajuk Seksyen/Bab mesti di TENGAH (Centre): '{full_line_text[:30]}...'",
                                "bbox": line["bbox"],
                            })

                        line_height = h_y1 - h_y0
                        if heading_size > 0 and (line_height / heading_size) > 1.4:
                            page_errors.append({
                                "msg": f"Tajuk Seksyen/Bab mesti SINGLE SPACING: '{full_line_text[:30]}...'",
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
                                    page_errors.append({
                                        "msg": f"Jenis font tidak sah ({font_name}): '{text[:25]}...'",
                                        "bbox": bbox,
                                    })

                                # Semakan saiz font
                                if clean_word_len >= 3:
                                    if size < 7.5:
                                        page_errors.append({
                                            "msg": f"Saiz font terlalu kecil ({size}pt): '{text[:25]}...'",
                                            "bbox": bbox,
                                        })
                                    elif 12.8 < size < 17.5 and not (is_chapter_title or is_prelim_title):
                                        page_errors.append({
                                            "msg": f"Saiz font tidak piawai ({size}pt): '{text[:25]}...'",
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
                                    page_errors.append({
                                        "msg": f"Kedudukan Tajuk Jadual Salah / Tiada Jadual Di Bawah: '{full_line_text[:35]}...'",
                                        "bbox": line["bbox"],
                                    })

                                clean_title_text = full_line_text.strip()
                                if re.match(r"^(Table|Jadual)\s+\d+(\.\d+)*\.?$", clean_title_text, re.IGNORECASE):
                                    page_errors.append({
                                        "msg": f"Format Tajuk Jadual Terpisah Baris: '{clean_title_text}' (Perlu sebaris dengan penerangan)",
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
                                    page_errors.append({
                                        "msg": f"Kedudukan Tajuk Rajah Salah (Mesti Di Bawah Rajah): '{full_line_text[:35]}...'",
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

        # 1. Semak ralat jika nombor M/S terpaparpada Title Page (m/s 1)
        if page_num == 0 and has_pagenum_found:
            page_errors.append({
                "msg": "Title Page: Nombor muka surat TIDAK BOLEH dipaparkan.",
                "bbox": None,
            })

        # 2. Semak ralat jika nombor M/S terpapar pada Declaration Page (m/s 2)
        if (is_declaration_page or page_num == 1) and has_pagenum_found:
            page_errors.append({
                "msg": "Declaration / Halaman Pengakuan: Nombor muka surat TIDAK BOLEH dipaparkan.",
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
            loc_label = "sebelah kiri/atas" if is_landscape else "bahagian bawah tengah"
            page_errors.append(
                {
                    "msg": f"Nombor muka surat tidak dikesan di {loc_label}.",
                    "bbox": None,
                }
            )

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
        with st.spinner("Menjana fail PDF akhir... Sila tunggu sebentar."):
            st.session_state.report_pdf_bytes = generate_pdf_report(
                detected_issues, len(doc)
            )
            st.session_state.annotated_pdf_bytes = generate_annotated_thesis(
                doc, all_pages_errors_list, st.session_state.ignored_errors
            )
        st.success("Fail PDF telah sedia untuk dimuat turun!")

    if (
        st.session_state.report_pdf_bytes is not None
        and st.session_state.annotated_pdf_bytes is not None
    ):
        col_down1, col_down2 = st.columns(2)

        with col_down1:
            btn_html_1 = create_download_button_html(
                st.session_state.report_pdf_bytes,
                "Laporan_Semakan_Format_Tesis_USM.pdf",
                "📥 1. Muat Turun Laporan Ringkasan (PDF)",
                color="#2563eb",
            )
            st.markdown(btn_html_1, unsafe_allow_html=True)

        with col_down2:
            btn_html_2 = create_download_button_html(
                st.session_state.annotated_pdf_bytes,
                "Tesis_Visual_Kotak_Ralat.pdf",
                "📥 2. Muat Turun Tesis Berkotak Visual (PDF)",
                color="#059669",
            )
            st.markdown(btn_html_2, unsafe_allow_html=True)

    # =========================================================================
    # 🔍 PRATONTON VISUAL PER MUKA SURAT (KOD BERSIH TANPA DUPLIKASI)
    # =========================================================================
    st.markdown("---")
    st.subheader("🔍 Mod Semakan & Pratonton Visual")

    for page_num in range(len(doc)):
        unique_page_errors = all_pages_errors_list[page_num]
        is_landscape = doc[page_num].rect.width > doc[page_num].rect.height
        tag_landscape = " [Landscape]" if is_landscape else ""

        # 1. Kira bilangan isu yang belum di-bypass
        active_errors_count = sum(
            1 for i, _ in enumerate(unique_page_errors)
            if f"p{page_num+1}_{i}" not in st.session_state.ignored_errors
        )

        # 2. Set status label mengikut jumlah isu aktif
        if active_errors_count > 0:
            status_str = f"⚠️ Ada Isu: {active_errors_count}"
        else:
            status_str = "✅ Baik / Disemak"

        # 3. HANYA 1 EXPANDER SAHAJA PER MUKA SURAT
        with st.expander(
            f"Muka Surat {page_num + 1}{tag_landscape} - ({status_str})"
        ):
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

            # Kolum Kiri: Pratonton Gambar
            with col_img:
                st.image(
                    img,
                    caption=f"Pratonton MS {page_num + 1}",
                    use_container_width=True,
                )

            # Kolum Kanan: Senarai Isu & Master Checkbox
            with col_details:
                if not unique_page_errors:
                    st.success("Muka surat ini bebas daripada ralat format.")
                else:
                    st.write("**Senarai Isu Dikesan:**")

                    page_err_ids = []
                    for i, err in enumerate(unique_page_errors):
                        err_id = f"p{page_num+1}_{i}"
                        page_err_ids.append(err_id)
                        is_ignored = err_id in st.session_state.ignored_errors

                        st.checkbox(
                            f"Abaikan (Bypass): {err['msg']}",
                            key=f"cb_{err_id}",
                            value=is_ignored,
                            on_change=toggle_bypass,
                            args=(err_id,),
                        )

                    st.divider()

                    all_bypassed = all(
                        eid in st.session_state.ignored_errors for eid in page_err_ids
                    )

                    def toggle_bypass_all_page(err_ids, p_num):
                        is_all_checked = st.session_state[f"cb_all_p{p_num+1}"]
                        for eid in err_ids:
                            if is_all_checked:
                                st.session_state.ignored_errors.add(eid)
                                st.session_state[f"cb_{eid}"] = True
                            else:
                                st.session_state.ignored_errors.discard(eid)
                                st.session_state[f"cb_{eid}"] = False

                    st.checkbox(
                        "☑️ **Abaikan Semua Isu Muka Surat Ini (Bypass All)**",
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
