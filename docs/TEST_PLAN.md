# 🧪 Coco-Tunnel API 测试方案与执行计划

> **版本**: v0.2  
> **作者**: Hermes Agent (Top-tier Software Engineer)  
> **日期**: 2026-04-10  
> **状态**: 🟢 执行阶段 (已获取 OpenAPI 规范 & 密钥)

---

## 🎯 1. 测试目标
确保 `coco-tunnel` 的控制面 API (pasctl) 满足**功能性、安全性、契约一致性**。
- **鉴权隔离**：验证 Admin、Internal、API Key 三套鉴权体系严格隔离，互不越权。
- **契约一致性**：验证响应结构符合 `ApiEnvelope` 定义 (`success`, `data`, `error`).
- **业务逻辑**：覆盖 Edge 节点管理、Tunnel 生命周期、API Key 管理等核心流程。

## 🛠️ 2. 测试架构 (Tech Stack)

| 组件 | 选型 | 理由 |
|------|------|------|
| **Core** | `pytest` + `pytest-asyncio` | 行业标准，原生支持异步协程 |
| **Client** | `httpx` | 异步 HTTP 客户端，支持 HTTP/2 和 Keep-Alive |
| **Env** | `python-dotenv` | 本地安全加载 `.env` 敏感配置 |
| **Schema** | `pydantic` | (未来) 用于严格验证响应数据结构 |
| **CI** | `GitHub Actions` | 自动化流水线 (Push/PR 触发) |

## 🔑 3. 鉴权体系测试策略

系统定义了三种隔离的安全域，测试将分别针对这三个域进行：

| 安全域 | 鉴权方式 | 关键头 (Header) | 核心测试端点 |
|:---|:---|:---|:---|
| **Admin** | Bearer Token | `Authorization: Bearer {ADMIN_TOKEN}` | `/api/v1/manage/edges/*`, `/assets/*` |
| **Internal** | Bearer Token | `Authorization: Bearer {INTERNAL_TOKEN}` | `/api/v1/internal/*` |
| **API Key** | Bearer Token | `Authorization: Bearer {API_KEY_SECRET}` | `/api/v1/manage/tunnels/*`, `/api/v1/manage/stats` |

### 越权测试 (Negative Testing)
- 使用 `INTERNAL_TOKEN` 访问 `/api/v1/manage/edges` ➔ 应返回 **401 Unauthorized**。
- 使用 `ADMIN_TOKEN` 访问 `/api/v1/internal/*` ➔ 应返回 **401/403**。

## 📋 4. 核心测试用例清单 (Top Priority)

### 4.1 基础设施 (Health)
- [x] `GET /health` - 验证服务存活

### 4.2 Admin 域 (运维管理)
- [ ] `GET /api/v1/manage/edges` - 列出节点
- [ ] `POST /api/v1/manage/edges` - 创建节点 (含 422 校验)
- [ ] `GET /assets/coco-edge` - 下载二进制文件 (验证 Content-Type)

### 4.3 API Key 域 (业务管理)
- [ ] `GET /api/v1/manage/tunnels` - 分页查询隧道
- [ ] `POST /api/v1/manage/tunnels` - 创建 TCP 隧道 (验证返回 client_token)
- [ ] `POST /api/v1/manage/tunnels/{id}/suspend` - 暂停隧道
- [ ] `POST /api/v1/manage/tunnels/{id}/resume` - 恢复隧道

### 4.4 Internal 域 (节点通信)
- [ ] `GET /api/v1/internal/nginx/configs` - 获取 Nginx 配置

## 📂 5. 目录结构

```text
coco-tunnel-test/
├── docs/
│   └── TEST_PLAN.md       # 📝 测试方案
├── tests/
│   ├── conftest.py        # 🔑 鉴权客户端 Fixtures (Admin, Internal, ApiKey)
│   ├── test_health.py     # ❤️ 健康检查
│   ├── test_admin_edges.py # 👮 Admin 域测试
│   └── test_apikey_tunnels.py # 🔑 API Key 域测试
├── .github/workflows/
│   └── ci.yml             # 🚀 自动测试流水线
├── .env                   # 🔒 本地密钥 (已加入 .gitignore)
└── pyproject.toml         # 📦 依赖管理
```
