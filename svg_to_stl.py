"""svg_to_stl.py — converte SVG do Tinkercad em STL com domes."""

from __future__ import annotations

import argparse
import re
import xml.etree.ElementTree as ET
from typing import NamedTuple

import trimesh

from braille_dome import BrailleParams, make_dome, make_plate, export_stl


SVG_NS = '{http://www.w3.org/2000/svg}'


class CircleHit(NamedTuple):
    cx: float
    cy: float
    r: float


def _parse_length(value, default=0.0):
    if value is None:
        return default
    m = re.match(r'^\s*(-?\d+(?:\.\d+)?)\s*(mm|cm|in|px|pt)?\s*$', value)
    if not m:
        return default
    val = float(m.group(1))
    unit = m.group(2) or ''
    if unit == 'cm': val *= 10
    elif unit == 'in': val *= 25.4
    elif unit == 'pt': val *= 25.4 / 72
    return val


def parse_svg(svg_path):
    tree = ET.parse(svg_path)
    root = tree.getroot()
    width = _parse_length(root.get('width'))
    height = _parse_length(root.get('height'))
    vb = root.get('viewBox')
    if vb:
        parts = vb.replace(',', ' ').split()
        if len(parts) == 4:
            _, _, vw, vh = (float(p) for p in parts)
            if width == 0: width = vw
            if height == 0: height = vh

    circles = []
    for el in root.iter():
        tag = el.tag
        local = tag.split('}')[-1] if '}' in tag else tag
        if local == 'circle':
            cx = _parse_length(el.get('cx'))
            cy = _parse_length(el.get('cy'))
            r = _parse_length(el.get('r'))
            if r > 0:
                circles.append(CircleHit(cx, cy, r))
        elif local == 'ellipse':
            cx = _parse_length(el.get('cx'))
            cy = _parse_length(el.get('cy'))
            rx = _parse_length(el.get('rx'))
            ry = _parse_length(el.get('ry'))
            if rx > 0 and ry > 0 and abs(rx - ry) / max(rx, ry) < 0.2:
                circles.append(CircleHit(cx, cy, (rx + ry) / 2))
    return circles, width, height


def svg_to_braille_stl(svg_path, stl_out, params=None,
                       scale=1.0, flip_y=True, add_plate=True, verbose=True):
    if params is None:
        params = BrailleParams()
    circles, svg_w, svg_h = parse_svg(svg_path)
    if verbose:
        print(f"SVG: {svg_path} | canvas {svg_w}×{svg_h} | círculos {len(circles)}")
    if not circles:
        raise ValueError("Nenhum círculo encontrado no SVG.")

    pts = []
    for c in circles:
        x = c.cx * scale
        y = (svg_h - c.cy) * scale if flip_y else c.cy * scale
        pts.append((x, y))

    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    margin = params.plate_margin
    plate_w = (max_x - min_x) + 2 * margin
    plate_h = (max_y - min_y) + 2 * margin
    dx = -min_x + margin
    dy = -min_y + margin

    meshes = []
    if add_plate:
        meshes.append(make_plate(plate_w, plate_h, params.plate_thickness))
        z_base = params.plate_thickness
    else:
        z_base = 0.0
    for (x, y) in pts:
        meshes.append(make_dome(params, (x + dx, y + dy), z_base))

    combined = trimesh.util.concatenate(meshes)
    combined.merge_vertices()
    export_stl(combined, stl_out)
    if verbose:
        print(f"STL: {stl_out} | V={len(combined.vertices)} F={len(combined.faces)} watertight={combined.is_watertight}")
    return combined


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('svg')
    ap.add_argument('stl')
    ap.add_argument('--scale', type=float, default=1.0)
    ap.add_argument('--no-flip-y', action='store_true')
    ap.add_argument('--no-plate', action='store_true')
    ap.add_argument('--full-hemisphere', action='store_true')
    args = ap.parse_args()
    p = BrailleParams(full_hemisphere=args.full_hemisphere)
    svg_to_braille_stl(args.svg, args.stl, p, args.scale,
                       not args.no_flip_y, not args.no_plate)


if __name__ == '__main__':
    main()
