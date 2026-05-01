"""
Barcode generator utility.
Clears the output folder on every run so only the latest AWBs remain.
Generates one barcode per AWB + a single combined 'latest_awbs.png'.
"""
import os
import glob
import shutil

import barcode
from barcode.writer import ImageWriter
from PIL import Image, ImageDraw, ImageFont

OUTPUT_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "..", "awb_barcodes"
)
OUTPUT_DIR = os.path.normpath(OUTPUT_DIR)

_FONT_BOLD  = "C:/Windows/Fonts/arialbd.ttf"
_FONT_REG   = "C:/Windows/Fonts/arial.ttf"
_LABEL_H    = 44
_PADDING    = 20
_COLS       = 2


def _get_font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()


def _make_single(awb: str, source: str, order_type: str) -> Image.Image:
    """Return a PIL Image with the Code128 barcode + label header."""
    writer = ImageWriter()
    writer.set_options({
        "module_height": 15.0,
        "module_width": 0.8,
        "quiet_zone": 6.5,
        "font_size": 10,
        "text_distance": 5.0,
        "background": "white",
        "foreground": "black",
        "write_text": True,
    })
    Code128 = barcode.get_barcode_class("code128")
    bc = Code128(awb, writer=writer)

    tmp_path = os.path.join(OUTPUT_DIR, f"_tmp_{awb}")
    bc.save(tmp_path)
    png = tmp_path + ".png"

    with Image.open(png) as _raw:
        bc_img = _raw.copy()
    os.remove(png)

    # Add label strip on top
    final = Image.new("RGB", (bc_img.width, bc_img.height + _LABEL_H), "white")
    final.paste(bc_img, (0, _LABEL_H))
    draw = ImageDraw.Draw(final)
    draw.text((10, 6),  f"{source}  |  {order_type}",
              fill="black",   font=_get_font(_FONT_BOLD, 16))
    draw.text((10, 26), f"AWB: {awb}",
              fill="#444444", font=_get_font(_FONT_REG, 13))
    return final


def _make_combined(images: list, labels: list) -> Image.Image:
    """Stitch all barcode images into a neat grid (2 columns)."""
    if not images:
        return Image.new("RGB", (100, 100), "white")

    cell_w = max(img.width  for img in images) + _PADDING
    cell_h = max(img.height for img in images) + _PADDING

    cols   = min(_COLS, len(images))
    rows   = (len(images) + cols - 1) // cols

    title_h = 50
    canvas_w = cols * cell_w + _PADDING
    canvas_h = rows * cell_h + _PADDING + title_h

    canvas = Image.new("RGB", (canvas_w, canvas_h), "#f5f5f5")
    draw   = ImageDraw.Draw(canvas)

    # Title bar
    draw.rectangle([0, 0, canvas_w, title_h], fill="#1a1a2e")
    draw.text((15, 12), "Latest AWBs", fill="white",
              font=_get_font(_FONT_BOLD, 22))

    for i, (img, label) in enumerate(zip(images, labels)):
        row, col = divmod(i, cols)
        x = _PADDING + col * cell_w
        y = title_h + _PADDING // 2 + row * cell_h

        # White card background
        draw.rectangle([x - 4, y - 4, x + img.width + 4, y + img.height + 4],
                       fill="white", outline="#dddddd", width=1)
        canvas.paste(img, (x, y))

    return canvas


def generate(awb_list: list[tuple[str, str, str]], clear: bool = True) -> str:
    """
    Generate barcodes and a combined latest_awbs.png.

    awb_list: list of (source, order_type, awb)  e.g. [("Clickpost","PREPAID","ZPE...")]
    clear:    if True (default), wipe old files from the output folder first
    Returns:  path to the combined image
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    if clear:
        for f in glob.glob(os.path.join(OUTPUT_DIR, "*.png")):
            os.remove(f)

    images, labels = [], []
    for source, order_type, awb in awb_list:
        img = _make_single(awb, source, order_type)
        fname = os.path.join(OUTPUT_DIR, f"{source}_{order_type}_{awb}.png")
        img.save(fname)
        images.append(img)
        labels.append(f"{source} | {order_type}")
        print(f"  Barcode saved: {os.path.basename(fname)}")

    combined = _make_combined(images, labels)
    combined_path = os.path.join(OUTPUT_DIR, "latest_awbs.png")
    combined.save(combined_path)
    print(f"\n  Combined view: {combined_path}")
    return combined_path


if __name__ == "__main__":
    # Quick self-test
    sample = [
        ("Clickpost", "PREPAID", "ZPEDETMAQWDW0FN"),
        ("Clickpost", "COD",     "ZPEKAKE9Z9WPX0V"),
        ("Clickpost", "RVP",     "ZPEXBYETYNVFI13"),
        ("Uniware",   "PREPAID", "ZPENZE8RYZDFGVV"),
        ("Uniware",   "COD",     "ZPERM6V4LOVDCZT"),
        ("Easycom",   "PREPAID", "ZPE0QZX6D4ILO6D"),
        ("Easycom",   "COD",     "ZPEENX4F7H00DZX"),
    ]
    generate(sample)
