import os
import re
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

SYSTEM_PROMPT = """Tu es un moteur de generation d'examens ministeriel quebecois pour eleves du primaire. Tu generes des evaluations originales inspirees des exemples fournis. Reponds UNIQUEMENT avec le JSON demande, sans texte avant ou apres.

FORMAT DE SORTIE :
{
  "examen": "contenu complet en markdown",
  "corrige": "corrige complet en markdown"
}

TYPES : MATH-QUESTIONNAIRE (15-20 QCM A/B/C/D), MATH-C1 (situation-probleme), MATH-C2 (raisonnement), LECTURE-NARRATIF (texte + questions), LECTURE-INFORMATIF (texte + questions).
DIFFICULTE 1-10 : 1-2 debut 5e, 3-4 milieu 6e, 5-6 standard ministeriel, 7-8 enrichi, 9-10 defi.
Utilise des contextes quebecois authentiques. Contenu 100% original a chaque generation."""

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
        raise HTTPException(status_code=400, detail="Difficulte doit etre entre 1 et 10")

    example = load_example(req.type_examen)
    example_section = ""
    if example:
        example_section = f"\n\nExemple de reference (NE PAS reproduire, style seulement) :\n{example}"

    user_message = f"""Genere un examen :
- Niveau : {req.niveau}
- Type : {req.type_examen}
- Difficulte : {req.difficulte}/10
{example_section}

Reponds UNIQUEMENT avec le JSON."""

    response = get_client().messages.create(
        model="claude-opus-4-5",
        max_tokens=4096,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}]
    )

    raw = response.content[0].text.strip()

    json_match = re.search(r'\{.*\}', raw, re.DOTALL)
    if json_match:
        raw = json_match.group(0)

    try:
        data = json.loads(raw)
        return {
            "examen": data.get("examen", ""),
            "corrige": data.get("corrige", ""),
        }
    except json.JSONDecodeError:
        return {
            "examen": raw,
            "corrige": "Corrige non disponible.",
        }


@app.post("/api/verify-password")
def verify_password(req: VerifyPasswordRequest):
    is_valid = hmac.compare_digest(req.password, PARENT_PASSWORD)
    return {"valid": is_valid}


@app.get("/health")
def health():
    return {"status": "ok"}


STATIC_DIR = Path(__file__).parent / "static"
if STATIC_DIR.exists():
    assets_dir = STATIC_DIR / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")

    @app.get("/{full_path:path}")
    def serve_frontend(full_path: str):
        return FileResponse(str(STATIC_DIR / "index.html"))