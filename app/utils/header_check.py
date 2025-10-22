from fastapi import Header, HTTPException
from jose import JWTError
from ..utils import jwt

# Hàm xác thực token
async def verify_token(authorization: str = Header(...)):
    token = authorization.split()[1]
    if not token:
        raise HTTPException(status_code=401, detail="Token missing")

    try:
        payload = jwt.decode_token(token)
        return payload # Trả email để endpoint sử dụng
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")