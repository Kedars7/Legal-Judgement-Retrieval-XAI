# Legal Judgment Research AI

Legal Judgment Research AI is a full-stack application for searching and exploring Indian Supreme Court judgments using hybrid retrieval and explainable relevance ranking.

The project combines dense semantic search, BM25 lexical search, reciprocal rank fusion, judgment-level diversification, and retrieval explanations. A React interface provides staged search feedback, ranked results, and detailed judgment explanations.

## Features

- Natural-language legal search
- Hybrid retrieval using InLegalBERT embeddings and BM25
- Reciprocal Rank Fusion (RRF) with judgment diversification
- Relevance explanations for retrieved candidates
- Judgment details and source metadata
- Mock search mode for frontend development
- FastAPI backend with health and search endpoints
- Responsive React interface built with Vite and Tailwind CSS

## Technology Stack

### Frontend

- React 18
- Vite 5
- React Router
- Tailwind CSS
- Framer Motion
- Lucide React

### Backend

- Python
- FastAPI
- Uvicorn
- InLegalBERT / Sentence Transformers
- FAISS
- BM25
- PyTorch
- Scikit-learn

## Project Structure

```text
.
|-- backend/
|   |-- api/
|   |   |-- main.py
|   |   `-- search_service.py
|   |-- data/
|   |-- embeddings/
|   |-- index/
|   |-- ranking/
|   |-- scripts/
|   `-- requirements.txt
|-- frontend/
|   |-- src/
|   |-- .env.example
|   |-- package.json
|   `-- vite.config.js
|-- .gitignore
`-- README.md
```

## Prerequisites

- Python 3.11 or 3.12 recommended
- Node.js 18 or newer
- npm
- Generated backend data and retrieval artifacts

The backend loads FAISS, BM25, metadata, and model assets during startup. Run the project's data-processing and index-generation scripts if those artifacts are not already available.

## Backend Setup

From the project root:

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Start the API:

```powershell
uvicorn api.main:app --reload --host 127.0.0.1 --port 8000
```

The backend must be started from the `backend` directory so that local imports resolve correctly.

API endpoints:

- `GET /` - Service status
- `GET /health` - Health check
- `POST /search` - Judgment search

Example search request:

```json
{
  "query": "Article 14 discrimination and equality before law",
  "top_k": 10
}
```

Example request using PowerShell:

```powershell
Invoke-RestMethod -Method Post `
  -Uri "http://127.0.0.1:8000/search" `
  -ContentType "application/json" `
  -Body '{"query":"Article 14 equality before law","top_k":10}'
```

## Frontend Setup

From the project root:

```powershell
cd frontend
npm install
Copy-Item .env.example .env
npm run dev
```

Open the URL printed by Vite, normally `http://localhost:5173`.

## Environment Variables

Create `frontend/.env` from `.env.example`:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
VITE_USE_MOCK_DATA=false
```

- `VITE_API_BASE_URL`: FastAPI backend URL
- `VITE_USE_MOCK_DATA=false`: Calls the real backend
- `VITE_USE_MOCK_DATA=true`: Uses local mock search results

When the variable is omitted, frontend mock mode is enabled by default.

## Frontend Commands

```powershell
npm run dev
npm run build
npm run preview
```

## How It Works

1. The user submits a natural-language legal query.
2. The backend creates a dense InLegalBERT embedding and retrieves candidates from FAISS.
3. BM25 retrieves lexical candidates.
4. Reciprocal Rank Fusion combines both retrieval lists.
5. Results are diversified to limit repeated chunks from the same judgment.
6. Feature extraction and the retrieval explanation engine produce ranked, explainable results.
7. The React frontend displays the ranked judgments and supporting details.

## Data and Generated Files

The repository ignores virtual environments, environment files, frontend dependencies/build output, and generated retrieval artifacts. Common generated locations include:

- `backend/data/`
- `backend/embeddings/`
- `backend/index/`
- `backend/ranking/models/`

Do not commit credentials or private source documents.
