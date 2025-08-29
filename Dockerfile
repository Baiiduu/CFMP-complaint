# 使用官方 Python 3.11 的精简镜像，固定版本避免自动升级
FROM python:3.11.10-slim-bookworm
# 环境变量设置
# PYTHONDONTWRITEBYTECODE: 防止Python将pyc文件写入磁盘
# PYTHONUNBUFFERED: 强制Python的stdout和stderr流不被缓冲
# DEBIAN_FRONTEND: 非交互式安装包，避免交互式提示
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# 安装系统依赖，支持MySQL数据库连接和其他编译需求
# build-essential: 包含编译所需的基本工具
# libmariadb-dev-compat 和 libmariadb-dev: MySQL/MariaDB客户端库
# libjpeg-dev 和 zlib1g-dev: 图像处理相关库（虽然当前项目不需要，但保留以防后续扩展）
# libffi-dev 和 libssl-dev: 加密和外部函数接口相关库
# python3-dev: Python开发头文件
# pkg-config: 编译时查找库的工具
# 替换原来的RUN apt-get部分为以下内容
# 使用阿里云的Debian源，加速国内访问


RUN rm -rf /etc/apt/sources.list.d/* && \
    rm -f /etc/apt/sources.list

ADD sources.list /etc/apt/
# 分开执行update和install，更容易排查问题
RUN apt-get update -y

RUN apt-get install -y \
    build-essential \
    libmariadb-dev-compat \
    libmariadb-dev \
    libjpeg-dev \
    zlib1g-dev \
    libffi-dev \
    libssl-dev \
    python3-dev \
    pkg-config \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 设置工作目录
WORKDIR /app

# 拷贝 requirements.txt 并安装依赖
# 先拷贝依赖文件，利用Docker层缓存机制，只有依赖变化时才重新安装
COPY requirements.txt .

# 配置pip使用阿里云镜像源，提高下载速度
RUN pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/

# 升级 pip 和安装构建工具
RUN python -m pip install --upgrade pip setuptools wheel

# 安装项目依赖包，使用--no-cache-dir避免缓存，减小镜像大小
RUN pip install --no-cache-dir -r requirements.txt

# 拷贝项目源代码到容器中
# 这一步放在安装依赖之后，因为代码变更频率高于依赖变更
COPY complaint-service .

# 收集静态文件到staticfiles目录
# 这是Django生产环境的标准做法
RUN python manager.py collectstatic --noinput --clear

# 创建普通用户，避免以root身份运行应用（安全最佳实践）
RUN adduser --disabled-password --gecos '' appuser && chown -R appuser:appuser /app
USER appuser

# 端口暴露
# 暴露8000端口，这是Django应用默认端口
EXPOSE 8000

# 启动命令
# 使用gunicorn作为WSGI服务器运行Django应用
# --bind 0.0.0.0:8000: 绑定到所有网络接口的8000端口
# --workers 3: 使用3个工作进程处理请求
# config.wsgi:application: 指定WSGI应用入口
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "config.wsgi:application"]
