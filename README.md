
[中文说明](README_zh.md) | **English**

# Zurl

Zurl is a simple and practical short URL system that can quickly generate short links for easy sharing and management. Zurl aims to provide a lightweight solution to help users better manage and track links.

![](https://v.uuu.ovh/imgs/2025/09/12/cf868390221fcfcb.png)

![](https://v.uuu.ovh/imgs/2025/09/12/a7f605b1c7419bf4.png)

## Features

* [x] **Short Link Generation**: Users can convert long URLs into short links for easy sharing and distribution.
* [x] **Link Management**: Provides an intuitive interface where administrators can view, edit, and delete links.
* [x] **Delayed Counting**: The system delays recording click counts for each short link to avoid excessive pressure during high concurrency.
* [x] **Automatic Title Retrieval**: When adding links, the system attempts to automatically retrieve the title of the long URL for easy identification.
* [x] **UA Blocking Support**: Administrators can customize User-Agents to block, preventing malicious access.
* [x] **Data Migration**: Supports migrating YOURLS data to Zurl, helping users transition.
* [x] **API**: Provides API interfaces for secondary development and integration into any system.
* [x] Support for setting short link expiration dates.
* [x] Custom site information
* [x] API Token management
* [x] Bilingual support (Chinese and English)
* [x] Subpath deployment (BASE_URL) for reverse proxy
* [ ] Advanced analytics
* [ ] Login session management

## Installing Zurl

> Docker deployment is supported. Please ensure you have Docker and Docker Compose installed. Zurl requires Redis for delayed click counting; the project provides a `docker-compose.yaml` that runs both Zurl and Redis.

**Clone the repo and run with Docker Compose (recommended):**

```bash
git clone https://github.com/helloxz/zurl.git && cd zurl
```

Use the included `docker-compose.yaml`. Optional: set subpath via env (e.g. `BASE_URL=/s` for `http://IP:3080/s`):

```yaml
# docker-compose.yaml (in project root)
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

Then run:

```bash
docker compose up -d --build
```

Visit `http://IP:3080` (or `http://IP:3080/<BASE_URL>` if you set `BASE_URL`) and follow the prompts to complete initialization.

**Using pre-built image only:**  
Use the same `zurl` service block but set `build` to use image `helloz/zurl`, and either run Redis via the same compose or set `REDIS_HOST` / `REDIS_PORT` / `REDIS_PASSWORD` to point to an existing Redis instance.

**Upgrade**

1. Backup the data in the current mounted directory (and Redis data if needed).
2. Stop and remove the current containers: `docker compose down`
3. Pull the latest image or rebuild: `docker compose pull` or `docker compose build --pull`
4. Recreate and start: `docker compose up -d`

> Note: Please backup your data before upgrading. You are responsible for any data risks caused by upgrades!

## Configuration

**Redis**  
Redis is required. In Docker, it is configured via environment variables: `REDIS_HOST`, `REDIS_PORT`, `REDIS_DB`, `REDIS_PASSWORD`. You can also set these in `config.toml` under the `[redis]` section when not using env vars.

**Subpath (BASE_URL)**  
For deployment under a subpath (e.g. `/zurl`), set `BASE_URL` in the environment or in `config.toml` under `app.BASE_URL` (e.g. `BASE_URL = "/zurl"`). Rebuild the frontend with the same base if you build from source.

**UA Blocking**

You can find `config.toml` in the mounted directory and add User-Agents to block in `app.DENY_UA`. Default blocks:

* *WeChat
* *QQ

> Note: You need to restart the container after modifying the configuration!

**Reset Password**

If you forget your administrator account or password, you can delete the `config.toml` file in the mounted directory, then restart the container and revisit Zurl to complete initialization. (This operation does not affect data)

> Do not delete the `db` directory in the mounted directory, as this will cause link data loss.

## Demo

* Demo site: [https://zurl.demo.mba](https://zurl.demo.mba)
* Username: `xiaoz`
* Password: `blog.xiaoz.org`

## Issue Feedback

* If you have any issues, you can submit them in [Issues](https://github.com/helloxz/zurl/issues).
* Or add my WeChat: `xiaozme`, please be sure to note Zurl

## Tech Stack

* Backend: Python3 + FastAPI
* Frontend: Vue3 + Element Plus
* Database: SQLite3
* Cache: Redis

## Other Products

If you're interested, you can also learn about our other products.

* [Zdir](https://www.zdir.pro/zh/) - A lightweight, multi-functional file sharing program.
* [OneNav](https://www.onenav.top/) - An efficient browser bookmark management tool for centralized bookmark management.
* [ImgURL](https://www.imgurl.org/) - A free image hosting service launched in 2017.
