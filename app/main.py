from fastapi import FastAPI, File, UploadFile, Request, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from .database import get_db, engine
from . import models
from fastapi.security import OAuth2PasswordRequestForm
from .auth import verify_password, create_access_token
from .setup import create_initial_user
from .parser import parse_cnab_stream
from .queries import post_all_transactions, get_all_transactions
from fastapi.responses import JSONResponse

app = FastAPI()
models.Base.metadata.create_all(bind=engine)
create_initial_user()

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

@app.get("/")
async def redirect_login_page(request: Request):
    return templates.TemplateResponse(
        request=request, 
        name="login.html", 
        context={}
    )

@app.get("/login")
async def login_page(request: Request):
    return templates.TemplateResponse(
        request=request, 
        name="login.html", 
        context={}
    )

@app.post("/auth")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Usuário ou senha incorretos")

    access_token = create_access_token(data={"sub": user.username})
    
    return{
        "access_token": access_token,
        "token_type": "bearer"
    }

@app.get("/home")
async def home(request: Request):
    return templates.TemplateResponse(
        request=request, 
        name="index.html", 
        context={}
    )

@app.post("/upload")
async def upload_cnab(
    request: Request,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)):
    
    transactions = parse_cnab_stream(file.file)
    
    try:
        post_all_transactions(db, transactions)
        return JSONResponse(
            content="<div class='alert success'>Arquivo processado com sucesso!</div>",
            status_code=200
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Erro no processamento: {str(e)}"
        )
    
@app.get("/get-list")
def get_all_info_database(request: Request, db: Session = Depends(get_db)):
    
    transaction_list = list(get_all_transactions(db))
    
    return templates.TemplateResponse(
        request, 
        "partials/table.html", 
        {"transacoes": transaction_list}
    )