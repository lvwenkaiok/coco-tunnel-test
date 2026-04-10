# 🧪 Coco-Tunnel API 测试方案与执行报告

> **版本**: v1.0  
> **作者**: Hermes Agent (Top-tier Software Engineer)  
> **日期**: 2026-04-10  
> **状态**: 🟢 核心测试完成 (24/24 通过)

---

## 📊 测试执行结果

```
======================== 24 passed in 8.02s =========================
```

| 测试文件 | 用例数 | 状态 | 说明 |
|----------|:------:|:----:|------|
| `test_health.py` | 1 | ✅ | 健康检查 |
| `test_admin_edges.py` | 2 | ✅ | Admin 基础功能 |
| `test_apikey_tunnels.py` | 2 | ✅ | API Key 基础功能 |
| `test_auth_security.py` | 5 | ✅ | **鉴权隔离与安全** |
| `test_tunnel_lifecycle.py` | 8 | ✅ | **隧道完整生命周期** |
| `test_edge_lifecycle.py` | 6 | ✅ | **Edge 节点完整生命周期** |

---

## 🔑 核心测试覆盖

### 1. 鉴权安全 (Auth Security)
- ✅ Admin Token 无法访问 Internal 接口 → 401
- ✅ Internal Token 无法访问 Admin 接口 → 401/403
- ✅ API Key 无法访问 Admin 接口 → 401/403
- ✅ 无认证访问受保护接口 → 401
- ✅ 无效 Token 访问 → 401

### 2. 隧道生命周期 (Tunnel CRUD)
- ✅ 创建隧道并返回 `client_token`
- ✅ 查询单个隧道详情
- ✅ 分页查询 + 按 `user_id` 过滤
- ✅ 暂停隧道 (`/suspend`)
- ✅ 恢复隧道 (`/resume`)
- ✅ 管理员轮换 Token (`/token/rotate`)
- ✅ 查询隧道实时状态 (`/state`)
- ✅ 删除隧道 + 验证 404

### 3. Edge 节点生命周期
- ✅ 创建节点 + 验证出现在列表
- ✅ 创建节点校验 (缺少必填字段 → 422)
- ✅ 更新节点配置 (`PATCH`)
- ✅ 生成安装脚本 (`/install-script`)
- ✅ 错误页配置 CRUD (Get + Update)
- ✅ 删除节点

---

## 🛠️ 技术架构

| 组件 | 选型 | 说明 |
|------|------|------|
| **框架** | `pytest` + `pytest-asyncio` | 异步测试支持 |
| **HTTP** | `httpx` | 异步客户端，HTTP/2 支持 |
| **配置** | `python-dotenv` | 本地密钥管理 |
| **CI** | GitHub Actions | Push/PR 自动触发 |

### 三域鉴权模型

```
┌─────────────────────────────────────────────────┐
│              Coco-Tunnel API                    │
├────────────┬────────────┬───────────────────────┤
│   Admin    │  Internal  │      API Key          │
│  /manage/  │ /internal/ │   /manage/tunnels     │
│  /assets/  │            │   /manage/stats       │
├────────────┴────────────┴───────────────────────┤
│         Bearer Token Auth (隔离)                │
└─────────────────────────────────────────────────┘
```

---

## 📂 项目结构

```
coco-tunnel-test/
├── docs/TEST_PLAN.md              # 本文档
├── tests/
│   ├── conftest.py                # 三域 HTTP 客户端 Fixtures
│   ├── test_health.py             # 健康检查
│   ├── test_admin_edges.py        # Admin 基础测试
│   ├── test_apikey_tunnels.py     # API Key 基础测试
│   ├── test_auth_security.py      # 鉴权隔离测试
│   ├── test_tunnel_lifecycle.py   # 隧道 CRUD 全流程
│   └── test_edge_lifecycle.py     # Edge 节点 CRUD 全流程
├── .github/workflows/ci.yml       # CI 流水线
├── pyproject.toml                 # 依赖配置
├── .env                           # 本地密钥 (不提交)
└── .gitignore
```

---

## 📋 待补充 (需要时序图文件)

> ⚠️ 未收到 `coco-tunnel-business-sequence.md` 文件内容。以下测试待补充：

- [ ] 客户端连接建立流程测试
- [ ] 数据转发链路验证
- [ ] Webhook 回调测试
- [ ] Internal 接口完整测试 (JWT 公钥、Nginx 配置、Token 校验)
- [ ] Assets 二进制下载测试
- [ ] 批量操作测试 (Batch Suspend/Resume)
- [ ] 流量统计与月度报表测试

**请重新发送时序图文件内容，我将补充对应的集成测试。**
