"""
app.py — Braille Dome
======================
Interface web bilingue (PT/EN) para gerar STL braille com pontos
arredondados, em vez dos cilindros de topo plano do Tinkercad.

Buinho FabLab · Messejana, Alentejo
Licença: CC-BY-SA 4.0
"""

from __future__ import annotations

import io
import os
import tempfile
from pathlib import Path

from flask import Flask, render_template_string, request, send_file, abort

from braille_dome import BrailleParams, generate_braille_mesh
from svg_to_stl import svg_to_braille_stl


app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 4 * 1024 * 1024  # 4 MB


INDEX_HTML = r"""
<!doctype html>
<html lang="pt">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Braille Dome — Buinho FabLab</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Asap:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
  :root {
    --creme: #FAF0E1;
    --azul: #2038A6;
    --laranja: #FA6415;
    --vermelho: #F23A2F;
    --amarelo: #FCB515;
    --cinza: #6b6354;
  }
  * { box-sizing: border-box; }
  html, body { margin: 0; padding: 0; }
  body {
    font-family: 'Asap', system-ui, sans-serif;
    background: var(--creme);
    color: #1a1a1a;
    line-height: 1.5;
  }
  .wrap { max-width: 820px; margin: 0 auto; padding: 2rem 1.5rem 4rem; }

  /* Header */
  header { display: flex; justify-content: space-between; align-items: baseline; flex-wrap: wrap; gap: 1rem; }
  .brand { font-size: 1.1rem; font-weight: 700; color: var(--azul); letter-spacing: -0.01em; }
  .brand span.educ { color: var(--laranja); font-weight: 500; }
  .lang {
    display: inline-flex; gap: 0; background: rgba(32, 56, 166, 0.08);
    border-radius: 100px; padding: 3px;
  }
  .lang button {
    background: none; border: none; padding: 5px 14px; border-radius: 100px;
    font-family: inherit; font-size: 0.85rem; cursor: pointer;
    color: var(--azul); font-weight: 500;
  }
  .lang button.active { background: var(--azul); color: var(--creme); }

  h1 {
    font-size: clamp(2.2rem, 5vw, 3.6rem);
    font-weight: 700; line-height: 1.05; margin: 2rem 0 0.6rem;
    color: var(--azul); letter-spacing: -0.02em;
  }
  .lede {
    font-size: 1.15rem; color: var(--cinza); max-width: 60ch;
    margin: 0 0 2rem;
  }

  /* Diagrama da diferença */
  .diff {
    display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;
    margin: 1.5rem 0 2.5rem;
  }
  .diff > div {
    background: rgba(255,255,255,0.5); border-radius: 12px;
    padding: 1rem; text-align: center;
  }
  .diff svg { width: 100%; max-width: 220px; height: auto; }
  .diff .lbl {
    display: block; font-size: 0.85rem; font-weight: 600;
    margin-top: 0.4rem; color: var(--azul);
  }
  .diff .bad .lbl { color: var(--vermelho); }
  .diff .bad span { color: var(--vermelho); }
  .diff .good .lbl { color: var(--azul); }

  /* Cards de formulário */
  .card {
    background: white; border-radius: 14px; padding: 1.6rem 1.8rem;
    margin: 1.2rem 0; box-shadow: 0 1px 3px rgba(32,56,166,0.08);
  }
  .card h2 {
    font-size: 1.4rem; font-weight: 600; color: var(--azul);
    margin: 0 0 0.3rem; display: flex; align-items: center; gap: 0.6rem;
  }
  .card h2 .num {
    display: inline-flex; width: 30px; height: 30px; border-radius: 6px;
    background: var(--laranja); color: white; align-items: center;
    justify-content: center; font-size: 1rem; font-weight: 700;
  }
  .card p.sub { color: var(--cinza); margin: 0 0 1.2rem; font-size: 0.95rem; }

  label {
    display: block; font-weight: 600; color: var(--azul);
    margin: 0.9rem 0 0.3rem; font-size: 0.9rem;
  }
  input[type=text], textarea, input[type=file], input[type=number] {
    width: 100%; padding: 0.6rem 0.8rem; border: 1.5px solid #ddd;
    border-radius: 6px; font-family: inherit; font-size: 1rem;
    background: white; transition: border-color 0.15s;
  }
  input:focus, textarea:focus {
    outline: none; border-color: var(--azul);
  }
  textarea { min-height: 90px; resize: vertical; }
  .row { display: flex; gap: 1rem; }
  .row > div { flex: 1; }
  .check { display: flex; align-items: flex-start; gap: 0.5rem; margin: 0.7rem 0; }
  .check input { width: auto; margin-top: 4px; }
  .check label { margin: 0; font-weight: 400; color: #333; font-size: 0.9rem; }

  button.go {
    background: var(--azul); color: white; border: none;
    padding: 0.8rem 1.6rem; border-radius: 6px; cursor: pointer;
    font-family: inherit; font-weight: 600; font-size: 1rem;
    margin-top: 1.2rem; transition: background 0.15s;
  }
  button.go:hover { background: #15267d; }

  /* Notas técnicas */
  details {
    background: white; border-radius: 12px; padding: 1rem 1.4rem;
    margin: 1rem 0; border-left: 4px solid var(--amarelo);
  }
  details summary {
    cursor: pointer; font-weight: 600; color: var(--azul); padding: 0.3rem 0;
  }
  details p, details ul { color: #333; font-size: 0.95rem; }
  details li { margin: 0.3rem 0; }

  footer {
    margin-top: 3rem; padding-top: 1.5rem;
    border-top: 1px solid rgba(32,56,166,0.15);
    font-size: 0.85rem; color: var(--cinza);
    display: flex; justify-content: space-between; flex-wrap: wrap; gap: 1rem;
  }
  footer a { color: var(--azul); text-decoration: none; font-weight: 500; }
  footer a:hover { text-decoration: underline; }

  /* Toggle de idioma — controlado via classes .hidden-lang adicionadas pelo JS */
  .hidden-lang { display: none !important; }
</style>
</head>
<body>
<div class="wrap">

<header>
  <div class="brand">Buinho<span class="educ"> · educativo</span></div>
  <div class="lang">
    <button id="lang-pt" class="active" onclick="setLang('pt')">PT</button>
    <button id="lang-en" onclick="setLang('en')">EN</button>
  </div>
</header>

<h1>
  <span class="pt">Braille Dome</span>
  <span class="en hidden-lang">Braille Dome</span>
</h1>

<p class="lede">
  <span class="pt">
    Gerador de etiquetas braille em STL para impressão 3D, com pontos
    arredondados que não magoam ao tato. Para escolas, FabLabs e contextos
    de educação inclusiva.
  </span>
  <span class="en hidden-lang">
    STL generator for 3D-printed braille labels, with rounded dots that
    are gentle to the touch. For schools, FabLabs, and inclusive education.
  </span>
</p>

<!-- Diagrama secção transversal -->
<div class="diff">
  <div class="bad">
    <svg viewBox="0 0 120 60" xmlns="http://www.w3.org/2000/svg">
      <rect x="0" y="40" width="120" height="20" fill="#ddd" stroke="#888"/>
      <rect x="48" y="20" width="24" height="20" fill="#888" stroke="#000" stroke-width="1.2"/>
      <line x1="38" y1="14" x2="48" y2="20" stroke="#F23A2F" stroke-width="1.5" marker-end="url(#arr-r)"/>
      <line x1="82" y1="14" x2="72" y2="20" stroke="#F23A2F" stroke-width="1.5" marker-end="url(#arr-r)"/>
      <text x="34" y="11" font-size="6" fill="#F23A2F" text-anchor="end">!</text>
      <text x="86" y="11" font-size="6" fill="#F23A2F">!</text>
      <defs>
        <marker id="arr-r" markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto">
          <path d="M0,0 L6,3 L0,6 Z" fill="#F23A2F"/>
        </marker>
      </defs>
    </svg>
    <span class="lbl pt">Tinkercad: cilindro com aresta viva</span>
    <span class="lbl en hidden-lang">Tinkercad: cylinder with sharp edge</span>
  </div>
  <div class="good">
    <svg viewBox="0 0 120 60" xmlns="http://www.w3.org/2000/svg">
      <rect x="0" y="40" width="120" height="20" fill="#ddd" stroke="#888"/>
      <path d="M 47 40 A 13 13 0 0 1 73 40 Z" fill="#2038A6" stroke="#000" stroke-width="1.2"/>
    </svg>
    <span class="lbl pt">Braille Dome: calote arredondada</span>
    <span class="lbl en hidden-lang">Braille Dome: rounded dome</span>
  </div>
</div>

<!-- Texto -->
<div class="card">
  <form action="/from-text" method="post">
    <h2>
      <span class="num">1</span>
      <span class="pt">Gerar a partir de texto</span>
      <span class="en hidden-lang">Generate from text</span>
    </h2>
    <p class="sub">
      <span class="pt">Escreve o que queres em braille. Suporta acentos portugueses, números e maiúsculas.</span>
      <span class="en hidden-lang">Type what you want in braille. Supports accents, numbers and capitals.</span>
    </p>

    <label for="text">
      <span class="pt">Texto (uma ou mais linhas)</span>
      <span class="en hidden-lang">Text (one or more lines)</span>
    </label>
    <textarea name="text" id="text" required>Buinho FabLab</textarea>

    <div class="row">
      <div>
        <label for="margin">
          <span class="pt">Margem (mm)</span>
          <span class="en hidden-lang">Margin (mm)</span>
        </label>
        <input type="number" name="margin" id="margin" value="5" step="0.5" min="0" max="20">
      </div>
      <div>
        <label for="thickness">
          <span class="pt">Espessura da placa (mm)</span>
          <span class="en hidden-lang">Plate thickness (mm)</span>
        </label>
        <input type="number" name="thickness" id="thickness" value="1.5" step="0.1" min="0.5" max="10">
      </div>
    </div>

    <div class="check">
      <input type="checkbox" name="full_hemisphere" id="fh1">
      <label for="fh1">
        <span class="pt">Hemisfério completo (mais alto, 0.75 mm — fora da norma Marburg)</span>
        <span class="en hidden-lang">Full hemisphere (taller, 0.75 mm — outside Marburg norm)</span>
      </label>
    </div>

    <button type="submit" class="go">
      <span class="pt">Descarregar STL</span>
      <span class="en hidden-lang">Download STL</span>
    </button>
  </form>
</div>

<!-- SVG -->
<div class="card">
  <form action="/from-svg" method="post" enctype="multipart/form-data">
    <h2>
      <span class="num">2</span>
      <span class="pt">Converter SVG do Tinkercad</span>
      <span class="en hidden-lang">Convert Tinkercad SVG</span>
    </h2>
    <p class="sub">
      <span class="pt">Já tens um desenho no Tinkercad? Exporta como SVG e converte aqui.</span>
      <span class="en hidden-lang">Already have a Tinkercad design? Export as SVG and convert here.</span>
    </p>

    <label for="svg">
      <span class="pt">Ficheiro SVG</span>
      <span class="en hidden-lang">SVG file</span>
    </label>
    <input type="file" name="svg" id="svg" accept=".svg" required>

    <div class="row">
      <div>
        <label for="scale">
          <span class="pt">Escala</span>
          <span class="en hidden-lang">Scale</span>
        </label>
        <input type="number" name="scale" id="scale" value="1.0" step="0.01" min="0.01" max="100">
      </div>
      <div>
        <label for="thickness2">
          <span class="pt">Espessura da placa (mm)</span>
          <span class="en hidden-lang">Plate thickness (mm)</span>
        </label>
        <input type="number" name="thickness" id="thickness2" value="1.5" step="0.1" min="0.5" max="10">
      </div>
    </div>

    <div class="check">
      <input type="checkbox" name="no_plate" id="np">
      <label for="np">
        <span class="pt">Sem placa de suporte (só os domes)</span>
        <span class="en hidden-lang">No supporting plate (domes only)</span>
      </label>
    </div>

    <button type="submit" class="go">
      <span class="pt">Converter para STL</span>
      <span class="en hidden-lang">Convert to STL</span>
    </button>
  </form>
</div>

<details>
  <summary>
    <span class="pt">Notas técnicas e impressão 3D</span>
    <span class="en hidden-lang">Technical notes and 3D printing</span>
  </summary>
  <div class="pt">
    <ul>
      <li><strong>Norma:</strong> Marburg Medium — Ø 1.5 mm, altura 0.5 mm, espaçamento intra-célula 2.5 mm, inter-célula 6.0 mm, linhas 10.0 mm.</li>
      <li><strong>Geometria:</strong> calote esférica, base de raio ≈ 0.7 mm, topo perfeitamente arredondado. Sem arestas vivas.</li>
      <li><strong>Impressão:</strong> qualquer impressora FDM serve. Camadas de 0.1 mm dão resultado óptimo nos domes; 0.2 mm é suficiente.</li>
      <li><strong>Material:</strong> PLA padrão. PETG ou TPU também funcionam — TPU é particularmente confortável ao tato.</li>
      <li><strong>Suportes:</strong> não são necessários.</li>
      <li><strong>Acentos:</strong> á à â ã ç é ê í ó ô õ ú ü. Números são precedidos pelo prefixo numérico (3-4-5-6) automaticamente. Maiúsculas pelo prefixo (4-6).</li>
    </ul>
  </div>
  <div class="en hidden-lang">
    <ul>
      <li><strong>Standard:</strong> Marburg Medium — Ø 1.5 mm dot, 0.5 mm height, 2.5 mm intra-cell, 6.0 mm inter-cell, 10.0 mm line spacing.</li>
      <li><strong>Geometry:</strong> spherical cap, base radius ≈ 0.7 mm, perfectly rounded top. No sharp edges.</li>
      <li><strong>Printing:</strong> any FDM printer works. 0.1 mm layers are optimal for the domes; 0.2 mm is fine.</li>
      <li><strong>Material:</strong> standard PLA. PETG or TPU also work — TPU is especially gentle to the touch.</li>
      <li><strong>Supports:</strong> not needed.</li>
      <li><strong>Accents:</strong> Portuguese accents supported. Numbers automatically prefixed (3-4-5-6). Capitals prefixed (4-6).</li>
    </ul>
  </div>
</details>

<details>
  <summary>
    <span class="pt">Para professores: como usar na sala de aula</span>
    <span class="en hidden-lang">For teachers: classroom use</span>
  </summary>
  <div class="pt">
    <ol>
      <li>Escreve o nome do aluno, o conceito ou a etiqueta no formulário.</li>
      <li>Descarrega o ficheiro STL.</li>
      <li>Abre no slicer da impressora 3D (PrusaSlicer, Cura, Bambu Studio).</li>
      <li>Imprime. Demora 5–15 minutos para uma etiqueta pequena.</li>
      <li>Cola na carteira, na porta, na pasta — em qualquer sítio que precise de ser identificado tátilmente.</li>
    </ol>
    <p>Funciona bem como actividade pedagógica — os próprios alunos podem gerar e imprimir as etiquetas, o que torna o braille parte da experiência da turma toda.</p>
  </div>
  <div class="en hidden-lang">
    <ol>
      <li>Type the student's name, the concept, or the label.</li>
      <li>Download the STL file.</li>
      <li>Open in your 3D printer's slicer (PrusaSlicer, Cura, Bambu Studio).</li>
      <li>Print. Takes 5–15 minutes for a small label.</li>
      <li>Stick on desks, doors, folders — anywhere that needs to be identified by touch.</li>
    </ol>
    <p>Works well as a classroom activity — students can generate and print labels themselves, making braille part of the whole class experience.</p>
  </div>
</details>

<footer>
  <div>
    <span class="pt">Feito por <a href="https://buinho.pt" target="_blank">Buinho FabLab</a> · Messejana, Alentejo · Open-source CC-BY-SA 4.0</span>
    <span class="en hidden-lang">Built by <a href="https://buinho.pt" target="_blank">Buinho FabLab</a> · Messejana, Portugal · Open-source CC-BY-SA 4.0</span>
  </div>
  <div>
    <a href="https://github.com/" target="_blank">
      <span class="pt">Código fonte</span>
      <span class="en hidden-lang">Source code</span>
    </a>
  </div>
</footer>

</div>

<script>
function setLang(lang) {
  document.querySelectorAll('.pt, .en').forEach(el => {
    if (el.classList.contains(lang)) {
      el.classList.remove('hidden-lang');
    } else {
      el.classList.add('hidden-lang');
    }
  });
  document.getElementById('lang-pt').classList.toggle('active', lang === 'pt');
  document.getElementById('lang-en').classList.toggle('active', lang === 'en');
  document.documentElement.lang = lang;
  try { localStorage.setItem('braille_dome_lang', lang); } catch(e) {}
}
// Inicializa com PT (default) ou idioma guardado
let initialLang = 'pt';
try {
  const saved = localStorage.getItem('braille_dome_lang');
  if (saved === 'en' || saved === 'pt') initialLang = saved;
} catch(e) {}
setLang(initialLang);
</script>
</body>
</html>
"""


@app.route('/')
def index():
    return render_template_string(INDEX_HTML)


@app.route('/from-text', methods=['POST'])
def from_text():
    text = request.form.get('text', '').strip()
    if not text:
        abort(400, 'Texto vazio')

    params = BrailleParams(
        plate_margin=float(request.form.get('margin', 5)),
        plate_thickness=float(request.form.get('thickness', 1.5)),
        full_hemisphere=bool(request.form.get('full_hemisphere')),
    )
    mesh = generate_braille_mesh(text, params)
    buf = io.BytesIO()
    buf.write(mesh.export(file_type='stl'))
    buf.seek(0)
    safe = ''.join(c if c.isalnum() else '_' for c in text)[:30] or 'braille'
    return send_file(buf, mimetype='model/stl',
                     as_attachment=True,
                     download_name=f'{safe}.stl')


@app.route('/from-svg', methods=['POST'])
def from_svg():
    f = request.files.get('svg')
    if not f or not f.filename:
        abort(400, 'Falta o SVG')

    params = BrailleParams(
        plate_thickness=float(request.form.get('thickness', 1.5)),
        full_hemisphere=bool(request.form.get('full_hemisphere')),
    )

    with tempfile.TemporaryDirectory() as tmp:
        svg_path = Path(tmp) / 'in.svg'
        stl_path = Path(tmp) / 'out.stl'
        f.save(svg_path)

        svg_to_braille_stl(
            svg_path=str(svg_path),
            stl_out=str(stl_path),
            params=params,
            scale=float(request.form.get('scale', 1.0)),
            add_plate=not bool(request.form.get('no_plate')),
            verbose=False,
        )
        with open(stl_path, 'rb') as fh:
            data = fh.read()

    buf = io.BytesIO(data)
    base = Path(f.filename).stem
    return send_file(buf, mimetype='model/stl',
                     as_attachment=True,
                     download_name=f'{base}_dome.stl')


# Health check para Render/Railway/HF Spaces
@app.route('/health')
def health():
    return {'status': 'ok'}, 200


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
