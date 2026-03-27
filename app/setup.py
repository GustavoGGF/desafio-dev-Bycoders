from .database import SessionLocal
from . import models
from .auth import get_password_hash

def create_initial_user():
    db = SessionLocal()
    
    try:
        user = db.query(models.User).filter(models.User.username == "admin").first()
        
        if not user:
            admin_user = models.User(
                username = "admin",
                hashed_password=get_password_hash("admin123")
            )
            
            db.add(admin_user)
            db.commit()
    except Exception as e:
        print(f"Erro ao criar usuário: {e}")
    finally:
        db.close()