from typing import BinaryIO, Generator
from .schemas import TransacaoBase
from datetime import date, time
from sqlalchemy.exc import SQLAlchemyError

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
                
        except SQLAlchemyError as e:
                print(f"Erro de Banco de Dados: {e}")
                raise e # Relança para a rota /upload capturar e retornar o 405
                
        except Exception as e:
                print(f"Erro inesperado no processamento: {e}")
                raise e