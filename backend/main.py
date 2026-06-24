from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import os

from backend.database.db import init_db
from backend.api.routes import (
    auth,
    predict,
    suppliers,
    planner,
    analytics,
    copilot,
    what_if,
    reports
)

# Initialize FastAPI App
app = FastAPI(
    title="Supply Chain delivery slippage Optimization Platform",
    description="Enterprise API for predicting construction material delivery risks, explaining drivers, and generating procurement planning insights.",
    version="1.0.0"
)

# Configure CORS Middleware
# Allows seamless cross-origin requests for local and production frontends
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Database and Seed Data on App Startup
@app.on_event("startup")
def on_startup():
    print("Starting up server...")
    try:
        init_db()
    except Exception as e:
        print(f"Error during database initialization: {e}")

# Include API Routers under /api prefix
app.include_router(auth.router, prefix="/api")
app.include_router(predict.router, prefix="/api")
app.include_router(suppliers.router, prefix="/api")
app.include_router(planner.router, prefix="/api")
app.include_router(analytics.router, prefix="/api")
app.include_router(copilot.router, prefix="/api")
app.include_router(what_if.router, prefix="/api")
app.include_router(reports.router, prefix="/api")

# Ensure static directory exists
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(STATIC_DIR, exist_ok=True)

# Mount static folder for loading CSS, JS and media files
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Serve the Single-Page Application (SPA) dashboard at the root URL
@app.get("/", response_class=HTMLResponse, tags=["Frontend SPA"])
async def serve_dashboard():
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            return f.read()
    return """
    <html>
        <head><title>Supply Chain Optimization Platform</title></head>
        <body style="font-family: sans-serif; padding: 50px; text-align: center; background-color: #0f172a; color: white;">
            <h1>Supply Chain Optimization Platform</h1>
            <p style="color: #94a3b8;">Local SPA dashboard index.html is being created. Please refresh in a moment.</p>
        </body>
    </html>
    """

if __name__ == "__main__":
    import uvicorn
    # Local execution helper
    port_num = int(os.getenv("PORT", 8050))
    print(f"Starting server on port {port_num}...")
    uvicorn.run("main:app", host="127.0.0.1", port=port_num, reload=True)
