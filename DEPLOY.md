# Deploy — passo a passo

Este guia explica como pôr o **Braille Dome** online numa URL pública,
para que professores e FabLabs em qualquer parte da Europa possam usar
sem instalar nada.

Recomendação: **começa pelo Render**. É gratuito, leva 10 minutos, e se
mais tarde quiseres mudar para outro lado o código fica igual.

---

## Passo 1 — Pôr no GitHub

### Se nunca usaste GitHub Desktop, esta é a forma mais simples

1. Descarrega o **GitHub Desktop**: https://desktop.github.com
2. Instala e faz login com a tua conta GitHub
3. Clica em **File → New repository...**
4. Preenche:
   - **Name:** `braille-dome`
   - **Description:** "3D-printable braille labels with rounded dots"
   - **Local path:** escolhe a pasta onde tens os ficheiros
   - **Initialize with README:** deixa em branco (nós já temos um)
5. Clica **Create repository**
6. Copia todos os ficheiros do Braille Dome para essa pasta (excepto a pasta `dist/`, `build/`, `__pycache__/`)
7. Volta ao GitHub Desktop. Vais ver os ficheiros listados em "Changes"
8. No fundo da janela, no campo "Summary", escreve `Initial commit`
9. Clica **Commit to main**
10. Em cima, clica **Publish repository**
11. **Importante:** desmarca a opção "Keep this code private" — o repositório tem de ser **público** para o Render funcionar gratuitamente
12. Clica **Publish repository**

✅ Pronto, o teu código está em `https://github.com/<O-TEU-NOME>/braille-dome`

### Alternativa: linha de comandos (se já usas Git)

```bash
cd braille_dome
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/<O-TEU-NOME>/braille-dome.git
git push -u origin main
```

---

## Passo 2 — Deploy no Render

1. Vai a **https://render.com** e cria conta (podes usar a conta GitHub)
2. No dashboard clica **+ New** → **Web Service**
3. Liga a tua conta GitHub se ainda não estiver ligada
4. Encontra o repositório **braille-dome** na lista e clica **Connect**
5. Preenche:
   - **Name:** `braille-dome` (vai aparecer no URL)
   - **Region:** Frankfurt (mais perto de Portugal)
   - **Branch:** `main`
   - **Runtime:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
   - **Plan:** **Free**
6. Clica **Create Web Service**
7. O Render vai começar a fazer build. Demora 3–8 minutos a primeira vez
8. Quando aparecer **Live** (ponto verde), o teu URL público estará pronto:
   `https://braille-dome.onrender.com` (ou parecido)

✅ A app está **online e acessível por qualquer pessoa no mundo**.

### Notas sobre o free tier

- A app "adormece" ao fim de 15 min sem uso. O primeiro acesso depois disso
  demora ~30s a acordar (o utilizador vê a página de loading do Render).
  Para uso esporádico em escolas, é aceitável.
- Se quiseres acordada permanentemente, há planos a partir de $7/mês.

---

## Passo 3 — Partilhar

Já podes:

- Mandar o link para a lista de FabLabs Portugal e Europa
- Pôr o link no site `buinho.pt`
- Mencionar em newsletters Erasmus+
- Adicionar à página do projecto Inclusively Wired (educação inclusiva)
- Documentar como recurso aberto na rede de escolas EIRA

---

## Passo 4 (opcional) — Usar domínio próprio

Quando quiseres mudar de `braille-dome.onrender.com` para algo como
`braille.buinho.pt`:

1. No painel do Render, na tua web service, vai a **Settings → Custom Domains**
2. Adiciona `braille.buinho.pt`
3. O Render dá-te um registo CNAME para configurar no DNS do `buinho.pt`
4. Adicionas o CNAME no painel DNS do registar do domínio
5. Em ~1h o domínio começa a apontar para a app

---

## Como actualizar

Sempre que mudares código:

**Com GitHub Desktop:** Commit + Push. O Render detecta e refaz deploy automaticamente.

**Com linha de comandos:**
```bash
git add .
git commit -m "descrição da mudança"
git push
```

---

*Buinho FabLab · Messejana · 2026*
