import os
import tempfile

import streamlit as st
from reportlab.lib.pagesizes import A4, letter

from tile_pattern import create_tiled_pdf


def main():
    st.title("Pattern Tiling Tool")
    st.write(
        "Upload a sewing pattern PDF and convert it into tiled A4 or US Letter pages "
        "with scale rulers and alignment guides."
    )

    uploaded_file = st.file_uploader("Upload pattern PDF", type=["pdf"])

    with st.expander("Tiling settings", expanded=True):
        page_size_label = st.radio(
            "Page size",
            options=["A4", "US Letter"],
            index=0,
            help="Choose the paper size you will print on.",
        )

        dpi = st.number_input(
            "DPI (resolution)",
            min_value=50,
            max_value=300,
            value=100,
            step=25,
            help="Higher DPI gives better quality but larger files.",
        )

        col1, col2, col3 = st.columns(3)
        with col1:
            top_margin_mm = st.number_input(
                "Top margin (mm)",
                min_value=0,
                max_value=100,
                value=50,
                step=5,
                help="Space at the top of each page for rulers and labels.",
            )
        with col2:
            left_margin_mm = st.number_input(
                "Left margin (mm)",
                min_value=0,
                max_value=50,
                value=10,
                step=2,
                help="Left margin used for the pattern tile.",
            )
        with col3:
            right_margin_mm = st.number_input(
                "Right margin (mm)",
                min_value=0,
                max_value=50,
                value=10,
                step=2,
                help="Right margin used for the pattern tile.",
            )

    generated_pdf_bytes = None
    grid_info = None

    if uploaded_file is not None:
        generate = st.button("Generate tiled PDF", type="primary")

        if generate:
            with st.spinner("Generating tiled PDF..."):
                # Persist uploaded file to a temporary location
                with tempfile.NamedTemporaryFile(
                    suffix=".pdf", delete=False
                ) as input_tmp:
                    input_tmp.write(uploaded_file.read())
                    input_path = input_tmp.name

                # Temporary output path
                output_fd, output_path = tempfile.mkstemp(suffix="_tiled.pdf")
                os.close(output_fd)

                try:
                    # Choose page size
                    if page_size_label == "A4":
                        page_size = A4
                    else:
                        page_size = letter

                    # For now, use a single side margin value consistent with the
                    # existing implementation (left/right the same); we pass the
                    # left margin through to the tiling function.
                    rows, cols = create_tiled_pdf(
                        input_pdf=input_path,
                        output_pdf=output_path,
                        tile_size=page_size,
                        dpi=int(dpi),
                        top_margin_mm=float(top_margin_mm),
                        side_margin_mm=float(left_margin_mm),
                    )

                    grid_info = (rows, cols)

                    with open(output_path, "rb") as f:
                        generated_pdf_bytes = f.read()

                finally:
                    # Clean up temp files
                    if os.path.exists(input_path):
                        os.remove(input_path)
                    if os.path.exists(output_path):
                        os.remove(output_path)

    if generated_pdf_bytes is not None:
        if grid_info is not None:
            rows, cols = grid_info
            st.success(
                f"Generated tiled pattern: {rows} rows × {cols} columns "
                f"({rows * cols} pages)."
            )

        base_name = (
            os.path.splitext(uploaded_file.name)[0] if uploaded_file is not None else "pattern"
        )
        download_name = f"{base_name}_tiled.pdf"

        st.download_button(
            label="Download tiled PDF",
            data=generated_pdf_bytes,
            file_name=download_name,
            mime="application/pdf",
        )


if __name__ == "__main__":
    main()

