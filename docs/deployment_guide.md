# DeerFlow 部署指南

## 概述

本指南详细介绍了 DeerFlow 的各种部署方式，包括本地开发环境、生产环境和容器化部署。无论您是个人开发者还是企业用户，都可以根据需求选择适合的部署方案。

## 环境要求

### 最低系统要求

- **操作系统**：Linux、macOS 或 Windows
- **CPU**：双核处理器（推荐四核或更高）
- **内存**：4GB RAM（推荐 8GB 或更高）
- **存储**：10GB 可用空间（推荐 20GB 或更高）
- **网络**：稳定的互联网连接

### 软件依赖

- **Python**：版本 3.12+
- **Node.js**：版本 22+
- **uv**：Python 包管理工具
- **pnpm**：Node.js 包管理工具
- **marp-cli**：用于 PPT 生成（可选）

## 本地开发环境

### 1. 克隆代码库

```bash
git clone https://github.com/bytedance/deer-flow.git
cd deer-flow
```

### 2. 安装依赖

```bash
# 安装 Python 依赖
uv sync

# 安装 Web UI 依赖
cd web
pnpm install
cd ..
```

### 3. 配置环境变量

创建 `.env` 文件并设置必要的环境变量：

```bash
cp .env.example .env
```

编辑 `.env` 文件，配置以下关键变量：

```bash
# 选择搜索 API：tavily, duckduckgo, brave_search, arxiv
SEARCH_API=tavily
TAVILY_API_KEY=your_tavily_api_key

# 如果使用 Brave Search
# BRAVE_SEARCH_API_KEY=your_brave_search_api_key

# 如果使用 TTS 功能
# VOLCENGINE_ACCESS_KEY=your_volcengine_access_key
# VOLCENGINE_SECRET_KEY=your_volcengine_secret_key
# VOLCENGINE_SERVICE_ID=your_volcengine_service_id

# 如果使用 RAG 功能
# RAG_PROVIDER=ragflow
# RAGFLOW_API_URL=http://localhost:9388
# RAGFLOW_API_KEY=ragflow-xxx
# RAGFLOW_RETRIEVAL_SIZE=10

# 如果使用 LangSmith 追踪
# LANGSMITH_TRACING=true
# LANGSMITH_ENDPOINT=https://api.smith.langchain.com
# LANGSMITH_API_KEY=xxx
# LANGSMITH_PROJECT=xxx
```

### 4. 配置 LLM 模型

创建 `conf.yaml` 文件并配置 LLM 模型：

```bash
cp conf.yaml.example conf.yaml
```

编辑 `conf.yaml` 文件，配置模型信息：

```yaml
# 基本模型配置示例（OpenAI 兼容模型）
BASIC_MODEL:
  base_url: "https://api.openai.com/v1"
  model: "gpt-4o"
  api_key: "your_api_key"

# 如果使用 Doubao 模型
# BASIC_MODEL:
#   base_url: "https://ark.cn-beijing.volces.com/api/v3"
#   model: "doubao-1.5-pro-32k-250115"
#   api_key: "your_api_key"

# 如果使用 Qwen 模型
# BASIC_MODEL:
#   base_url: "https://dashscope.aliyuncs.com/compatible-mode/v1"
#   model: "qwen-max-latest"
#   api_key: "your_api_key"
```

### 5. 启动开发服务器

#### 控制台界面

```bash
uv run main.py
```

#### Web 界面

```bash
# 在 macOS/Linux 上
./bootstrap.sh -d

# 在 Windows 上
bootstrap.bat -d
```

然后在浏览器中访问 `http://localhost:3000`。

## 生产环境部署

### 1. 构建前端资源

```bash
cd web
pnpm build
cd ..
```

### 2. 配置生产环境变量

编辑 `.env` 文件，确保所有必要的环境变量都已正确配置。对于生产环境，建议：

- 使用环境变量而不是 `.env` 文件
- 使用更严格的 CORS 设置
- 配置适当的日志级别

### 3. 启动生产服务器

#### 使用 Gunicorn（推荐用于 Linux/macOS）

```bash
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker server:app
```

#### 使用 Uvicorn

```bash
uvicorn server:app --host 0.0.0.0 --port 8000 --workers 4
```

### 4. 配置反向代理（可选但推荐）

为了更好的安全性和性能，建议使用 Nginx 或 Apache 作为反向代理。

#### Nginx 配置示例

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

## Docker 部署

### 1. 单独构建和运行后端

```bash
# 构建 Docker 镜像
docker build -t deer-flow-api .

# 运行容器
docker run -d -t -p 8000:8000 --env-file .env --name deer-flow-api-app deer-flow-api

# 停止容器
docker stop deer-flow-api-app
```

### 2. 使用 Docker Compose 部署完整应用

```bash
# 构建镜像
docker compose build

# 启动服务
docker compose up -d

# 查看日志
docker compose logs -f

# 停止服务
docker compose down
```

Docker Compose 配置文件 (`docker-compose.yml`) 示例：

```yaml
version: '3'

services:
  api:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    env_file:
      - .env
    volumes:
      - ./conf.yaml:/app/conf.yaml
    restart: unless-stopped

  web:
    build:
      context: ./web
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://api:8000
    depends_on:
      - api
    restart: unless-stopped
```

## 云平台部署

### AWS 部署

#### 使用 Elastic Beanstalk

1. 安装 EB CLI：
   ```bash
   pip install awsebcli
   ```

2. 初始化 EB 应用程序：
   ```bash
   eb init -p docker deer-flow
   ```

3. 创建环境并部署：
   ```bash
   eb create deer-flow-env
   ```

4. 更新部署：
   ```bash
   eb deploy
   ```

#### 使用 ECS (Elastic Container Service)

1. 创建 ECR 仓库并推送镜像
2. 创建 ECS 任务定义和服务
3. 配置负载均衡器和自动扩展

### GCP 部署

#### 使用 Cloud Run

1. 构建并推送 Docker 镜像到 Google Container Registry：
   ```bash
   gcloud builds submit --tag gcr.io/your-project-id/deer-flow
   ```

2. 部署到 Cloud Run：
   ```bash
   gcloud run deploy deer-flow --image gcr.io/your-project-id/deer-flow --platform managed
   ```

### Azure 部署

#### 使用 Azure Container Instances

1. 创建资源组：
   ```bash
   az group create --name deer-flow-group --location eastus
   ```

2. 创建容器实例：
   ```bash
   az container create --resource-group deer-flow-group --name deer-flow --image your-registry/deer-flow --dns-name-label deer-flow --ports 80
   ```

## 高可用性部署

对于需要高可用性的生产环境，建议：

1. **水平扩展**：部署多个应用实例
2. **负载均衡**：使用负载均衡器分发流量
3. **自动扩展**：根据负载自动调整实例数量
4. **数据库分离**：使用外部数据库存储状态
5. **监控和告警**：设置监控和告警系统

## 性能优化

### 服务器优化

1. **增加工作进程数**：根据 CPU 核心数调整工作进程
2. **内存优化**：监控并优化内存使用
3. **缓存**：实现适当的缓存策略
4. **异步处理**：将长时间运行的任务移至异步队列

### LLM 服务优化

1. **模型选择**：根据需求选择合适的模型
2. **批处理**：实现请求批处理
3. **提示优化**：优化提示以减少令牌使用
4. **本地模型**：考虑使用本地部署的模型

## 监控和日志

### 日志配置

在 `.env` 文件中配置日志级别：

```
LOG_LEVEL=INFO  # 可选: DEBUG, INFO, WARNING, ERROR, CRITICAL
```

### 监控工具

1. **Prometheus**：收集指标
2. **Grafana**：可视化指标
3. **ELK Stack**：集中式日志管理
4. **New Relic/Datadog**：应用性能监控

## 安全最佳实践

1. **API 密钥管理**：安全存储和轮换 API 密钥
2. **CORS 配置**：限制跨域请求
3. **HTTPS**：启用 HTTPS 加密
4. **输入验证**：验证所有用户输入
5. **依赖更新**：定期更新依赖包

## 故障排除

### 常见问题

1. **API 连接错误**：
   - 检查 API 密钥和基本 URL 配置
   - 验证网络连接和防火墙设置

2. **模型响应错误**：
   - 检查模型配置
   - 验证请求格式和参数

3. **内存错误**：
   - 增加容器或服务器内存限制
   - 优化大型请求的处理

4. **Web UI 加载问题**：
   - 检查前端构建和静态文件
   - 验证 API 端点配置

### 日志查看

```bash
# 查看应用日志
tail -f deer-flow.log

# 查看 Docker 容器日志
docker logs -f deer-flow-api-app

# 查看 Docker Compose 服务日志
docker compose logs -f api
```

## 升级指南

### 从旧版本升级

1. 备份配置文件：
   ```bash
   cp .env .env.backup
   cp conf.yaml conf.yaml.backup
   ```

2. 拉取最新代码：
   ```bash
   git pull origin main
   ```

3. 更新依赖：
   ```bash
   uv sync
   cd web
   pnpm install
   cd ..
   ```

4. 迁移配置：
   ```bash
   # 检查新的配置选项
   diff .env.example .env
   # 更新配置文件
   ```

5. 重启服务：
   ```bash
   # 如果使用 Docker Compose
   docker compose down
   docker compose up -d
   
   # 如果直接运行
   # 重启应用服务
   ``` 