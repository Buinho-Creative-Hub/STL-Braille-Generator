"""
braille_dome.py v2
====================
Núcleo da geração de braille com pontos em calote esférica (dome).

Mudanças em relação à v1:
  • Substituído `trimesh.slice_plane` por construção directa em UV
    (latitude/longitude). Vantagens:
      - Não precisa de scipy
      - Não precisa de booleanas
      - Garantidamente estanque (watertight)
      - Garantidamente fechado (sem buracos no Tinkercad/slicers)

Norma: Marburg Medium
  Ø ponto = 1.5 mm   |   altura = 0.5 mm
  intra-célula = 2.5 mm   |   inter-célula = 6.0 mm   |   linhas = 10 mm

Buinho FabLab, Messejana
"""

from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np
import trimesh


# ---------------------------------------------------------------------------
# Parâmetros
# ---------------------------------------------------------------------------

@dataclass
class BrailleParams:
    dot_diameter: float = 1.5
    dot_height: float = 0.5
    dot_spacing: float = 2.5
    cell_spacing: float = 6.0
    line_spacing: float = 10.0

    plate_thickness: float = 1.5
    plate_margin: float = 5.0

    full_hemisphere: bool = False  # True => h = R = 0.75; False => h = 0.5
    n_lat: int = 12                # divisões em latitude (suavidade vertical)
    n_lon: int = 24                # divisões em longitude (suavidade horizontal)

    @property
    def dot_radius(self) -> float:
        return self.dot_diameter / 2.0

    @property
    def sphere_radius(self) -> float:
        return self.dot_radius

    @property
    def dome_actual_height(self) -> float:
        return self.sphere_radius if self.full_hemisphere else self.dot_height


# ---------------------------------------------------------------------------
# Tabela braille (PT)
# ---------------------------------------------------------------------------

_BRAILLE_BASE = {
    'a': (1,), 'b': (1, 2), 'c': (1, 4), 'd': (1, 4, 5), 'e': (1, 5),
    'f': (1, 2, 4), 'g': (1, 2, 4, 5), 'h': (1, 2, 5), 'i': (2, 4),
    'j': (2, 4, 5), 'k': (1, 3), 'l': (1, 2, 3), 'm': (1, 3, 4),
    'n': (1, 3, 4, 5), 'o': (1, 3, 5), 'p': (1, 2, 3, 4),
    'q': (1, 2, 3, 4, 5), 'r': (1, 2, 3, 5), 's': (2, 3, 4),
    't': (2, 3, 4, 5), 'u': (1, 3, 6), 'v': (1, 2, 3, 6),
    'w': (2, 4, 5, 6), 'x': (1, 3, 4, 6), 'y': (1, 3, 4, 5, 6),
    'z': (1, 3, 5, 6),
}

_BRAILLE_PT = {
    'á': (1, 2, 3, 5, 6), 'à': (1, 2, 3, 5, 6), 'â': (1, 6),
    'ã': (3, 4, 5), 'ç': (1, 2, 3, 4, 6), 'é': (1, 2, 3, 4, 5, 6),
    'ê': (1, 2, 6), 'í': (3, 4), 'ó': (3, 4, 6), 'ô': (1, 4, 5, 6),
    'õ': (2, 4, 6), 'ú': (2, 3, 4, 5, 6), 'ü': (1, 2, 5, 6),
}

_BRAILLE_PUNCT = {
    ' ': (), ',': (2,), ';': (2, 3), ':': (2, 5), '.': (2, 5, 6),
    '?': (2, 6), '!': (2, 3, 5), "'": (3,), '-': (3, 6),
    '"': (2, 3, 6), '(': (1, 2, 6), ')': (3, 4, 5), '/': (3, 4),
}

_BRAILLE_DIGITS = {
    '1': (1,), '2': (1, 2), '3': (1, 4), '4': (1, 4, 5), '5': (1, 5),
    '6': (1, 2, 4), '7': (1, 2, 4, 5), '8': (1, 2, 5), '9': (2, 4),
    '0': (2, 4, 5),
}

NUMBER_PREFIX = (3, 4, 5, 6)
CAPITAL_PREFIX = (4, 6)


def text_to_cells(text: str) -> list[tuple[int, ...]]:
    cells: list[tuple[int, ...]] = []
    in_number = False
    for ch in text:
        if ch.isdigit():
            if not in_number:
                cells.append(NUMBER_PREFIX)
                in_number = True
            cells.append(_BRAILLE_DIGITS[ch])
            continue
        in_number = False
        if ch.isupper():
            cells.append(CAPITAL_PREFIX)
            ch = ch.lower()
        if ch in _BRAILLE_BASE:
            cells.append(_BRAILLE_BASE[ch])
        elif ch in _BRAILLE_PT:
            cells.append(_BRAILLE_PT[ch])
        elif ch in _BRAILLE_PUNCT:
            cells.append(_BRAILLE_PUNCT[ch])
        else:
            cells.append(())
    return cells


# ---------------------------------------------------------------------------
# Geometria do dome — construção UV directa (sem slice_plane, sem scipy)
# ---------------------------------------------------------------------------

def _build_dome_mesh(R: float, h: float,
                     n_lat: int = 12, n_lon: int = 24) -> trimesh.Trimesh:
    """
    Constrói uma calote esférica como malha triangular fechada.

    R: raio da esfera de origem
    h: altura visível da calote (0 < h <= R)
    n_lat: anéis de latitude (do topo até à base)
    n_lon: divisões em longitude

    Retorna malha estanque com base plana em z=0 e topo em z=h.
    """
    h = min(h, R)
    cos_max = (R - h) / R
    theta_max = math.acos(max(-1.0, min(1.0, cos_max)))

    verts: list[list[float]] = [[0.0, 0.0, h]]   # 0: pólo

    # Anéis (i=1..n_lat); o anel n_lat fica no plano da base
    for i in range(1, n_lat + 1):
        theta = (i / n_lat) * theta_max
        z = R * math.cos(theta) - (R - h)
        r = R * math.sin(theta)
        # Garantir base exactamente em z=0
        if i == n_lat:
            z = 0.0
        for j in range(n_lon):
            phi = (j / n_lon) * 2.0 * math.pi
            verts.append([r * math.cos(phi), r * math.sin(phi), z])

    base_center = len(verts)
    verts.append([0.0, 0.0, 0.0])

    faces: list[list[int]] = []

    # Cap superior (pólo → primeiro anel)
    for j in range(n_lon):
        a = 1 + j
        b = 1 + ((j + 1) % n_lon)
        faces.append([0, b, a])  # normal para cima

    # Quads entre anéis (cada quad = 2 triângulos)
    for i in range(n_lat - 1):
        r0 = 1 + i * n_lon
        r1 = 1 + (i + 1) * n_lon
        for j in range(n_lon):
            a = r0 + j
            b = r0 + ((j + 1) % n_lon)
            c = r1 + j
            d = r1 + ((j + 1) % n_lon)
            faces.append([a, d, b])
            faces.append([a, c, d])

    # Cap inferior (último anel → centro da base, normal para baixo)
    last = 1 + (n_lat - 1) * n_lon
    for j in range(n_lon):
        a = last + j
        b = last + ((j + 1) % n_lon)
        faces.append([base_center, a, b])

    # process=False evita que o trimesh chame fix_normals (que requer networkx).
    # As faces já foram construídas com a orientação correcta (winding
    # consistente para fora) na construção UV acima.
    mesh = trimesh.Trimesh(
        vertices=np.asarray(verts, dtype=np.float64),
        faces=np.asarray(faces, dtype=np.int64),
        process=False,
    )
    return mesh


def make_dome(params: BrailleParams, center: tuple[float, float],
              z_base: float) -> trimesh.Trimesh:
    """Cria um dome no ponto (cx, cy), apoiado em z_base."""
    dome = _build_dome_mesh(
        R=params.sphere_radius,
        h=params.dome_actual_height,
        n_lat=params.n_lat,
        n_lon=params.n_lon,
    )
    cx, cy = center
    dome.apply_translation([cx, cy, z_base])
    return dome


def make_plate(width: float, height: float, thickness: float,
               origin: tuple[float, float] = (0.0, 0.0)) -> trimesh.Trimesh:
    box = trimesh.creation.box(extents=[width, height, thickness])
    ox, oy = origin
    box.apply_translation([ox + width / 2, oy + height / 2, thickness / 2])
    return box


def cell_dot_positions(cell: tuple[int, ...],
                       cell_origin: tuple[float, float],
                       params: BrailleParams) -> list[tuple[float, float]]:
    cx, cy = cell_origin
    s = params.dot_spacing
    layout = {1: (0, 0), 2: (0, -s), 3: (0, -2 * s),
              4: (s, 0), 5: (s, -s), 6: (s, -2 * s)}
    return [(cx + layout[d][0], cy + layout[d][1]) for d in cell]


def generate_braille_mesh(text: str,
                          params: BrailleParams | None = None,
                          line_break: str = '\n') -> trimesh.Trimesh:
    if params is None:
        params = BrailleParams()

    lines = text.split(line_break)
    cell_lines = [text_to_cells(line) for line in lines]
    max_cells = max((len(c) for c in cell_lines), default=0)
    n_lines = len(cell_lines)

    text_w = (max_cells - 1) * params.cell_spacing + params.dot_spacing if max_cells else 0
    text_h = (n_lines - 1) * params.line_spacing + 2 * params.dot_spacing if n_lines else 0
    plate_w = text_w + 2 * params.plate_margin
    plate_h = text_h + 2 * params.plate_margin

    meshes = [make_plate(plate_w, plate_h, params.plate_thickness)]
    z_top = params.plate_thickness

    for line_idx, cells in enumerate(cell_lines):
        line_y_top = (params.plate_margin + text_h
                      - line_idx * params.line_spacing - params.dot_spacing)
        for cell_idx, cell in enumerate(cells):
            cell_x = params.plate_margin + cell_idx * params.cell_spacing
            for (x, y) in cell_dot_positions(cell, (cell_x, line_y_top), params):
                meshes.append(make_dome(params, (x, y), z_top))

    combined = trimesh.util.concatenate(meshes)
    combined.merge_vertices()
    return combined


def export_stl(mesh: trimesh.Trimesh, path: str) -> None:
    mesh.export(path, file_type='stl')


if __name__ == '__main__':
    import sys
    txt = sys.argv[1] if len(sys.argv) > 1 else 'Buinho'
    out = sys.argv[2] if len(sys.argv) > 2 else 'test.stl'
    m = generate_braille_mesh(txt, BrailleParams())
    export_stl(m, out)
    print(f'OK: {out}')
    print(f'  V={len(m.vertices)}  F={len(m.faces)}')
    print(f'  watertight={m.is_watertight}')
    print(f'  bounds={m.bounds}')
