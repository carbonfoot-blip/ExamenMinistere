import os
import json
import hmac
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from anthropic import Anthropic

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_client():
    return Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
EXAMPLES_DIR = Path(__file__).parent / "examples"
PARENT_PASSWORD = os.environ.get("PARENT_PASSWORD", "changeme123")

SYSTEM_PROMPT = """Tu es un moteur de génération d'examens et de questionnaires ministériels québécois pour élèves du primaire.

Tu génères des évaluations authentiques, adaptées au niveau scolaire et à la difficulté demandée, en t'inspirant d'exemples fournis pour reproduire le style, la structure et la complexité — mais en produisant du contenu entièrement original à chaque génération.

Tu ne répètes jamais exactement un exemple fourni. Les exemples servent uniquement de modèles stylistiques et de calibrage de complexité.

NIVEAUX : Primaire 6e année (seul niveau actif).

TYPES D'EXAMENS pour Primaire 6e :
- MATH-QUESTIONNAIRE : 15-20 questions à choix multiples (A/B/C/D) couvrant : calcul, géométrie, mesure, fractions/décimaux, probabilité, statistiques, algèbre, puissances. Contextes réalistes québécois. Chaque question : contexte en texte normal, question en gras, 4 choix.
- MATH-C1 : Situation-problème complète avec contexte réaliste, données nécessaires, 1-2 questions guidantes, consigne de démarche.
- MATH-C2 : Concept ou régularité à analyser, justifier ou compléter. Suite/tableau/figure. Questions courtes avec justification.
- LECTURE-NARRATIF : Texte narratif original (personnages, intrigue, lieu québécois) + 8-12 questions variées.
- LECTURE-INFORMATIF : Texte informatif (sciences, société, nature, histoire du Québec) + 8-12 questions variées.

DIFFICULTÉ (1-10) :
1-2 : Niveau début 5e. Opérations simples, textes ~100 mots, questions littérales.
3-4 : Niveau milieu 6e. Multi-étapes, textes ~150 mots, inférences simples.
5-6 : Niveau fin 6e (standard ministériel). Problèmes complexes, textes ~200 mots, raisonnement requis.
7-8 : Niveau enrichi. Abstraction, justification écrite, textes ~250 mots.
9-10 : Niveau défi. Situations inédites, textes ~300 mots, questions ouvertes exigeantes.

FORMAT DE SORTIE — réponds UNIQUEMENT avec ce JSON (aucun texte avant ou après) :
{
  "examen": "contenu complet de l'examen en markdown, prêt à afficher",
  "corrige": "corrigé complet avec réponses, démarches et barème en markdown"
}

RÈGLES :
- Contenu 100% original à chaque génération
- Français québécois standard (terminologie MEQ)
- Contextes culturellement pertinents (noms, lieux québécois)
- Cohérence de difficulté du début à la fin
- Pour LECTURE : texte complet et autonome, pas un résumé
- Toutes les questions ont exactement une réponse correcte (ou réponses clairement acceptables pour questions ouvertes)
- Pour MATH-QUESTIONNAIRE : format identique à l'exemple fourni (Question X en gras, contexte, question en gras, choix A/B/C/D)
"""

EXAM_TYPES = {
    "Primaire 6e": [
        "MATH-QUESTIONNAIRE",
        "MATH-C1",
        "MATH-C2",
        "LECTURE-NARRATIF",
        "LECTURE-INFORMATIF"
    ]
}

EXAMPLE_FILES = {
    "MATH-QUESTIONNAIRE": "math-questionnaire.json",
    "LECTURE-NARRATIF": "lecture-narratif.json",
}


class GenerateRequest(BaseModel):
    niveau: str
    type_examen: str
    difficulte: int


class VerifyPasswordRequest(BaseModel):
    password: str


def load_example(type_examen: str) -> str:
    filename = EXAMPLE_FILES.get(type_examen)
    if not filename:
        return ""
    path = EXAMPLES_DIR / filename
    if not path.exists():
        return ""
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return json.dumps(data, ensure_ascii=False, indent=2)


@app.get("/api/config")
def get_config():
    return {"exam_types": EXAM_TYPES}


@app.post("/api/generate")
def generate_exam(req: GenerateRequest):
    if req.difficulte < 1 or req.difficulte > 10:
        raise HTTPException(status_code=400, detail="Difficulté doit être entre 1 et 10")

    example = load_example(req.type_examen)
    example_section = ""
    if example:
        example_section = f"\n\nVoici un exemple de référence pour le style et la structure (NE PAS reproduire, s'en inspirer uniquement) :\n{example}"

    user_message = f"""Génère un examen avec ces paramètres :
- Niveau : {req.niveau}
- Type : {req.type_examen}
- Difficulté : {req.difficulte}/10
{example_section}

Réponds UNIQUEMENT avec le JSON demandé."""

    response = get_client().messages.create(
        model="claude-opus-4-5",
        max_tokens=4096,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}]
    )

    raw = response.content[0].text.strip()

    # Nettoyer les balises markdown si présentes
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1]
        if raw.endswith("```"):
            raw = raw.rsplit("```", 1)[0]

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Erreur de génération — réponse invalide")

    return {
        "examen": data.get("examen", ""),
        "corrige": data.get("corrige", ""),
    }


@app.post("/api/verify-password")
def verify_password(req: VerifyPasswordRequest):
    is_valid = hmac.compare_digest(req.password, PARENT_PASSWORD)
    return {"valid": is_valid}


@app.get("/health")
def health():
    return {"status": "ok"}

# Servir le frontend React (doit être en dernier)
STATIC_DIR = Path(__file__).parent / "static"
if STATIC_DIR.exists():
    assets_dir = STATIC_DIR / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")

    @app.get("/{full_path:path}")
    def serve_frontend(full_path: str):
        return FileResponse(str(STATIC_DIR / "index.html"))
