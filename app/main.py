from fastapi import FastAPI, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import Base, engine, get_db
from app.routers import auth as auth_router
from app.routers import movies as movies_router
from app.routers import ratings as ratings_router
from app.routers import recommendations as rec_router
from app.routers import metrics as metrics_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Movie Recommendation Web App", version="1.0.0")
app.include_router(auth_router.router)
app.include_router(movies_router.router)
app.include_router(ratings_router.router)
app.include_router(rec_router.router)
app.include_router(metrics_router.router)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# -------- Minimal UI --------

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

@app.get("/my-ratings", response_class=HTMLResponse)
def my_ratings_page(request: Request):
    return templates.TemplateResponse("my_ratings.html", {"request": request})

@app.get("/recommendations", response_class=HTMLResponse)
def recommendations_page(request: Request):
    return templates.TemplateResponse("recommendations.html", {"request": request})

@app.get("/analytics", response_class=HTMLResponse)
def analytics_page(request: Request):
    return templates.TemplateResponse("analytics.html", {"request": request})
