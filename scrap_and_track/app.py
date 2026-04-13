"""
WebScraper + Fiche Récap — Application Streamlit
Prérequis : pip install streamlit requests beautifulsoup4 openai markdown2 weasyprint
Lancement  : streamlit run app.py

Variables d'environnement requises :
  AZURE_AI_ENDPOINT  — ex: https://<resource>.openai.azure.com/
  AZURE_AI_API_KEY   — clé d'accès Azure AI Foundry
  AZURE_AI_MODEL     — nom du déploiement (ex: gpt-4o) — optionnel, défaut: gpt-4o
"""

import os
import io
import streamlit as st
import requests
from bs4 import BeautifulSoup
from openai import AzureOpenAI
import markdown2

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="WebDigest",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Mono:wght@400;500&family=DM+Sans:wght@300;400;500&display=swap');

:root {
    --ink:       #1a1a2e;
    --paper:     #f5f0e8;
    --accent:    #c84b31;
    --accent2:   #2d6a4f;
    --muted:     #7a7060;
    --border:    #d4c9b0;
    --card:      #fdfaf4;
}

html, body, [data-testid="stAppViewContainer"] {
    background-color: var(--paper) !important;
    font-family: 'DM Sans', sans-serif;
    color: var(--ink);
}

/* Header */
.wd-header {
    display: flex;
    align-items: baseline;
    gap: 12px;
    padding: 2rem 0 0.5rem;
    border-bottom: 2px solid var(--ink);
    margin-bottom: 2rem;
}
.wd-logo {
    font-family: 'DM Serif Display', serif;
    font-size: 2.6rem;
    color: var(--ink);
    letter-spacing: -1px;
    line-height: 1;
}
.wd-logo span { color: var(--accent); }
.wd-tagline {
    font-size: 0.85rem;
    color: var(--muted);
    font-style: italic;
    font-family: 'DM Serif Display', serif;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: transparent;
    border-bottom: 1px solid var(--border);
    gap: 0;
}
.stTabs [data-baseweb="tab"] {
    font-family: 'DM Mono', monospace;
    font-size: 0.78rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--muted);
    padding: 0.6rem 1.4rem;
    border: 1px solid transparent;
    border-bottom: none;
    border-radius: 4px 4px 0 0;
}
.stTabs [aria-selected="true"] {
    background: var(--card) !important;
    color: var(--ink) !important;
    border-color: var(--border) !important;
}

/* Cards */
.wd-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 1.5rem;
    margin-bottom: 1rem;
}

/* Buttons */
.stButton > button {
    background: var(--ink) !important;
    color: var(--paper) !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.78rem !important;
    letter-spacing: 0.06em !important;
    text-transform: uppercase !important;
    border: none !important;
    border-radius: 3px !important;
    padding: 0.55rem 1.4rem !important;
    transition: background 0.2s !important;
}
.stButton > button:hover {
    background: var(--accent) !important;
}

/* Download buttons */
.stDownloadButton > button {
    background: transparent !important;
    color: var(--accent2) !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.75rem !important;
    letter-spacing: 0.05em !important;
    text-transform: uppercase !important;
    border: 1px solid var(--accent2) !important;
    border-radius: 3px !important;
    padding: 0.45rem 1.1rem !important;
}
.stDownloadButton > button:hover {
    background: var(--accent2) !important;
    color: white !important;
}

/* Inputs */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    background: white !important;
    border: 1px solid var(--border) !important;
    border-radius: 4px !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.85rem !important;
    color: var(--ink) !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: var(--ink) !important;
    box-shadow: none !important;
}

/* File uploader */
[data-testid="stFileUploader"] {
    background: white;
    border: 1.5px dashed var(--border);
    border-radius: 6px;
    padding: 1rem;
}

/* Success / info / warning */
.stSuccess, .stInfo, .stWarning {
    border-radius: 4px !important;
    font-size: 0.85rem !important;
}

/* Result box */
.wd-result {
    background: white;
    border-left: 3px solid var(--accent);
    padding: 1.5rem 1.8rem;
    border-radius: 0 6px 6px 0;
    font-family: 'DM Sans', sans-serif;
    line-height: 1.7;
    font-size: 0.92rem;
}
.wd-result h1, .wd-result h2, .wd-result h3 {
    font-family: 'DM Serif Display', serif;
    color: var(--ink);
}
.wd-result h2 { border-bottom: 1px solid var(--border); padding-bottom: 0.3rem; }

/* Label */
label, .stLabel { font-size: 0.82rem !important; color: var(--muted) !important; }

/* Step badge */
.step-badge {
    display: inline-block;
    background: var(--ink);
    color: var(--paper);
    font-family: 'DM Mono', monospace;
    font-size: 0.7rem;
    letter-spacing: 0.05em;
    padding: 2px 8px;
    border-radius: 2px;
    margin-bottom: 0.6rem;
}
</style>
""",
    unsafe_allow_html=True,
)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown(
    """
<div class="wd-header">
    <div class="wd-logo">Web<span>Digest</span></div>
    <div class="wd-tagline">extrait · résume · éclaire</div>
</div>
""",
    unsafe_allow_html=True,
)

# ── Helpers ───────────────────────────────────────────────────────────────────


def scrape_url(url: str) -> tuple[str, str]:
    """Retourne (texte_extrait, titre_page)."""
    headers = {"User-Agent": "Mozilla/5.0 (compatible; WebDigest/1.0)"}
    resp = requests.get(url, headers=headers, timeout=15)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    # Supprimer scripts / styles
    for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
        tag.decompose()
    title = soup.title.string.strip() if soup.title else "page"
    text = soup.get_text(separator="\n", strip=True)
    # Dédoublonner les lignes vides
    lines = [line for line in text.splitlines() if line.strip()]
    return "\n".join(lines), title


def make_fiche(texts: list[str], extra_instructions: str = "") -> str:
    """Appelle Azure AI Foundry (API OpenAI) et retourne la fiche en Markdown."""
    endpoint = os.environ.get("AZURE_AI_ENDPOINT", "").rstrip("/")
    api_key = os.environ.get("AZURE_AI_API_KEY", "")
    model = os.environ.get("AZURE_AI_MODEL", "gpt-4o")

    if not endpoint:
        st.error("⚠️  Variable d'environnement AZURE_AI_ENDPOINT introuvable.")
        st.stop()
    if not api_key:
        st.error("⚠️  Variable d'environnement AZURE_AI_API_KEY introuvable.")
        st.stop()

    client = AzureOpenAI(
        azure_endpoint=endpoint,
        api_key=api_key,
        api_version="2024-12-01-preview",
    )

    combined = "\n\n---\n\n".join(texts)

    system_prompt = """Tu es un assistant spécialisé dans la synthèse de contenus.
Produis une fiche récapitulative claire, structurée et utile en Markdown.
La fiche doit contenir :
1. **Titre & contexte** : sujet principal, source(s), date si disponible
2. **Résumé exécutif** : 3-5 phrases essentielles
3. **Points clés** : liste hiérarchisée des idées importantes
4. **Concepts / termes importants** : mini-glossaire si pertinent
5. **Pistes pour aller plus loin** : questions ouvertes, sujets connexes, lectures suggérées
Utilise un langage précis, des titres Markdown (##), des listes à puces et du gras pour les termes importants.
Réponds UNIQUEMENT en Markdown, sans préambule ni conclusion.
Dans le cas où tu recevrais des instructions supplémentaires, cherche à tout prix à les satisfaire, quitte à adapter certaines parties du plan."""

    user_content = f"Voici le(s) contenu(s) à synthétiser :\n\n{combined}"
    if extra_instructions.strip():
        user_content += f"\n\nInstructions supplémentaires : {extra_instructions.strip()}"

    response = client.chat.completions.create(
        model=model,
        max_tokens=2048,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ],
    )
    return response.choices[0].message.content


def md_to_pdf_bytes(md_text: str) -> bytes:
    """Convertit Markdown → HTML → PDF (weasyprint)."""
    try:
        from weasyprint import HTML as WeasyHtml

        html_body = markdown2.markdown(md_text, extras=["fenced-code-blocks", "tables"])
        full_html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8">
<style>
  body {{ font-family: Georgia, serif; max-width: 760px; margin: 40px auto; color: #1a1a2e; line-height: 1.7; }}
  h1,h2,h3 {{ font-family: 'Palatino Linotype', serif; }}
  h2 {{ border-bottom: 1px solid #ccc; padding-bottom: 4px; }}
  code {{ background: #f0ede6; padding: 2px 5px; border-radius: 3px; font-size: 0.85em; }}
  ul {{ padding-left: 1.4em; }}
</style></head><body>{html_body}</body></html>"""
        buf = io.BytesIO()
        WeasyHtml(string=full_html).write_pdf(buf)
        return buf.getvalue()
    except ImportError:
        return None


# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2 = st.tabs(["  01 — Extraire une page web  ", "  02 — Générer une fiche récap  "])

# ════════════════════════════════════════════════════════════════════════════
# TAB 1 — SCRAPER
# ════════════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown('<div class="step-badge">ÉTAPE 1</div>', unsafe_allow_html=True)
    st.markdown("#### Extraire le texte d'une page web")

    url = st.text_input(
        "URL de la page",
        placeholder="https://fr.wikipedia.org/wiki/Machine_learning",
        label_visibility="visible",
    )

    btn_col, spacer_col = st.columns([1, 4])
    with btn_col:
        extract_clicked = st.button("Extraire →", use_container_width=True)

    if extract_clicked:
        if not url.strip():
            st.warning("Merci de saisir une URL.")
        else:
            with st.spinner("Téléchargement et extraction en cours…"):
                try:
                    page_text, page_title = scrape_url(url.strip())
                    slug = page_title[:40].replace(" ", "_").replace("/", "-")
                    filename = f"{slug}.txt"
                    st.success(f"✓ {len(page_text.splitlines())} lignes extraites — **{page_title}**")
                    st.markdown('<div class="wd-result">', unsafe_allow_html=True)
                    st.text_area(
                        "Aperçu (500 premiers caractères)",
                        page_text[:500] + ("…" if len(page_text) > 500 else ""),
                        height=160,
                        disabled=True,
                    )
                    st.markdown("</div>", unsafe_allow_html=True)
                    st.download_button(
                        label=f"⬇  Télécharger {filename}",
                        data=page_text.encode("utf-8"),
                        file_name=filename,
                        mime="text/plain",
                    )
                except Exception as e:
                    st.error(f"Erreur lors de l'extraction : {e}")

# ════════════════════════════════════════════════════════════════════════════
# TAB 2 — FICHE RÉCAP
# ════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown('<div class="step-badge">ÉTAPE 2</div>', unsafe_allow_html=True)
    st.markdown("#### Générer une fiche récapitulative")

    uploaded_files = st.file_uploader(
        "Importer un ou plusieurs fichiers .txt",
        type=["txt"],
        accept_multiple_files=True,
    )

    extra_instructions = st.text_area(
        "Instructions supplémentaires (optionnel)",
        placeholder="Ex : focus sur les aspects techniques, niveau débutant, insister sur les applications pratiques…",
        height=90,
    )

    btn_col, spacer_col = st.columns([1, 4])
    with btn_col:
        generate_clicked = st.button("Générer la fiche →", use_container_width=True)

    if generate_clicked:
        if not uploaded_files:
            st.warning("Merci d'importer au moins un fichier .txt.")
        else:
            texts = []
            for uploaded_file in uploaded_files:
                content = uploaded_file.read().decode("utf-8", errors="replace")
                texts.append(f"[Source : {uploaded_file.name}]\n\n{content}")
                uploaded_file.seek(0)

            with st.spinner("Analyse et synthèse en cours via LLM…"):
                try:
                    fiche_md = make_fiche(texts, extra_instructions)

                    st.success(f"✓ Fiche générée à partir de {len(uploaded_files)} fichier(s).")

                    # Affichage rendu
                    st.markdown("---")
                    st.markdown('<div class="wd-result">', unsafe_allow_html=True)
                    st.markdown(fiche_md)
                    st.markdown("</div>", unsafe_allow_html=True)

                    # Téléchargements
                    st.markdown("##### Télécharger la fiche")
                    col_dl_md, col_dl_html, col_dl_pdf = st.columns(3)

                    with col_dl_md:
                        st.download_button(
                            "⬇  Markdown (.md)",
                            data=fiche_md.encode("utf-8"),
                            file_name="fiche_recap.md",
                            mime="text/markdown",
                        )

                    with col_dl_html:
                        fiche_html_body = markdown2.markdown(
                            fiche_md, extras=["fenced-code-blocks", "tables"]
                        )
                        fiche_full_html = f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<style>body{{font-family:Georgia,serif;max-width:760px;margin:40px auto;color:#1a1a2e;line-height:1.7}}
h1,h2,h3{{font-family:'Palatino Linotype',serif}}h2{{border-bottom:1px solid #ccc;padding-bottom:4px}}</style>
</head><body>{fiche_html_body}</body></html>"""
                        st.download_button(
                            "⬇  HTML (.html)",
                            data=fiche_full_html.encode("utf-8"),
                            file_name="fiche_recap.html",
                            mime="text/html",
                        )

                    with col_dl_pdf:
                        pdf_bytes = md_to_pdf_bytes(fiche_md)
                        if pdf_bytes:
                            st.download_button(
                                "⬇  PDF (.pdf)",
                                data=pdf_bytes,
                                file_name="fiche_recap.pdf",
                                mime="application/pdf",
                            )
                        else:
                            st.caption("PDF indisponible — installez `weasyprint`")

                except Exception as e:
                    st.error(f"Erreur lors de la génération : {e}")

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<p style=\"font-family:'DM Mono',monospace;font-size:0.7rem;color:#aaa;text-align:center;\">"
    "WebDigest · propulsé par Azure AI Foundry &amp; BeautifulSoup</p>",
    unsafe_allow_html=True,
)
