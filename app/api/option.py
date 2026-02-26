from app.models.options import Options
import re
from app.utils.helper import *
import json
from fastapi import Form

class OptionAPI:
    async def set_option(self,key:str=Form(...),value:str=Form(...)):
        # 检查key是否合法，只能是字母、数字或下划线以及中横线组成，且不小于2位
        if not re.match(r'^[a-zA-Z0-9_-]{2,}$', key):
            return show_json(500,"Invalid key format")
        # 检查value是否合法，只能是json
        try:
            json.loads(value)
            # 写入数据库中 (避免使用变量名 re 覆盖 re 模块，之前这里导致 UnboundLocalError)
            result = Options.set_option(key, value)
            # 如果写入成功
            if result:
                return show_json(200,"success")
            else:
                return show_json(500,"Failed to set option")
        except ValueError:
            return show_json(500,"Invalid value format")

    async def get_option(self,key: str):
        value = await Options.get_option(key)
        if not value:
            return show_json(404, "Option not found")
        return show_json(200, "success", value)
    
    # 获取站点信息
    async def get_site_info(self):
        # 获取配置值（补充 await，避免拿到协程对象）
        site_info = Options.get_option("site_info")
        # 若不存在
        if not site_info:
            return show_json(404, "Site info not found")
        # 若为可解析的字符串 / 字节，再尝试 JSON 解析
        if isinstance(site_info, (str, bytes, bytearray)):
            try:
                site_info = json.loads(site_info)
            except (TypeError, ValueError):
                return show_json(500, "Site info invalid JSON")
        # 确保返回的站点信息包含 allow_guest_shorten，缺失时默认为 True
        if isinstance(site_info, dict) and "allow_guest_shorten" not in site_info:
            site_info = {**site_info, "allow_guest_shorten": True}
        return show_json(200, "success", site_info)
    
