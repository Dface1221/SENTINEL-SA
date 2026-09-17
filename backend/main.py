import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import init_db
from .api.routes import router

app = FastAPI(
    title="NCIIPC SAT-SA: Supervisory Analytics Tool for SOC Assessment",
    description="Supervisory analytics platform for evaluating periodic SOC submissions from Critical Sector Entities (CSEs).",
    version="1.0.0"
)

# Enable CORS for local Vite frontend dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database tables on startup
@app.on_event("startup")
def on_startup():
    init_db()

# Mount API routes
app.include_router(router)

# Mount compiled static frontend for standalone single-process operation
frontend_dist = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend", "dist"))
if os.path.exists(frontend_dist):
    from fastapi.staticfiles import StaticFiles
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="static_frontend")
else:
    @app.get("/")
    def root():
        return {
            "system": "NCIIPC SAT-SA",
            "role": "Supervisory Analytics Tool for SOC Assessment",
            "mandate": "National Critical Information Infrastructure Protection Centre",
            "status": "Operational (Offline Local Mode)",
            "docs_url": "/docs"
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)
