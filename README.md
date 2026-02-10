# 📐 Pattern Tiling Tool

Convert large A0 sewing patterns into printable A4/Letter size pages with professional alignment guides.

## ✨ Features

- **Scale Rulers**: 5cm and 2" rulers on every page for print verification
- **Page Numbers**: Clear letter-number labels (A1, A2, B1, B2, etc.)
- **Alignment Marks**: Corner marks with arrows showing adjacent pages
- **Crop Marks**: Dashed center guides for precise alignment
- **Grid Info**: Row and column position on each page

## 📋 How to Use

### Option 1: Streamlit Web App (Recommended)

Run a simple web interface to upload a pattern and download the tiled PDF.

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
2. **Start the app**:
   ```bash
   streamlit run app.py
   ```
3. **In your browser**:
   - Upload your pattern PDF
   - Choose paper size (A4 or US Letter)
   - Adjust DPI and margins if needed
   - Click **Generate tiled PDF**
   - Download the resulting tiled PDF

### Option 2: Manual Script Use (Advanced)

You can still run the tiling logic directly from Python:

```python
from reportlab.lib.pagesizes import A4, letter
from tile_pattern import create_tiled_pdf

rows, cols = create_tiled_pdf(
    input_pdf="/path/to/your/pattern.pdf",
    output_pdf="/path/to/output_tiled.pdf",
    tile_size=A4,        # or letter
    dpi=100,             # adjust as needed
    top_margin_mm=50,    # default
    side_margin_mm=10,   # default
)
print(f"Tiled into {rows} rows x {cols} columns")
```

## 🎯 What Gets Created

Each page includes:
- ✅ Centered scale rulers (5cm + 2 inches)
- ✅ Large page number (A1, A2, etc.)
- ✅ Grid position (Row X/Y | Column X/Y)
- ✅ Corner L-marks with neighbor indicators
- ✅ Edge alignment marks
- ✅ Your pattern content

## 🖨️ Printing Instructions

1. **Print at 100% scale** (NO "fit to page")
2. **Verify scale**: The 5cm ruler should measure exactly 5cm
3. **Arrange pages**: Follow the grid (A1-A8 = row 1, B1-B8 = row 2, etc.)
4. **Align pages**: Use corner arrows to match neighbors
5. **Tape together**: On the back side with clear tape

## 📏 Supported Sizes

- **Input**: Any size PDF (A0, A1, custom sizes)
- **Output**: A4 (default) or Letter size
- **DPI**: Adjustable (default 100, increase for better quality)

## 🔧 Technical Details

- **Engine**: PyMuPDF + ReportLab
- **Quality**: 100 DPI default (balance of quality vs file size)
- **Grid**: Automatically calculated based on pattern size
- **Margins**: 50mm top (for rulers/labels), 10mm sides

## 💡 Tips

- **Large patterns**: May create 50-100+ pages
- **Memory issues**: Lower DPI from 100 to 75
- **Better quality**: Increase DPI to 150 (larger file)
- **US patterns**: Change `tile_size=A4` to `tile_size=letter`

## 📁 File Locations

- Core tiling logic: `tile_pattern.py`
- Streamlit app entry point: `app.py`

---

Created: February 2026  
Last Updated: February 2026  
Version: 1.0
