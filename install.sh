#!/bin/sh

# 安装依赖
install_deps(){
    apk update
    apk add python3
    apk add py3-pip
    mkdir -p /opt/zurl/app/data/db
}

# 安装 Python 依赖
install_python_deps(){
    python3 -m venv myenv
    . myenv/bin/activate
    pip3 install -r app/requirements.txt
}

# 清理缓存，缩小镜像体积
clean(){
    apk del py3-pip
    rm -rf /var/cache/apk/*
    rm -rf /root/.cache
    rm -rf /opt/zurl/.github
    rm -rf /opt/zurl/.git
    rm -rf /opt/zurl/frontend
}

install_deps && install_python_deps && clean
