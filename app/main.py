from datetime import date, time
from typing import BinaryIO, Generator
from fastapi import FastAPI, File, UploadFile, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from .schemas import TransacaoBase
from .database import get_db, engine
from itertools import islice
from .models import Transacao
from . import models

app = FastAPI()
models.Base.metadata.create_all(bind=engine)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

@app.get("/")
async def read_index(request: Request):
    return templates.TemplateResponse(
        request=request, 
        name="index.html", 
        context={}
    )
    
def parse_cnab_stream(file_buffer: BinaryIO) -> Generator[TransacaoBase, None, None]:
        for line_bytes in file_buffer:
            try:
                line = line_bytes.decode("utf-8")
                if not line.strip(): 
                    continue
                    
                ano, mes, dia = int(line[1:5]), int(line[5:7]), int(line[7:9])
                h, m, s = int(line[42:44]), int(line[44:46]), int(line[46:48])
                    
                yield TransacaoBase(
                    tipo=int(line[0:1]),
                    data=date(ano, mes, dia),
                    valor=int(line[9:19]) / 100.0,
                    cpf=line[19:30],
                    cartao=line[30:42],
                    hora=time(h, m, s),
                    dono_loja=line[48:62].strip(),
                    nome_loja=line[62:81].strip()
                )
                
            except (ValueError, IndexError) as e:
                print(f"Erro na linha {line_bytes}: Dado mal formatado. Menssagem de Erro: {e}")
                continue
        
def chunked_iterable(iterable: Generator[TransacaoBase, None, None], size: int):
    it = iter(iterable)
    while True:
        chunk = list(islice(it, size))
        if not chunk:
            break
        yield chunk
        
def db_connect(db: Session, gerador_transacoes: Generator[TransacaoBase, None, None]):    
    for batch in chunked_iterable(gerador_transacoes, 1000):
        # Converte o lote de Pydantic para SQLAlchemy Models
        db_batch = [
            Transacao(**t.model_dump()) 
            for t in batch
        ]
        db.add_all(db_batch)
        db.commit() # Commita o lote atual
            
    return db.query(Transacao).all()

@app.post("/upload")
async def upload_cnab(
    request: Request, 
    file: UploadFile = File(...), 
    db: Session = Depends(get_db)):
    
    gerador_transacoes = parse_cnab_stream(file.file)
    
    lista_transacoes = list(db_connect(db, gerador_transacoes))
            
    return templates.TemplateResponse(
        request, 
        "partials/table.html", 
        {"transacoes": lista_transacoes}
    )