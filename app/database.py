from os import getenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
from time import sleep

load_dotenv()

SQLACLCHEMY_DATABASE_URL = getenv("DATABASE_URL")

if not SQLACLCHEMY_DATABASE_URL:
    raise RuntimeError("Erro ao obter SQLACLCHEMY_DATABASE_URL")

engine = create_engine(SQLACLCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
def get_engine_with_retry(url: str, retries: int=10, delay: int=10):
    clean_url = url.strip().replace('"', '').replace("'", "")
    
    for i in range(retries):
        try:
            temp_engine = create_engine(clean_url)
            # Agora usamos o 'conn' para um "Health Check" real
            with temp_engine.connect() as conn:
                # O 'conn' executa um comando simples de ping no Postgres
                conn.execute(text("SELECT 1")) 
                print("--- Banco de dados pronto e processando queries! ---")
                return temp_engine
        except Exception as e:
            if i == retries - 1: 
                raise e
            print(f"Tentativa {i+1}/{retries}: Aguardando banco... (Erro: {e})")
            sleep(delay)

# Chame a função passando a URL
engine = get_engine_with_retry(SQLACLCHEMY_DATABASE_URL)