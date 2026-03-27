from sqlalchemy import Column, Integer, Date, Numeric, String, Time
from .database import Base
from sqlalchemy.orm import Mapped, mapped_column

class Transacao(Base):
    __tablename__ = "transacoes"
    
    id = Column(Integer, primary_key=True, index=True)
    tipo = Column(Integer, nullable=False)
    data = Column(Date, nullable=False)
    valor = Column(Numeric(precision=10, scale=2), nullable=False)
    cpf = Column(String(11), nullable=False)
    cartao = Column(String(12), nullable=False)
    hora = Column(Time, nullable=False)
    dono_loja = Column(String(14), nullable=False)
    nome_loja = Column(String(19), nullable=False)
    
class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String, unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column()