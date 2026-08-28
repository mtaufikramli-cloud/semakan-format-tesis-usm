import base64
import io
import re
from fpdf import FPDF
from PIL import Image
import pymupdf as fitz
import streamlit as st
import streamlit.components.v1 as components

# ==========================================
# ⚙️ TETAPAN AWAL APPLIKASI STREAMLIT
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
APP_VERSION = "v1.1.2 (Optimized Layout & Appendix Fix)"

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
    st.stop()

# ==================== SIDEBAR & TETAPAN ====================
with st.sidebar:
    st.caption(f"📌 **Versi:** {APP_VERSION}")
    if st.button("🚪 Log Out", type="secondary", use_container_width=True):
        logout()
    st.markdown("---")
    st.header("⚙️ Tetapan Templat Tesis")

    # Set nilai default awal supaya tidak ralat
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
        "Margin Kiri (mm)",
        min_value=10.0,
        max_value=60.0,
        value=default_left,
        step=1.0,
    )
    margin_right_mm = st.number_input(
        "Margin Kanan (mm)",
        min_value=10.0,
        max_value=60.0,
        value=default_right,
        step=1.0,
    )
    margin_top_mm = st.number_input(
        "Margin Atas (mm)",
        min_value=10.0,
        max_value=60.0,
        value=default_top,
        step=1.0,
    )
    margin_bottom_mm = st.number_input(
        "Margin Bawah (mm)",
        min_value=10.0,
        max_value=60.0,
        value=default_bottom,
        step=1.0,
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
        help="Semak format tajuk jadual (di atas jadual) dan tajuk rajah (di bawah rajah) mengikut saiz font, jenis font, ketebalan (bold), dan susunan perkataan."
    )

    abaikan_teks_dalam_gambar = st.sidebar.checkbox(
        "Abaikan Teks Dalam Gambar / Rajah",
        value=True,
        help="Abaikan ralat font untuk label atau teks yang bertindih di atas gambar/rajah."
    )

    abaikan_appendix = st.checkbox(
        "Abaikan Semakan Font pada Lampiran (Appendix)",
        value=True,
        help="Abaikan semakan jenis dan saiz font untuk semua muka surat di dalam bahagian Lampiran (Appendices)."
    )

    abaikan_pagenum_appendix = st.sidebar.checkbox(
        "Abaikan Semakan No. M/S di Lampiran (Appendices)",
        value=True,
        help="Abaikan semakan kehadiran dan kedudukan nombor muka surat bermula dari tajuk Lampiran utama."
    )

MATH_SYMBOL_FONTS = [
    "cambriamath",
    "symbol",
    "mtextra",
    "math",
    "wingdings",
    "webdings",
    "msmincho",
    "segoeui-symbol",
]

MM_TO_PT = 72 / 25.4  # Nisbah 1 mm ke pt (~2.83465)

MARGIN_LEFT_PT = margin_left_mm * MM_TO_PT
MARGIN_RIGHT_PT = margin_right_mm * MM_TO_PT
MARGIN_TOP_PT = margin_top_mm * MM_TO_PT
MARGIN_BOTTOM_PT = margin_bottom_mm * MM_TO_PT

def is_roman_numeral(val_str):
    """Fungsi menyemak secara dinamik sama ada perkataan ialah nombor Roman valid (i hingga c / 100+)"""
    val_str = val_str.lower().strip()
    if not val_str:
        return False
    # Pattern Regex khas untuk mengesahkan susunan nombor Roman yang sah (i, ii, iv, ix, xiv, xxviii, dsb)
    roman_pattern = r"^M{0,4}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})$"
    return bool(re.match(roman_pattern, val_str, re.IGNORECASE))

TABLE_PREFIX_REGEX = re.compile(
    r"^\s*(Table|Jadual)\s+\d+(\.\d+)*", re.IGNORECASE
)
FIGURE_PREFIX_REGEX = re.compile(
    r"^\s*(Figure|Rajah)\s+\d+(\.\d+)*", re.IGNORECASE
)
IN_TEXT_CITATION_REGEX = re.compile(
    r"^\s*(Figure|Rajah|Table|Jadual)\s+\d+(\.\d+)*\.\s", re.IGNORECASE
)
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
    pdf.cell(
        0,
        10,
        "Laporan Semakan Format Tesis",
        new_x="LMARGIN",
        new_y="NEXT",
        align="C",
    )
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(
        0,
        6,
        f"Jumlah Muka Surat Diperiksa: {total_pages}",
        new_x="LMARGIN",
        new_y="NEXT",
        align="C",
    )
    pdf.ln(5)

    if not filtered_errors:
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(
            0,
            10,
            "Tiada isu format dikesan. Tesis mematuhi piawaian!",
            new_x="LMARGIN",
            new_y="NEXT",
        )
    else:
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(30, 8, "Muka Surat", border=1, align="C")
        pdf.cell(
            160,
            8,
            "Butiran Isu Format",
            border=1,
            align="C",
            new_x="LMARGIN",
            new_y="NEXT",
        )

        pdf.set_font("Helvetica", "", 10)
        for item in filtered_errors:
            page_str = f"MS {item['page']}"
            issue_str = item["msg"].replace("*", "")
            pdf.cell(30, 8, page_str, border=1, align="C")
            pdf.cell(
                160, 8, issue_str[:90], border=1, new_x="LMARGIN", new_y="NEXT"
            )

    return bytes(pdf.output())


def generate_annotated_thesis(doc_input, all_pages_errors, ignored_set):
    pdf_buffer = io.BytesIO()
    doc_input.save(pdf_buffer)
    pdf_buffer.seek(0)
    annotated_doc = fitz.open(stream=pdf_buffer.read(), filetype="pdf")

    for page_num, errors in enumerate(all_pages_errors):
        page = annotated_doc[page_num]
        for i, err in enumerate(errors):
            err_id = f"p{page_num+1}_{i}"
            if err["bbox"] and err_id not in ignored_set:
                page.draw_rect(err["bbox"], color=(1, 0, 0), width=1.5)

    out_buffer = io.BytesIO()
    annotated_doc.save(out_buffer)
    annotated_doc.close()
    return out_buffer.getvalue()


def create_download_button_html(
    file_bytes, filename, button_text, color="#2563eb"
):
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

        # PASS 2: SEMAKAN MARGIN & TEKS
        for b in blocks:
            if "lines" in b:
                for line in b["lines"]:
                    full_line_text = "".join(
                        [s["text"] for s in line["spans"]]
                    ).strip()

                    for span in line["spans"]:
                        text = span["text"].strip()
                        size = round(span["size"], 1)
                        font_name = span["font"]
                        bbox = span["bbox"]

                        if not text:
                            continue

                        x0, y0, x1, y1 = bbox

                        is_this_pagenum_span = False
                        for p_box in pagenum_bboxes:
                            if abs(y0 - p_box[1]) < 15 and abs(x0 - p_box[0]) < 30:
                                is_this_pagenum_span = True
                                break

                        if is_this_pagenum_span:
                            continue

                        # Semakan Ralat Margin
                        if y1 > (cur_m_bottom + 2):
                            page_errors.append(
                                {
                                    "msg": f"Luar Margin Bawah: '{full_line_text[:20]}...'",
                                    "bbox": bbox,
                                }
                            )

                        if y0 < (cur_m_top - 2):
                            page_errors.append(
                                {
                                    "msg": f"Luar Margin Atas: '{full_line_text[:20]}...'",
                                    "bbox": bbox,
                                }
                            )

                        # Semakan Jenis & Saiz Font
                        skip_font_check = in_appendix_section or (abaikan_appendix and is_appendix_page)

                        if not skip_font_check:
                            font_name_clean = font_name.lower().replace(" ", "")
                            is_math_font = any(
                                mf in font_name_clean for mf in MATH_SYMBOL_FONTS
                            )

                            is_inside_image = False
                            if abaikan_teks_dalam_gambar and images_info:
                                for img in images_info:
                                    img_bbox = img["bbox"]
                                    text_center_x = (x0 + x1) / 2
                                    text_center_y = (y0 + y1) / 2
                                    
                                    if (img_bbox[0] <= text_center_x <= img_bbox[2]) and \
                                       (img_bbox[1] <= text_center_y <= img_bbox[3]):
                                        is_inside_image = True
                                        break

                            if not is_math_font and not is_inside_image:
                                font_matched = any(
                                    f.lower().replace(" ", "") in font_name_clean
                                    for f in allowed_fonts
                                )
                                if not font_matched and len(text) > 3:
                                    page_errors.append(
                                        {
                                            "msg": f"Jenis font tidak sah ({font_name}): '{text[:25]}...'",
                                            "bbox": bbox,
                                        }
                                    )

                                if len(text) > 5:
                                    if size < 8.0:
                                        page_errors.append(
                                            {
                                                "msg": f"Saiz font terlalu kecil ({size}pt): '{text[:25]}...'",
                                                "bbox": bbox,
                                            }
                                        )
                                    elif 12.5 < size < 18.0:
                                        page_errors.append(
                                            {
                                                "msg": f"Saiz font terlalu besar ({size}pt): '{text[:25]}...'",
                                                "bbox": bbox,
                                            }
                                        )

                        # Semakan Tajuk Jadual / Rajah
                        if semak_caption and not is_list_page:
                            is_dot_leader_line = bool(DOT_LEADER_REGEX.search(full_line_text))
                            is_sentence = bool(VERB_KEYWORDS_REGEX.search(full_line_text))
                            is_in_text_citation = bool(IN_TEXT_CITATION_REGEX.match(full_line_text))

                            if (
                                TABLE_PREFIX_REGEX.match(full_line_text)
                                and not is_sentence
                                and not is_dot_leader_line
                                and not is_in_text_citation
                            ):
                                table_below_close = False
                                for d in drawings:
                                    d_y0 = d["rect"][1]
                                    if 0 < (d_y0 - y1) < 50:
                                        table_below_close = True
                                        break

                                if not table_below_close:
                                    page_errors.append(
                                        {
                                            "msg": f"Kedudukan Tajuk Jadual Salah (Mesti Di Atas Jadual): '{full_line_text[:35]}...'",
                                            "bbox": bbox,
                                        }
                                    )

                                clean_title_text = full_line_text.strip()
                                if re.match(r"^(Table|Jadual)\s+\d+(\.\d+)*\.?$", clean_title_text, re.IGNORECASE):
                                    page_errors.append(
                                        {
                                            "msg": f"Format Tajuk Jadual Terlangkau/Terpisah Baris: '{clean_title_text}' (Sepatutnya sebaris dengan penerangan)",
                                            "bbox": bbox,
                                        }
                                    )

                            elif (
                                FIGURE_PREFIX_REGEX.match(full_line_text)
                                and not is_sentence
                                and not is_dot_leader_line
                                and not is_in_text_citation
                            ):
                                image_above_close = False
                                image_below_close = False

                                for img in images_info:
                                    img_y0 = img["bbox"][1]
                                    img_y1 = img["bbox"][3]

                                    if 0 < (y0 - img_y1) < 50:
                                        image_above_close = True

                                    if 0 < (img_y0 - y1) < 30:
                                        image_below_close = True

                                if image_below_close and not image_above_close:
                                    page_errors.append(
                                        {
                                            "msg": f"Kedudukan Tajuk Rajah Salah (Mesti Di Bawah Rajah): '{full_line_text[:35]}...'",
                                            "bbox": bbox,
                                        }
                                    )

        # SEMAKAN KEHADIRAN NOMBOR MUKA SURAT
        if not in_appendix_section:
            lines = [line.strip().upper() for line in full_page_text.split("\n") if line.strip()]
            for line in lines:
                if (line.startswith("APPENDIX") or line.startswith("LAMPIRAN")) and len(line) < 60:
                    in_appendix_section = True
                    break

        is_other_exempted = any(
            k in page_text_lower for k in ["list of publications", "publication"]
        )

        # PEMBETULAN DI SINI: Menyertakan abaikan_pagenum_appendix ke dalam syarat pengecualian
        skip_pagenum_check = (in_appendix_section and abaikan_pagenum_appendix) or is_other_exempted

        if page_num >= 2 and not skip_pagenum_check and not has_pagenum_found:
            loc_label = "sebelah kiri/atas" if is_landscape else "bahagian bawah tengah"
            page_errors.append(
                {
                    "msg": f"Nombor muka surat tidak dikesan di {loc_label}.",
                    "bbox": None,
                }
            )

        unique_page_errors = []
        seen_msgs = set()
        for e in page_errors:
            if e["msg"] not in seen_msgs:
                seen_msgs.add(e["msg"])
                unique_page_errors.append(e)

        all_pages_errors_list.append(unique_page_errors)

        # Kumpul ralat aktif untuk laporan
        for i, err in enumerate(unique_page_errors):
            err_id = f"p{page_num+1}_{i}"
            if err_id not in st.session_state.ignored_errors:
                detected_issues.append({"page": page_num + 1, "msg": err["msg"]})

    # =========================================================================
    # 📄 SEKSYEN JANA & MUAT TURUN DOKUMEN (DIPINDAHKAN KE ATAS UNTUK MESRA UX)
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
    # 🔍 PRATONTON VISUAL PER MUKA SURAT
    # =========================================================================
    st.markdown("---")
    st.subheader("🔍 Mod Semakan & Pratonton Visual")

    for page_num in range(len(doc)):
        unique_page_errors = all_pages_errors_list[page_num]
        is_landscape = doc[page_num].rect.width > doc[page_num].rect.height
        
        has_active_errors = any(
            f"p{page_num+1}_{i}" not in st.session_state.ignored_errors
            for i in range(len(unique_page_errors))
        )

        status_icon = "⚠️ Ada Isu" if has_active_errors else "✅ Baik / Disemak"
        tag_landscape = " [Landscape]" if is_landscape else ""

        with st.expander(
            f"Muka Surat {page_num + 1}{tag_landscape} - ({status_icon})"
        ):
            col_img, col_details = st.columns([1, 1])
            doc_page = doc[page_num]

            for i, err in enumerate(unique_page_errors):
                err_id = f"p{page_num+1}_{i}"
                if (
                    err["bbox"]
                    and err_id not in st.session_state.ignored_errors
                ):
                    doc_page.draw_rect(
                        err["bbox"], color=(1, 0, 0), width=1.5
                    )

            pix = doc_page.get_pixmap(dpi=120)
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

            with col_img:
                st.image(
                    img,
                    caption=f"Pratonton MS {page_num + 1}",
                    use_container_width=True,
                )

            with col_details:
                if not unique_page_errors:
                    st.success("Muka surat ini bebas daripada ralat format.")
                else:
                    st.write("**Senarai Isu Dikesan:**")
                    for i, err in enumerate(unique_page_errors):
                        err_id = f"p{page_num+1}_{i}"
                        is_ignored = err_id in st.session_state.ignored_errors

                        st.checkbox(
                            f"Abaikan (Bypass): {err['msg']}",
                            key=f"cb_{err_id}",
                            value=is_ignored,
                            on_change=toggle_bypass,
                            args=(err_id,),
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
