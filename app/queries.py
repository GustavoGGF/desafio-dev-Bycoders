from typing import Generator

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from .schemas import TransacaoBase
from itertools import islice
from .models import Transacao

def chunked_iterable(iterable: Generator[TransacaoBase, None, None], size: int):
    it = iter(iterable)
    while True:
        chunk = list(islice(it, size))
        if not chunk:
            break
        yield chunk
        
def post_all_transactions(db: Session, gerador_transacoes: Generator[TransacaoBase, None, None]):    
    try:
            for batch in chunked_iterable(gerador_transacoes, 1000):
                # Converte o lote
                db_batch = [
                    Transacao(**t.model_dump()) 
                    for t in batch
                ]
                
                db.add_all(db_batch)
                db.commit() # Tenta salvar o lote
                
    except SQLAlchemyError as e:
            db.rollback() # CANCELA tudo que não foi commitado se der erro de banco
            print(f"Erro de Banco de Dados: {e}")
            raise e # Relança para a rota /upload capturar e retornar o 405
            
    except Exception as e:
            db.rollback() # Proteção extra para erros de lógica/Python
            print(f"Erro inesperado no processamento: {e}")
            raise e

def get_all_transactions(db: Session):    
    return db.query(Transacao).all()