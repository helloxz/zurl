from app.api.sys import *
from app.config import templates, get_config
from app.middleware.deny import deny_uas
from app.models.options import Options
import json
import os


def _get_base_path():
    """与 main 中保持一致：优先环境变量 BASE_URL，否则配置文件。供模板注入前端使用。"""
    base = os.environ.get("BASE_URL", "").strip() or ""
    if not base:
        try:
            base = (get_config().get("app") or {}).get("BASE_URL") or ""
        except Exception:
            pass
    base = (base or "").strip().rstrip("/")
    return base if base else ""

class IndexAPI:
    async def index(self, request: Request):
        # 调用deny_uas中间件检查User-Agent
        if await deny_uas(request):
            return templates.TemplateResponse("error_pages/deny.html", {"request": request})
        
        # 获取版本号和版本日期
        versionInfo = {
            "version": VERSION,
            "version_date": VERSION_DATE
        }
        # 默认站点信息，确保变量始终已定义（allow_guest_shorten 默认 True，与站点设置一致）
        site_info = {
            "title": "Zurl",
            "keywords": "zurl,短链服务,短链接",
            "description": "Zurl是一款轻量级短链服务，使用FastAPI开发。",
            "header": "",
            "footer": "",
            "allow_guest_shorten": True,
        }
        # 获取站点信息
        site_str = Options.get_option("site_info")
        # 转为json
        if site_str:
            try:
                parsed = json.loads(site_str)
                if isinstance(parsed, dict):
                    # 合并配置，保留默认缺失字段
                    site_info.update(parsed)
            except (TypeError, ValueError, json.JSONDecodeError):
                # 解析失败保持默认
                pass
        
        base_path = _get_base_path()
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "versionInfo": versionInfo,
                "site_info": site_info,
                "base_path": base_path or "",
            },
        )
