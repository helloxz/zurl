
**中文说明** | [English](README.md)

# Zurl

Zurl 是一款简单且实用的短链接系统，可以快速生成短链接，方便分享和管理。Zurl 旨在提供一个轻量级的解决方案，帮助用户更好地管理和跟踪链接。

![970c82f82f62fe5c.png](https://img.rss.ink/imgs/2025/08/04/970c82f82f62fe5c.png)

![c57c3cce4618acd3.png](https://img.rss.ink/imgs/2025/08/04/c57c3cce4618acd3.png)

## 功能特点

* [x] **短链接生成**：用户可以将长链接转换为短链接，便于分享和传播。
* [x] **链接管理**：提供直观的界面，管理员可以查看、编辑和删除。
* [x] **延迟计数**：系统会延迟记录每个短链接的点击次数，避免高并发时压力过大。
* [x] **自动获取标题**：添加链接时，系统会尝试自动获取长链接的标题，方便后续识别。
* [x] **支持UA屏蔽**：管理员可以自定义需要屏蔽的User-Agent，防止恶意访问。
* [x] **数据迁移**：支持将YOURLS数据迁移到Zurl，帮助用户过渡。
* [x] **API**：提供API接口，方便二次开发和集成到任意系统。
* [x] 支持设置短链有效期。
* [x] 自定义站点信息
* [x] API Token管理
* [x] 中英文双语支持
* [x] 子路径部署（BASE_URL），便于反向代理
* [ ] 高级分析
* [ ] 登录会话管理

## 安装Zurl

> 支持 Docker 部署，请确保已安装 Docker 与 Docker Compose。Zurl 依赖 Redis 做延迟计数，项目提供的 `docker-compose.yaml` 会同时启动 Zurl 与 Redis。

**克隆仓库并使用 Docker Compose 运行（推荐）：**

```bash
git clone https://github.com/helloxz/zurl.git && cd zurl
```

使用项目自带的 `docker-compose.yaml`。如需子路径部署，可设置环境变量（如 `BASE_URL=/s` 则访问地址为 `http://IP:3080/s`）：

```yaml
# 项目根目录下的 docker-compose.yaml
services:
  redis:
    image: redis:7-alpine
    container_name: zurl-redis
    restart: always
    command: redis-server --requirepass zurl
    volumes:
      - ./redis/data:/data

  zurl:
    container_name: zurl
    build:
      context: .
      args:
        - BASE_URL=${BASE_URL:-}
    image: helloz/zurl
    ports:
      - "3080:3080"
    restart: always
    environment:
      - BASE_URL=${BASE_URL:-}
      - REDIS_HOST=redis
      - REDIS_PORT=6379
      - REDIS_DB=0
      - REDIS_PASSWORD=zurl
    volumes:
      - ./data:/opt/zurl/app/data
    depends_on:
      - redis
```

然后执行：

```bash
docker compose up -d --build
```

访问 `http://IP:3080`（若设置了 `BASE_URL` 则为 `http://IP:3080/<BASE_URL>`），按提示完成初始化。

**仅使用预构建镜像：**  
保留上述 `zurl` 服务配置，可不写 `build` 仅用镜像 `helloz/zurl`，并单独启动 Redis 或在环境中配置 `REDIS_HOST`、`REDIS_PORT`、`REDIS_PASSWORD` 指向已有 Redis。

**升级**

1. 备份当前挂载目录的数据（如有 Redis 数据也请备份）。
2. 停止并删除当前容器：`docker compose down`
3. 拉取最新镜像或重新构建：`docker compose pull` 或 `docker compose build --pull`
4. 重新创建并启动：`docker compose up -d`

> 注意：升级前请务必备份数据，升级造成的数据风险由您自行承担！

## 设置

**Redis**  
Zurl 依赖 Redis。在 Docker 中通过环境变量配置：`REDIS_HOST`、`REDIS_PORT`、`REDIS_DB`、`REDIS_PASSWORD`。未使用环境变量时，可在挂载目录下的 `config.toml` 中配置 `[redis]` 段。

**子路径（BASE_URL）**  
若部署在子路径（如 `/zurl`），请设置环境变量 `BASE_URL` 或在 `config.toml` 的 `app.BASE_URL` 中填写（如 `BASE_URL = "/zurl"`）。从源码构建时需使用相同 base 重新构建前端。

**UA屏蔽**

可以在挂载目录下找到`config.toml`中的`app.DENY_UA`添加需要屏蔽的User-Agent，默认屏蔽：

* *微信
* *QQ

> 注意：修改配置后需要重启容器！

**重置密码**

如果您忘记了管理员账号或密码，可以删除挂载目录下的`config.toml`文件，然后重启容器并重新访问Zurl完成初始化即可。（此操作不影响数据）

> 切勿删除挂载目录下的`db`目录，否则会导致链接数据丢失。

## 演示

* 演示站点：[https://zurl.demo.mba](https://zurl.demo.mba)
* 用户名：`xiaoz`
* 密码：`blog.xiaoz.org`

## 问题反馈

* 如果有任何问题可以在[Issues](https://github.com/helloxz/zurl/issues) 中提交。
* 或者添加我的微信：`xiaozme`，请务必备注Zurl

## 技术栈

* 后端：Python3 + FastAPI
* 前端：Vue3 + Element Plus
* 数据库：SQLite3
* 缓存：Redis

## 其他产品

如果您有兴趣，还可以了解我们的其他产品。

* [Zdir](https://www.zdir.pro/zh/) - 一款轻量级、多功能的文件分享程序。
* [OneNav](https://www.onenav.top/) - 高效的浏览器书签管理工具，将您的书签集中式管理。
* [ImgURL](https://www.imgurl.org/) - 2017年上线的免费图床。