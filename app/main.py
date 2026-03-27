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

app = FastAPI(
    title="Desafio Dev - Sistema de Importação CNAB",
    description="""
    API para processamento de arquivos CNAB, persistência em PostgreSQL 
    e visualização de transações financeiras.
    
## Funcionalidades
    * **Autenticação**: Gerenciamento de acesso via OAuth2 com tokens JWT.
    * **Navegação**: Renderização de templates Jinja2 para Login e Dashboard (Home).
    * **Upload**: Processamento de arquivos de largura fixa com parse eficiente em memória.
    * **Listagem**: Recuperação de transações do banco de dados e retorno de fragmentos HTML (Partials).
    * **Segurança**: Proteção de rotas e integridade de dados com Rollback automático em caso de falha.
    """,
    version="1.0.0",
    contact={
        "name": "Gustavo Freitas",
        "url": "https://github.com/GustavoGGF",
    }
)
models.Base.metadata.create_all(bind=engine)
create_initial_user()

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

@app.get("/", tags=["Navegação"])
async def redirect_login_page(request: Request):
    return templates.TemplateResponse(
        request=request, 
        name="login.html", 
        context={}
    )

@app.get("/login", tags=["Navegação"])
async def login_page(request: Request):
    return templates.TemplateResponse(
        request=request, 
        name="login.html", 
        context={}
    )

@app.post("/auth", tags=["Autenticação"])
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Usuário ou senha incorretos")

    access_token = create_access_token(data={"sub": user.username})
    
    return{
        "access_token": access_token,
        "token_type": "bearer"
    }

@app.get("/home", tags=["Navegação"])
async def home(request: Request):
    return templates.TemplateResponse(
        request=request, 
        name="index.html", 
        context={}
    )

@app.post("/upload", tags=["Upload"])
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
    
@app.get("/get-list", tags=["Listagem"])
def get_all_info_database(request: Request, db: Session = Depends(get_db)):
    
    transaction_list = list(get_all_transactions(db))
    
    return templates.TemplateResponse(
        request, 
        "partials/table.html", 
        {"transacoes": transaction_list}
    )