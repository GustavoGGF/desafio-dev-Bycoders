from pydantic import BaseModel, field_validator
from datetime import date, time
from typing import List

class TransacaoBase(BaseModel):
    tipo: int
    data: date
    valor: float
    cpf: str
    cartao: str
    hora: time
    dono_loja: str
    nome_loja: str

    # Um toque de Sênior: Validador para garantir que o valor nunca seja negativo no parse
    @field_validator('valor')
    @classmethod
    def valor_positivo(cls, v: float) -> float:
        if v < 0:
            raise ValueError('O valor da transação deve ser positivo')
        return v

class LojaResumo(BaseModel):
    nome_loja: str
    saldo_total: float
    transacoes: List[TransacaoBase]