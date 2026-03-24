from datetime import date, time
from typing import BinaryIO, Generator

from fastapi import FastAPI, File, UploadFile, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from .schemas import TransacaoBase

app = FastAPI()

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
# Itera sobre o SpooledTemporaryFile linha a linha (O(1) de memória na leitura)
    for line_bytes in file_buffer:
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

@app.post("/upload")
async def upload_cnab(request: Request, file: UploadFile = File(...)):
    
    gerador_transacoes = parse_cnab_stream(file.file)
        
    lista_transacoes = list(gerador_transacoes)
            

    return templates.TemplateResponse(
        request, 
        "partials/table.html", 
        {"transacoes": lista_transacoes}
    )