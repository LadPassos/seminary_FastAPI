from fastapi import APIRouter, Depends, Request, Form, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from models import User
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from hashlib import sha256

router = APIRouter()
templates = Jinja2Templates(directory="templates")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Página inicial
@router.get("/")
def index(request: Request, db: Session = Depends(get_db)):
    users = db.query(User).all()
    return templates.TemplateResponse("index.html", {"request": request, "users": users})

# Registrar usuário
@router.get("/register")
def register_form(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@router.post("/register")
def register_user(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    hashed_password = sha256(password.encode()).hexdigest()
    user = User(name=name, email=email, password=hashed_password)
    db.add(user)
    db.commit()
    return RedirectResponse("/", status_code=303)

# Login
@router.get("/login")
def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/login")
def login_user(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    hashed_password = sha256(password.encode()).hexdigest()
    user = db.query(User).filter(User.email == email, User.password == hashed_password).first()
    if not user:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    return RedirectResponse("/", status_code=303)

# Editar usuário
@router.get("/edit/{user_id}")
def edit_user_form(user_id: int, request: Request, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    return templates.TemplateResponse("edit_user.html", {"request": request, "user": user})

@router.post("/edit/{user_id}")
def edit_user(
    user_id: int,
    name: str = Form(...),
    email: str = Form(...),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == user_id).first()
    user.name = name
    user.email = email
    db.commit()
    return RedirectResponse("/", status_code=303)

# Excluir usuário
@router.get("/delete/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    db.delete(user)
    db.commit()
    return RedirectResponse("/", status_code=303)