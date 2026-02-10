#!/usr/bin/env python3
"""
Pattern Tiling - Image-based approach
Converts PDF to high-res image, then tiles it
"""

from PIL import Image, ImageDraw, ImageFont
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm, cm, inch
import fitz  # PyMuPDF
import os

def create_tiled_pdf(
    input_pdf,
    output_pdf,
    tile_size=A4,
    dpi=300,
    top_margin_mm=50,
    side_margin_mm=10,
):
    """Convert PDF to image and tile it"""
    
    # Open PDF with PyMuPDF
    doc = fitz.open(input_pdf)
    page = doc[0]
    
    # Convert to high-res image
    zoom = dpi / 72  # 72 is default DPI
    mat = fitz.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=mat)
    
    # Convert to PIL Image
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    
    print(f"Original image: {img.width}x{img.height} pixels at {dpi} DPI")
    print(f"Physical size: {img.width/dpi*25.4:.1f}mm x {img.height/dpi*25.4:.1f}mm")
    
    doc.close()
    
    # Calculate tile dimensions in pixels
    tile_width_mm, tile_height_mm = tile_size[0]/mm, tile_size[1]/mm
    
    usable_width_mm = tile_width_mm - 2 * side_margin_mm
    usable_height_mm = tile_height_mm - top_margin_mm - side_margin_mm
    
    # Convert to pixels
    usable_width_px = int(usable_width_mm / 25.4 * dpi)
    usable_height_px = int(usable_height_mm / 25.4 * dpi)
    
    # Calculate grid
    cols = (img.width + usable_width_px - 1) // usable_width_px
    rows = (img.height + usable_height_px - 1) // usable_height_px
    
    print(f"Usable tile size: {usable_width_mm:.1f}mm x {usable_height_mm:.1f}mm")
    print(f"Usable tile pixels: {usable_width_px}x{usable_height_px}")
    print(f"Grid: {rows} rows x {cols} columns = {rows*cols} pages")
    
    # Create PDF
    c = canvas.Canvas(output_pdf, pagesize=tile_size)
    tile_width_pt, tile_height_pt = tile_size
    
    page_count = 0
    for row in range(rows):
        for col in range(cols):
            # Extract tile from image
            x1 = col * usable_width_px
            y1 = row * usable_height_px
            x2 = min(x1 + usable_width_px, img.width)
            y2 = min(y1 + usable_height_px, img.height)
            
            tile_img = img.crop((x1, y1, x2, y2))
            
            # Save tile temporarily
            tile_path = f"/tmp/tile_{row}_{col}.png"
            tile_img.save(tile_path, "PNG", dpi=(dpi, dpi))
            
            # Start new page
            if page_count > 0:
                c.showPage()
            page_count += 1
            
            # Draw the pattern tile
            img_x = side_margin_mm * mm
            img_y = side_margin_mm * mm
            img_w = (x2 - x1) / dpi * inch
            img_h = (y2 - y1) / dpi * inch
            
            c.drawImage(tile_path, img_x, img_y, width=img_w, height=img_h, preserveAspectRatio=True)
            
            # Add scale ruler at top - centered properly
            ruler_y = tile_height_pt - 12*mm
            
            # Calculate total ruler width: 5cm + gap + 2inch
            gap = 8*mm
            total_ruler_width = 5*cm + gap + 2*inch
            ruler_start_x = (tile_width_pt - total_ruler_width) / 2
            
            # 5cm scale
            ruler_x = ruler_start_x
            c.setFont("Helvetica-Bold", 8)
            c.drawCentredString(ruler_x + 2.5*cm, ruler_y + 5*mm, "5cm")
            c.setLineWidth(0.5)
            c.rect(ruler_x, ruler_y, 5*cm, 3*mm, stroke=1, fill=0)
            
            for i in range(6):
                x = ruler_x + i * cm
                c.line(x, ruler_y, x, ruler_y + 3*mm)
                if i > 0:
                    c.setFont("Helvetica", 6)
                    c.drawCentredString(x - 0.5*cm, ruler_y - 2.5*mm, str(i))
            
            # 2 inches scale
            inch_x = ruler_x + 5*cm + gap
            c.setFont("Helvetica-Bold", 8)
            c.drawCentredString(inch_x + 1*inch, ruler_y + 5*mm, '2"')
            c.rect(inch_x, ruler_y, 2*inch, 3*mm, stroke=1, fill=0)
            
            for i in range(9):
                x = inch_x + i * inch / 4
                if i % 4 == 0:
                    c.line(x, ruler_y, x, ruler_y + 3*mm)
                    c.setFont("Helvetica", 6)
                    c.drawCentredString(x, ruler_y - 2.5*mm, str(i//4))
                elif i % 2 == 0:
                    c.line(x, ruler_y, x, ruler_y + 2*mm)
                else:
                    c.line(x, ruler_y, x, ruler_y + 1.5*mm)
            
            # Page label - centered and well positioned
            page_label = f"{chr(65 + row)}{col + 1}"
            c.setFont("Helvetica-Bold", 18)
            c.drawCentredString(tile_width_pt / 2, tile_height_pt - 28*mm, page_label)
            
            # Grid info
            c.setFont("Helvetica", 8)
            grid_info = f"Row {row+1}/{rows}  |  Column {col+1}/{cols}"
            c.drawCentredString(tile_width_pt / 2, tile_height_pt - 36*mm, grid_info)
            
            # Corner marks
            corner_size = 15*mm
            corner_offset = 10*mm
            
            c.setLineWidth(1.0)
            
            # Top-left
            c.line(corner_offset, tile_height_pt - corner_offset, 
                   corner_offset + corner_size, tile_height_pt - corner_offset)
            c.line(corner_offset, tile_height_pt - corner_offset, 
                   corner_offset, tile_height_pt - corner_offset - corner_size)
            c.setFont("Helvetica", 7)
            if row > 0:
                c.drawString(corner_offset + 2*mm, tile_height_pt - corner_offset - corner_size - 4*mm, 
                           f"↑ {chr(65+row-1)}{col+1}")
            if col > 0:
                c.drawString(corner_offset - 8*mm, tile_height_pt - corner_offset - 5*mm, 
                           f"← {chr(65+row)}{col}")
            
            # Top-right
            c.line(tile_width_pt - corner_offset, tile_height_pt - corner_offset, 
                   tile_width_pt - corner_offset - corner_size, tile_height_pt - corner_offset)
            c.line(tile_width_pt - corner_offset, tile_height_pt - corner_offset, 
                   tile_width_pt - corner_offset, tile_height_pt - corner_offset - corner_size)
            if col < cols - 1:
                c.drawRightString(tile_width_pt - corner_offset - 2*mm, 
                                tile_height_pt - corner_offset - corner_size - 4*mm, 
                                f"{chr(65+row)}{col+2} →")
            
            # Bottom-left
            c.line(corner_offset, corner_offset, corner_offset + corner_size, corner_offset)
            c.line(corner_offset, corner_offset, corner_offset, corner_offset + corner_size)
            if row < rows - 1:
                c.drawString(corner_offset + 2*mm, corner_offset + corner_size + 2*mm, 
                           f"↓ {chr(65+row+1)}{col+1}")
            
            # Bottom-right
            c.line(tile_width_pt - corner_offset, corner_offset, 
                   tile_width_pt - corner_offset - corner_size, corner_offset)
            c.line(tile_width_pt - corner_offset, corner_offset, 
                   tile_width_pt - corner_offset, corner_offset + corner_size)
            
            # Center alignment marks
            c.setDash([2, 2])
            c.setLineWidth(0.5)
            c.line(tile_width_pt/2 - 5*mm, tile_height_pt - corner_offset/2, 
                   tile_width_pt/2 + 5*mm, tile_height_pt - corner_offset/2)
            c.line(tile_width_pt/2 - 5*mm, corner_offset/2, 
                   tile_width_pt/2 + 5*mm, corner_offset/2)
            c.line(corner_offset/2, tile_height_pt/2 - 5*mm, 
                   corner_offset/2, tile_height_pt/2 + 5*mm)
            c.line(tile_width_pt - corner_offset/2, tile_height_pt/2 - 5*mm, 
                   tile_width_pt - corner_offset/2, tile_height_pt/2 + 5*mm)
            c.setDash([])
            
            # Clean up temp file
            os.remove(tile_path)
            
            print(f"  Created page {page_label} ({row+1},{col+1})")
    
    c.save()
    print(f"\nSaved: {output_pdf}")
    print(f"Total pages: {rows * cols}")
    return rows, cols

if __name__ == "__main__":
    os.makedirs("/mnt/user-data/outputs", exist_ok=True)
    
    print("=" * 70)
    print("Pattern Tiling Tool - Image-Based")
    print("=" * 70)
    
    rows, cols = create_tiled_pdf(
        "/home/user/pattern.pdf",
        "/mnt/user-data/outputs/Jacinta_Midi_Dress_Tiled.pdf",
        tile_size=A4,
        dpi=100  # Balance between quality and file size
    )
    
    print("\n" + "=" * 70)
    print("ASSEMBLY INSTRUCTIONS:")
    print("=" * 70)
    print("1. Print all pages at 100% scale (DO NOT use 'fit to page')")
    print("2. Verify scale: Measure the 5cm ruler - it should be exactly 5cm")
    print("3. Arrange pages in grid: A1-A8 (top row), B1-B8 (2nd row), etc.")
    print("4. Align using corner marks and arrows pointing to adjacent pages")
    print("5. Tape pages together on the back side")
    print(f"6. Final pattern: {rows} rows × {cols} columns")
    print("=" * 70)
