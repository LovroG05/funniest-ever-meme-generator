import os
import uuid
from io import BytesIO

from flask import Flask, render_template, request, url_for
from PIL import Image, ImageDraw, ImageFont


app = Flask(__name__)
UPLOAD_DIR = os.path.join(app.root_path, "static", "memes")
os.makedirs(UPLOAD_DIR, exist_ok=True)


def _draw_text(draw, text, font, image_width, position):
    if not text:
        return
    text = text.upper()
    text_width = draw.textbbox((0, 0), text, font=font)[2]
    x = (image_width - text_width) / 2
    y = position
    outline_range = 2
    for dx in range(-outline_range, outline_range + 1):
        for dy in range(-outline_range, outline_range + 1):
            draw.text((x + dx, y + dy), text, font=font, fill="black")
    draw.text((x, y), text, font=font, fill="white")


def _load_font(font_size):
    candidates = [
        "/usr/share/fonts/truetype/msttcorefonts/Impact.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, font_size)
        except OSError:
            continue
    return ImageFont.load_default()


def generate_meme(image_stream, top_text, bottom_text):
    image = Image.open(image_stream).convert("RGB")
    width, height = image.size
    draw = ImageDraw.Draw(image)
    font_size = max(width // 6, 48)
    font = _load_font(font_size)
    _draw_text(draw, top_text, font, width, 10)
    _draw_text(draw, bottom_text, font, width, height - font_size - 10)
    file_name = f"{uuid.uuid4().hex}.png"
    file_path = os.path.join(UPLOAD_DIR, file_name)
    image.save(file_path, "PNG")
    return file_name


@app.route("/", methods=["GET", "POST"])
def index():
    meme_url = None
    if request.method == "POST":
        uploaded = request.files.get("image")
        if uploaded and uploaded.filename:
            top_text = request.form.get("top_text", "")
            bottom_text = request.form.get("bottom_text", "")
            meme_name = generate_meme(uploaded.stream, top_text, bottom_text)
            meme_url = url_for("static", filename=f"memes/{meme_name}")
    return render_template("index.html", meme_url=meme_url)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=True)
