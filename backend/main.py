from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
import models, database
from routers import auth, properties, visits, reports, statistics

# IMPORTANT: Ensure database tables are created
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(
    title="Real Estate Automation API",
    description="Professional Modular Backend for Real Estate Automation",
    version="2.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for seeded property images
static_path = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_path):
    app.mount("/static", StaticFiles(directory=static_path), name="static")

# Register Routers
# Note: prefix="" is used to allow routers to define their own full literal paths
# which ensures 1:1 parity with the original monolithic URL structure.
app.include_router(auth.router)
app.include_router(properties.router)
app.include_router(visits.router)
app.include_router(reports.router)
app.include_router(statistics.router)

@app.get("/")
async def root():
    return {
        "status": "online",
        "message": "Modular Real Estate API is running with 1:1 Parity",
        "version": "2.0.0"
    }