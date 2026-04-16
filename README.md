# 📊 Data Day 2026 — Île-de-France Mobilités

Ressources et outils développés pour le **Data Day 2026** par le département Data d'Île-de-France Mobilités.

---

## 📁 Structure du projet

### `onyxia/`

Notebook Jupyter destiné à être exécuté sur la plateforme **Onyxia (SSP Cloud)**.

- **`etl_and_visualize.ipynb`** — Tutoriel pas à pas :
  1. **Chargement** des données d'offre théorique depuis le Datalake Azure (Parquet)
  2. **Filtrage et transformation** (période, mode de transport, colonnes utiles)
  3. **Sauvegarde** dans un bucket MinIO (S3-compatible)
  4. **Visualisation** interactive avec Plotly

### `scrap_and_track/`

Application **Streamlit** de web-scraping et génération de fiches récapitulatives via **Azure AI Foundry**.

- **`app.py`** — Application principale (*WebDigest*) : scrape une page web et produit une fiche de synthèse grâce à un modèle GPT (Azure OpenAI)
- **`requirements.txt`** — Dépendances Python : `streamlit`, `requests`, `beautifulsoup4`, `openai`, `markdown2`, `weasyprint`

---

## 🚀 Démarrage rapide

```bash
# scrap_and_track
cd scrap_and_track
pip install -r requirements.txt
streamlit run app.py
```

Variables d'environnement requises pour `scrap_and_track` :

| Variable | Description |
|---|---|
| `AZURE_AI_ENDPOINT` | Endpoint Azure OpenAI |
| `AZURE_AI_API_KEY` | Clé d'accès Azure AI Foundry |
| `AZURE_AI_MODEL` | Nom du déploiement (défaut : `gpt-4o`) |

---

## 📬 Contact

- **Ugo Demy** – DNUM / DATA&IA
- **Département Data** – Île-de-France Mobilités