# 帮我实现一个依赖注入中间件，通过request获取header中的Authorization: Bearer <token>，并验证token是否有效，有效则放行，无效则返回401 Unauthorized错误
from fastapi import Request, HTTPException, Depends
from app.models.sessions import Sessions
from app.models.conn import get_db
import time
async def get_current_session(request: Request):
    # 从请求头中获取Authorization字段
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # 验证Bearer token格式
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid token format")

    token = auth_header.split(" ")[1]

    # 从数据库中查询会话
    db = next(get_db())
    session = db.query(Sessions).filter(Sessions.token == token).first()
    db.close()

    # 如果会话不存在或已过期，返回401错误
    if not session or session.expires_at < int(time.time()):
        raise HTTPException(status_code=401, detail="Unauthorized")

    return session


async def get_current_session_optional(request: Request):
    """可选会话：有有效 token 则返回 session，否则返回 None。用于允许未登录访问的接口（如按配置决定是否要求登录的 shorten）。"""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None
    token = auth_header.split(" ")[1].strip()
    if not token:
        return None
    db = next(get_db())
    try:
        session = db.query(Sessions).filter(Sessions.token == token).first()
        if session and session.expires_at >= int(time.time()):
            return session
    finally:
        db.close()
    return None
