# /// script
# requires-python = ">=3.12"
# dependencies = ["pillow==12.3.0"]
# ///
"""Generate web images/posters and update the build journey. Run with uv run.

Keep original images alongside the WebP derivatives. Photos use quality 82 and
at most 1600 pixels per side; PNG diagrams retain every pixel with lossless WebP.
Requires ffmpeg on PATH for video posters. No extra build dependency is needed.
"""
from pathlib import Path
import re
import subprocess
import tempfile

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[1] / "docs/build-journey"
page = ROOT / "index.md"
text = page.read_text()
before = after = 0


def optimize_image(match):
    global before, after
    alt, relative = match.groups()
    source = ROOT / relative
    if source.suffix == ".webp":
        source = next(p for p in (source.with_suffix('.jpg'), source.with_suffix('.png')) if p.exists())
    with Image.open(source) as original:
        image = ImageOps.exif_transpose(original)
        if source.suffix.lower() != '.png':
            image.thumbnail((1600, 1600), Image.Resampling.LANCZOS)
        target = source.with_suffix('.webp')
        image.save(target, quality=82, method=6, lossless=source.suffix.lower() == '.png')
        width, height = image.size
    before += source.stat().st_size
    after += target.stat().st_size
    loading = 'loading=eager fetchpriority=high' if before == source.stat().st_size else 'loading=lazy'
    return f'![{alt}]({target.relative_to(ROOT).as_posix()}){{ {loading} decoding=async width={width} height={height} }}'


text = re.sub(r'!\[([^\]]*)\]\((images/[^)]+)\)\{[^}]*\}', optimize_image, text)


def optimize_video(match):
    tag, source_tag, relative = match.groups()
    target = (ROOT / relative).with_suffix('.webp')
    with tempfile.TemporaryDirectory() as temporary:
        frame = Path(temporary) / 'frame.png'
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', '1', '-i', str(ROOT / relative),
                        '-frames:v', '1', '-vf', 'scale=720:720:force_original_aspect_ratio=decrease',
                        str(frame)], check=True)
        with Image.open(frame) as image:
            image.save(target, quality=78, method=6)
            width, height = image.size
    tag = re.sub(r' (?:poster|width|height|loading)="[^"]*"', '', tag)
    tag = tag.replace('preload="metadata"', 'preload="none"')
    tag = tag.replace('style="', 'style="height: auto; ') if 'height: auto;' not in tag else tag
    tag = tag[:-1] + f' poster="{target.relative_to(ROOT).as_posix()}" width="{width}" height="{height}" loading="lazy">'
    return tag + source_tag


text = re.sub(r'(<video\b[^>]*>)(\s*<source src="(videos/[^"]+)"[^>]*>)', optimize_video, text)
page.write_text(text)
print(f'Displayed images: {before:,} → {after:,} bytes ({100 * (1 - after / before):.1f}% smaller)')
