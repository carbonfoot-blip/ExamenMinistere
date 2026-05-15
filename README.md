# Générateur d'examens ministériels — Primaire 6e

Application web propulsée par l'IA pour générer des examens de style ministériel québécois.

## Stack
- **Backend** : Python / FastAPI
- **Frontend** : React / Vite
- **IA** : API Anthropic (Claude)
- **Hébergement** : Railway

## Variables d'environnement (Railway)
| Variable | Description |
|---|---|
| `ANTHROPIC_API_KEY` | Clé API Anthropic |
| `PARENT_PASSWORD` | Mot de passe pour accéder au corrigé |

## Développement local

### Backend
```bash
cd backend
pip install -r requirements.txt
ANTHROPIC_API_KEY=sk-... PARENT_PASSWORD=monmotdepasse uvicorn main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Ajouter des exemples
Placer les fichiers JSON dans `backend/examples/` :
- `math-questionnaire.json`
- `math-c1.json`
- `math-c2.json`
- `lecture-narratif.json`
- `lecture-informatif.json`
 
