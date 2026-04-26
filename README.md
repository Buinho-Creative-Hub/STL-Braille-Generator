# Braille Dome

**3D-printable braille labels with rounded dots — for inclusive education.**

[![License: CC BY-SA 4.0](https://img.shields.io/badge/License-CC--BY--SA_4.0-2038A6.svg)](https://creativecommons.org/licenses/by-sa/4.0/)

---

## English

The Tinkercad braille generator is widely used in schools to 3D-print tactile labels for visually impaired students — but it produces dots as **flat-topped cylinders**, leaving sharp edges that can hurt children's hands.

**Braille Dome** generates the same braille, but with **spherical caps** (rounded domes) on top — gentle to the touch, while keeping the dimensional standard.

It's a small Python web app you can run locally or host online for your school network. Built by **[Buinho FabLab](https://buinho.pt)** in Messejana, Alentejo, Portugal, for the European inclusive-education community.

### Features

- **Text → STL**: type a label, get a printable file. Supports Portuguese accents, numbers, capital prefixes.
- **Tinkercad SVG → STL**: drop an existing braille SVG and get a properly rounded version.
- **Marburg Medium standard**: Ø 1.5 mm dots, 0.5 mm height, 2.5/6.0/10.0 mm spacing.
- **No external dependencies on slicers or paid software.**
- **Bilingual interface (PT/EN).**

### Quick start (local)

```bash
git clone https://github.com/YOUR-USER/braille-dome
cd braille-dome
pip install -r requirements.txt
python app.py
# open http://127.0.0.1:5000
```

### Deploy online

The app is deploy-ready for **Render**, **Railway**, **Fly.io**, or any host with Python + a `Procfile`.

**Render (free tier):**
1. Fork this repo on GitHub
2. Go to [render.com](https://render.com) → New → Web Service → connect your fork
3. Build: `pip install -r requirements.txt` · Start: `gunicorn app:app`
4. Done — you get a public URL like `https://braille-dome.onrender.com`

### Use cases

- Classroom labels (desks, drawers, equipment)
- Inclusive maker workshops
- AT (assistive technology) demonstrations
- Student-led activities — students generate their own labels

---

## Português

O gerador de braille do Tinkercad é muito usado nas escolas para imprimir etiquetas táteis em 3D para alunos invisuais — mas gera os pontos como **cilindros de topo plano**, deixando arestas vivas que magoam as mãos das crianças.

O **Braille Dome** gera o mesmo braille mas com **calotes esféricas** no topo — suaves ao tato, mantendo a norma dimensional.

É uma pequena app web em Python que podes correr localmente ou alojar online para a rede da tua escola. Feito pelo **[Buinho FabLab](https://buinho.pt)** em Messejana, Alentejo, para a comunidade europeia de educação inclusiva.

### Funcionalidades

- **Texto → STL**: escreves a etiqueta, descarregas o ficheiro pronto a imprimir. Suporta acentos portugueses, números, prefixo de maiúscula.
- **SVG do Tinkercad → STL**: largas um SVG braille existente e recebes a versão arredondada.
- **Norma Marburg Medium**: Ø 1.5 mm, altura 0.5 mm, espaçamentos 2.5/6.0/10.0 mm.
- **Sem dependência de slicers ou software pago.**
- **Interface bilingue (PT/EN).**

### Como começar (local)

```bash
git clone https://github.com/YOUR-USER/braille-dome
cd braille-dome
pip install -r requirements.txt
python app.py
# abre http://127.0.0.1:5000
```

### Pôr online

Está pronto para deploy em **Render**, **Railway**, **Fly.io** ou qualquer alojamento Python com `Procfile`.

**Render (free tier):**
1. Faz fork deste repo no GitHub
2. Vai a [render.com](https://render.com) → New → Web Service → liga ao teu fork
3. Build: `pip install -r requirements.txt` · Start: `gunicorn app:app`
4. Pronto — recebes URL pública tipo `https://braille-dome.onrender.com`

---

## Technical notes

- Geometry built directly in UV (latitude/longitude), no boolean operations needed.
- Pure Python: numpy + trimesh. No CAD kernel, no scipy.
- Each dome: 290 vertices, 576 faces, watertight.
- Output STLs are watertight and slicer-friendly.
- Default cap geometry: spherical cap with R=0.75 mm and visible height = 0.5 mm (Marburg standard). Optional full hemisphere mode (h = R = 0.75 mm).

---

## License

[CC-BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) — free to use, modify and redistribute, as long as you credit Buinho FabLab and share derivatives under the same license.

If you build on this for your own school network or FabLab, we'd love to hear about it: **info@buinho.pt** · [@buinhofablab](https://instagram.com/buinhofablab)

---

*Buinho FabLab · Messejana, Alentejo · 2026*
