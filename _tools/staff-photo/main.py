#!/usr/bin/env python3
"""
Crop staff photos so the face is centered at a consistent size.

Detects the face in an original photo (assets_data/staff/*.jpg), crops it
around the eyes with fixed framing, and writes a 300x360 JPEG to
assets/images/staff/ with metadata stripped.

Usage:
    pip install -r _tools/staff-photo/requirements.txt

    python3 _tools/staff-photo/main.py assets_data/staff/NAME.jpg [...]
    python3 _tools/staff-photo/main.py --all
    python3 _tools/staff-photo/main.py --all --preview sheet.jpg   # no overwrite
    python3 _tools/staff-photo/main.py --measure   # framing of current outputs

Framing adjustments (applied to every input; usually given with one photo):
    --scale 1.1          zoom out by 10%
    --shift-x / --shift-y   move the crop by a fraction of its width/height
    --level              rotate so the eyes are horizontal
"""

import argparse
import math
import statistics
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageOps

ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT / 'assets_data' / 'staff'
OUT_DIR = ROOT / 'assets' / 'images' / 'staff'
MODEL = Path(__file__).resolve().parent / 'face_detection_yunet_2023mar.onnx'

OUT_W, OUT_H = 300, 360
# Framing, relative to the output size. Calibrated with --measure.
EYE_DIST_RATIO = 0.175
EYE_Y_RATIO = 0.34

DETECT_MAX_SIDE = 1024
JPEG_QUALITY = 85


class FaceNotFound(Exception):
    pass


cv2.utils.logging.setLogLevel(cv2.utils.logging.LOG_LEVEL_ERROR)
_detector = None


def load_image(path):
    img = Image.open(path)
    img = ImageOps.exif_transpose(img)
    return img.convert('RGB')


def detect_face(img):
    """Return (box, right_eye, left_eye) of the most prominent face."""
    scale = min(1.0, DETECT_MAX_SIDE / max(img.size))
    small = img.resize((round(img.width * scale), round(img.height * scale)),
                       Image.LANCZOS) if scale < 1 else img
    bgr = cv2.cvtColor(np.asarray(small), cv2.COLOR_RGB2BGR)

    global _detector
    if _detector is None:
        _detector = cv2.FaceDetectorYN.create(str(MODEL), '', (0, 0))
    _detector.setInputSize((bgr.shape[1], bgr.shape[0]))
    _, faces = _detector.detect(bgr)
    if faces is None or len(faces) == 0:
        raise FaceNotFound('no face detected')

    faces = sorted(faces, key=lambda f: f[2] * f[3], reverse=True)
    if len(faces) > 1:
        warn(f'{len(faces)} faces detected; using the largest')
    f = faces[0] / scale
    return f[0:4], f[4:6], f[6:8]


def compute_crop(img_size, eye_center, eye_dist, scale=1.0, shift=(0.0, 0.0)):
    """Return (left, top, width, height) and a list of warnings."""
    img_w, img_h = img_size
    w = eye_dist / EYE_DIST_RATIO * scale
    h = w * OUT_H / OUT_W
    notes = []

    fit = min(1.0, img_w / w, img_h / h)
    if fit < 1:
        w, h = w * fit, h * fit
        notes.append(f'image too small for target framing; zoomed in {1 / fit:.2f}x')

    left = eye_center[0] - w * (0.5 - shift[0])
    top = eye_center[1] - h * (EYE_Y_RATIO - shift[1])
    clamped_left = min(max(left, 0), img_w - w)
    clamped_top = min(max(top, 0), img_h - h)
    if abs(clamped_left - left) > w * 0.02 or abs(clamped_top - top) > h * 0.02:
        notes.append('face too close to the image edge; crop shifted off-center')
    return (clamped_left, clamped_top, w, h), notes


def process(path, args):
    img = load_image(path)
    box, eye_r, eye_l = detect_face(img)
    eye_center = (eye_r + eye_l) / 2

    if args.level:
        dx, dy = eye_l - eye_r
        angle = math.degrees(math.atan2(dy, dx))
        img = img.rotate(angle, center=tuple(eye_center), resample=Image.BICUBIC)

    eye_dist = float(np.hypot(*(eye_l - eye_r)))
    (left, top, w, h), notes = compute_crop(
        img.size, eye_center, eye_dist, args.scale, (args.shift_x, args.shift_y))
    for n in notes:
        warn(n)

    if args.debug:
        save_debug(img, box, eye_r, eye_l, (left, top, w, h), Path(args.debug) / path.name)

    return img.resize((OUT_W, OUT_H), Image.LANCZOS, box=(left, top, left + w, top + h))


def save_debug(img, box, eye_r, eye_l, crop, out_path):
    dbg = img.copy()
    draw = ImageDraw.Draw(dbg)
    lw = max(2, round(max(img.size) / 400))
    x, y, w, h = box
    draw.rectangle((x, y, x + w, y + h), outline='yellow', width=lw)
    for ex, ey in (eye_r, eye_l):
        draw.ellipse((ex - 2 * lw, ey - 2 * lw, ex + 2 * lw, ey + 2 * lw), fill='red')
    cl, ct, cw, ch = crop
    draw.rectangle((cl, ct, cl + cw, ct + ch), outline='lime', width=lw)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    dbg.save(out_path.with_suffix('.jpg'), quality=JPEG_QUALITY)


def save_output(img, out_path):
    # A fresh image carries no EXIF/ICC/DPI from the original.
    clean = Image.new('RGB', img.size)
    clean.paste(img)
    clean.save(out_path, 'JPEG', quality=JPEG_QUALITY, optimize=True, progressive=True)


def save_contact_sheet(items, out_path, cols=6, pad=4):
    rows = math.ceil(len(items) / cols)
    sheet = Image.new('RGB', (cols * (OUT_W + pad) + pad, rows * (OUT_H + pad) + pad), 'white')
    for i, (_, img) in enumerate(items):
        sheet.paste(img, (pad + (i % cols) * (OUT_W + pad), pad + (i // cols) * (OUT_H + pad)))
    sheet.save(out_path, quality=JPEG_QUALITY)


def measure():
    """Print the framing ratios of the current output photos."""
    dist_ratios, y_ratios = [], []
    for path in sorted(OUT_DIR.glob('*.jpg')):
        img = load_image(path)
        try:
            _, eye_r, eye_l = detect_face(img)
        except FaceNotFound:
            print(f'{path.name}: no face detected')
            continue
        d = float(np.hypot(*(eye_l - eye_r))) / img.width
        y = float((eye_r[1] + eye_l[1]) / 2) / img.height
        x = float((eye_r[0] + eye_l[0]) / 2) / img.width
        dist_ratios.append(d)
        y_ratios.append(y)
        print(f'{path.name}: eye_dist={d:.3f} eye_y={y:.3f} eye_x={x:.3f}')
    if dist_ratios:
        print(f'median: EYE_DIST_RATIO={statistics.median(dist_ratios):.3f} '
              f'EYE_Y_RATIO={statistics.median(y_ratios):.3f}')


_current = ''


def warn(msg):
    print(f'WARNING: {_current}: {msg}', file=sys.stderr)


def main():
    global _current
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('files', nargs='*', type=Path, help='original photos')
    parser.add_argument('--all', action='store_true', help=f'process every photo in {SRC_DIR.relative_to(ROOT)}')
    parser.add_argument('--preview', metavar='FILE', help='write a contact sheet instead of the outputs')
    parser.add_argument('--measure', action='store_true', help='print framing of current outputs')
    parser.add_argument('--debug', metavar='DIR', help='write originals annotated with face and crop')
    parser.add_argument('--scale', type=float, default=1.0, help='>1 zooms out, <1 zooms in')
    parser.add_argument('--shift-x', type=float, default=0.0, help='move crop right by fraction of width')
    parser.add_argument('--shift-y', type=float, default=0.0, help='move crop down by fraction of height')
    parser.add_argument('--level', action='store_true', help='rotate so the eyes are horizontal')
    args = parser.parse_args()

    if args.measure:
        measure()
        return 0

    files = list(args.files)
    if args.all:
        for p in sorted(SRC_DIR.iterdir()):
            if p.suffix.lower() in ('.jpg', '.jpeg'):
                files.append(p)
            elif p.is_file():
                print(f'SKIP: {p.name}: needs original JPG', file=sys.stderr)
    if not files:
        parser.error('no input files (give paths or --all)')
    for p in files:
        if not p.resolve().is_relative_to(SRC_DIR):
            parser.error(f'{p}: input must be an original in {SRC_DIR.relative_to(ROOT)}/')

    results, failed = [], 0
    for path in files:
        _current = path.name
        try:
            results.append((path, process(path, args)))
        except FaceNotFound as e:
            print(f'ERROR: {path.name}: {e}', file=sys.stderr)
            failed += 1
        except Exception as e:
            print(f'ERROR: {path.name}: {type(e).__name__}: {e}', file=sys.stderr)
            failed += 1

    if args.preview and results:
        save_contact_sheet(results, args.preview)
        print(f'wrote {args.preview}')
    else:
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        for path, img in results:
            out = OUT_DIR / (path.stem + '.jpg')
            save_output(img, out)
            print(f'wrote {out.relative_to(ROOT)}')

    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main())
