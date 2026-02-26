# 使用 python-slim 作为基础镜像（不再使用 redis 镜像）
FROM python:3.12-slim

WORKDIR /opt/zurl

# 安装 Node.js 用于在容器内构建前端（构建完成后会卸载）
RUN apt-get update && apt-get install -y --no-install-recommends \
    nodejs npm \
    && rm -rf /var/lib/apt/lists/*

RUN npm install -g pnpm

# 复制项目文件（含前端源码，用于构建）
COPY . .

# 修正脚本换行符与权限
RUN sed -i 's/\r$//' install.sh run.sh && chmod +x install.sh run.sh

# 创建数据目录
RUN mkdir -p /opt/zurl/app/data/db

# 安装 Python 依赖
RUN python3 -m venv myenv && . myenv/bin/activate && pip install --no-cache-dir -r app/requirements.txt

# 构建前端：BASE_URL 仅在构建时生效，用于设置 VITE_BASE_URL（与运行时后端 BASE_URL 一致）
ARG BASE_URL=
ENV VITE_BASE_URL=${BASE_URL}
RUN cd frontend && pnpm install && pnpm build

# 构建完成后删除前端源码和 Node，缩小镜像
RUN rm -rf frontend && \
    apt-get purge -y nodejs npm && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/* /root/.npm

EXPOSE 3080
VOLUME /opt/zurl/app/data
CMD ["sh", "run.sh"]
