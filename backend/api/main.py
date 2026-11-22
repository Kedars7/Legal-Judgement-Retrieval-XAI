from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from api.search_service import LegalSearchService


# ============================================================
# APP
# ============================================================

app = FastAPI(
    title="Legal Judgment Retrieval API",
    description=(
        "Hybrid legal judgment retrieval with "
        "InLegalBERT, FAISS, BM25, Random Forest "
        "relevance scoring and SHAP explanations."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    # Vite may expose the frontend as localhost or 127.0.0.1, and may
    # choose another port when the default port is already in use.
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1)(:\d+)?$",
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# SEARCH SERVICE
# ============================================================

search_service = None


@app.on_event("startup")
def startup_event():

    global search_service

    print()
    print("=" * 80)
    print("STARTING LEGAL SEARCH API")
    print("=" * 80)

    search_service = LegalSearchService()

    print("=" * 80)
    print("LEGAL SEARCH API READY")
    print("=" * 80)


# ============================================================
# REQUEST MODEL
# ============================================================

class SearchRequest(BaseModel):

    query: str = Field(
        ...,
        min_length=3,
        description="Natural-language legal query",
    )

    top_k: int = Field(
        default=10,
        ge=1,
        le=20,
        description="Number of results to return",
    )


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/")
def root():

    return {
        "service": "Legal Judgment Retrieval API",
        "status": "running",
        "version": "1.0.0",
    }


@app.get("/health")
def health():

    return {
        "status": "healthy",
        "service": "legal-search",
    }


# ============================================================
# SEARCH ENDPOINT
# ============================================================

@app.post("/search")
def search(request: SearchRequest):

    if search_service is None:

        raise HTTPException(
            status_code=503,
            detail="Search service is not initialized.",
        )

    try:

        response = search_service.search(
            query=request.query,
            top_k=request.top_k,
        )

        return response

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    except Exception as exc:

        print(
            f"Search error: {exc}"
        )

        raise HTTPException(
            status_code=500,
            detail="Internal search error.",
        )