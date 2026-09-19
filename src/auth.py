import os
from fastapi import Security, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt

security = HTTPBearer()

SECRET_KEY = os.getenv("ADMIN_JWT_SECRET", "insecure-default-secret-do-not-use-in-prod")
ALGORITHM = "HS256"

def verify_admin_role(credentials: HTTPAuthorizationCredentials = Security(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        role = payload.get("role")
        if role not in ["editor", "administrator"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions. Role 'editor' or 'administrator' required."
            )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

def verify_cron_job(credentials: HTTPAuthorizationCredentials = Security(security)):
    token = credentials.credentials
    cron_secret = os.getenv("CRON_SECRET")
    
    if cron_secret and token == cron_secret:
        return {"role": "cron"}
        
    # If it's not the valid cron secret, try decoding it as an admin JWT
    return verify_admin_role(credentials)
