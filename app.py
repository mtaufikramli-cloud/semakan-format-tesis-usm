import base64
import io
from fpdf import FPDF
from PIL import Image
import pymupdf as fitz
import streamlit as st

st.set_page_config(
    page_title="Semakan Format Tesis USM", layout="wide", page_icon="📄"
)
st.title("📄 Sistem Semakan Format Tesis (USM Standard)")

# ==================== SIDEBAR: PRESET & TETAPAN ====================
st.sidebar.header("⚙️ Tetapan Template Tesis")

preset = st.sidebar.selectbox(
    "Pilih Templat Universiti",
    ["USM (Universiti Sains Malaysia)", "Custom (Manual)"],
)

if preset == "USM (Universiti Sains Malaysia)":
    default_left, default_right, default_top, default_bottom = (
        1.57,
        0.98,
        0.98,
        0.98,
    )
    default_fonts = [
        "Times New Roman",
        "TimesNewRoman",
        "Arial",
        "Calibri",
        "Garamond",
    ]
else:
    default_left, default_right, default_top, default_bottom = (
        1.50,
        1.00,
        1.00,
        1.00,
    )
    default_fonts = ["Times New Roman", "Arial"]

margin_left_inch = st.sidebar.number_input(
    "Margin Kiri (Inci)",
    min_value=0.5,
    max_value=2.0,
    value=default_left,
    step=0.01,
)
margin_right_inch = st.sidebar.number_input(
    "Margin Kanan (Inci)",
    min_value=0.5,
    max_value=2.0,
    value=default_right,
    step=0.01,
)
margin_top_inch = st.sidebar.number_input(
    "Margin Atas (Inci)",
    min_value=0.5,
    max_value=2.0,
    value=default_top,
    step=0.01,
)
margin_bottom_inch = st.sidebar.number_input(
    "Margin Bawah (Inci)",
    min_value=0.5,
    max_value=2.0,
    value=default_bottom,
    step=0.01,
)

allowed_fonts = st.sidebar.multiselect(
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

MARGIN_LEFT = (margin_left_inch * 72) - 10
MARGIN_RIGHT = (margin_right_inch * 72) - 12
MARGIN_TOP = (margin_top_inch * 72) - 8
MARGIN_BOTTOM = (margin_bottom_inch * 72) - 8

ROMAN_NUMERALS = [
    "i",
    "ii",
    "iii",
    "iv",
    "v",
    "vi",
    "vii",
    "viii",
    "ix",
    "x",
    "xi",
    "xii",
    "xiii",
    "xiv",
    "xv",
    "xvi",
    "xvii",
    "xviii",
    "xix",
    "xx",
]


# ==================== FUNGSI PENJANAAN PDF ====================
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
    """Menjana link muat turun HTML menggunakan Base64 URI bagi mengelakkan auto-download IDM"""
    b64 = base64.b64encode(file_bytes).decode()
    href = f'data:application/pdf;base64,{b64}'
    html = f"""
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
    return html


# ==================== KANDUNGAN UTAMA ====================
uploaded_file = st.file_uploader("Muat Naik Fail PDF Tesis", type=["pdf"])

if uploaded_file is not None:
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    st.success(f"Fail berjaya dimuat naik! Jumlah muka surat: {len(doc)}")

    # Inisialisasi State
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

        # Padamkan cache PDF supaya tiada muat turun automatik berlaku
        st.session_state.report_pdf_bytes = None
        st.session_state.annotated_pdf_bytes = None
        st.rerun()

    st.subheader("🔍 Mod Semakan & Pratonton Visual")
    st.info(
        "Petunjuk: Anda boleh menandakan **'Abaikan (Bypass)'** untuk isu yang hendak dikecualikan daripada laporan akhir."
    )

    detected_issues = []
    all_pages_errors_list = []

    for page_num in range(len(doc)):
        page = doc[page_num]
        rect = page.rect
        blocks = page.get_text("dict")["blocks"]

        is_landscape = rect.width > rect.height
        page_errors = []
        has_pagenum = False

        if is_landscape:
            cur_m_left, cur_m_right, cur_m_top, cur_m_bottom = (
                MARGIN_TOP,
                MARGIN_BOTTOM,
                MARGIN_LEFT,
                MARGIN_RIGHT,
            )
        else:
            cur_m_left, cur_m_right, cur_m_top, cur_m_bottom = (
                MARGIN_LEFT,
                MARGIN_RIGHT,
                MARGIN_TOP,
                MARGIN_BOTTOM,
            )

        for b in blocks:
            if "lines" in b:
                for line in b["lines"]:
                    for span in line["spans"]:
                        text = span["text"].strip()
                        size = round(span["size"], 1)
                        font_name = span["font"]
                        bbox = span["bbox"]

                        if not text:
                            continue

                        x0, y0, x1, y1 = bbox
                        center_x, center_y = (x0 + x1) / 2, (y0 + y1) / 2

                        is_pagenum_candidate = False
                        clean_text = text.lower().strip(".- ")

                        if clean_text.isdigit() or clean_text in ROMAN_NUMERALS:
                            if is_landscape:
                                if (
                                    x0 < 80
                                    and abs(center_y - (rect.height / 2)) < 150
                                ):
                                    has_pagenum = True
                                    is_pagenum_candidate = True
                            else:
                                if y0 > (
                                    rect.height - 70
                                ) and abs(center_x - (rect.width / 2)) < 120:
                                    has_pagenum = True
                                    is_pagenum_candidate = True

                        if is_pagenum_candidate:
                            continue

                        # 1. Semakan Margin
                        if x0 < cur_m_left:
                            page_errors.append(
                                {
                                    "msg": f"Luar Margin Kiri: '{text[:25]}...'",
                                    "bbox": bbox,
                                }
                            )
                        elif y0 < cur_m_top:
                            page_errors.append(
                                {
                                    "msg": f"Luar Margin Atas: '{text[:25]}...'",
                                    "bbox": bbox,
                                }
                            )
                        elif (rect.width - x1) < cur_m_right:
                            page_errors.append(
                                {
                                    "msg": f"Luar Margin Kanan: '{text[:25]}...'",
                                    "bbox": bbox,
                                }
                            )
                        elif (rect.height - y1) < cur_m_bottom:
                            page_errors.append(
                                {
                                    "msg": f"Luar Margin Bawah: '{text[:25]}...'",
                                    "bbox": bbox,
                                }
                            )

                        # 2. Semakan Font
                        font_name_clean = font_name.lower().replace(" ", "")
                        is_math_font = any(
                            mf in font_name_clean for mf in MATH_SYMBOL_FONTS
                        )

                        if not is_math_font:
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
                                elif size > 12.5 and size < 18.0:
                                    page_errors.append(
                                        {
                                            "msg": f"Saiz font terlalu besar ({size}pt): '{text[:25]}...'",
                                            "bbox": bbox,
                                        }
                                    )

        # 3. Semakan Nombor Muka Surat
        page_text = page.get_text().lower()
        is_exempted_page = any(
            k in page_text
            for k in [
                "appendix",
                "appendices",
                "list of publications",
                "publication",
            ]
        )

        if page_num >= 2 and not has_pagenum and not is_exempted_page:
            loc_label = (
                "sebelah kiri" if is_landscape else "bahagian bawah tengah"
            )
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

        tag_landscape = " [Landscape]" if is_landscape else ""
        has_active_errors = any(
            f"p{page_num+1}_{i}" not in st.session_state.ignored_errors
            for i in range(len(unique_page_errors))
        )

        status_icon = "⚠️ Ada Isu" if has_active_errors else "✅ Baik / Disemak"

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

                        if not is_ignored:
                            detected_issues.append(
                                {"page": page_num + 1, "msg": err["msg"]}
                            )

                        st.checkbox(
                            f"Abaikan (Bypass): {err['msg']}",
                            key=f"cb_{err_id}",
                            value=is_ignored,
                            on_change=toggle_bypass,
                            args=(err_id,),
                        )

    # ==================== SEKSYEN PENJANAAN & MUAT TURUN PDF ====================
    st.markdown("---")
    st.subheader("📄 Muat Turun Dokumen Akhir")

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

    # PAPARAN BUTANG HTML BASE64 (MENGELAKKAN IDM AUTO-DOWNLOAD)
    if (
        st.session_state.report_pdf_bytes is not None
        and st.session_state.annotated_pdf_bytes is not None
    ):
        st.markdown("---")
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