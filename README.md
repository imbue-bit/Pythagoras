<div align="center">
  <h1>Pythagoras</h1>
  <p>
    <strong>一个由 AI 驱动的认知数据接口，让您用自然语言与数据库对话。</strong>
  </p>
  <p>
    <a href="#-快速入门">快速入门</a> •
    <a href="#-核心特性">核心特性</a> •
    <a href="#-api-参考">API 参考</a> •
    <a href="#-贡献指南">贡献指南</a>
  </p>

  <p>
    <a href="https://github.com/imbue-bit/pythagoras/actions/workflows/ci.yml"><img src="https://img.shields.io/github/actions/workflow/status/your-org/pythagoras/ci.yml?branch=main&style=for-the-badge&logo=github" alt="CI Status"></a>
  </p>
</div>

---

Pythagoras 是一个开源的智能中间件，它在您的应用程序和 SQL 数据库之间建立了一个由大型语言模型驱动的认知层。它能将复杂的自然语言查询实时转化为精确、安全且高效的 SQL 语句，使任何人都能成为数据分析师。

忘记繁琐的 SQL 编写和 BI 工具的学习曲线吧。有了 Pythagoras，与您的数据交互就像与同事交谈一样简单。

## 🚀 快速入门

最快体验 Pythagoras 的方式是通过 Docker Compose。

### 1. 准备环境

克隆仓库并创建一个 `.env` 文件：

```bash
git clone https://github.com/your-org/pythagoras.git
cd pythagoras
cp .env.example .env
```

现在，编辑 `.env` 文件，填入您的 OpenAI API 密钥，并配置您的数据库连接信息（默认为一个开箱即用的 SQLite 数据库）。

```dotenv
# .env
OPENAI_API_KEY="sk-..."
DATABASE_TYPE="sqlite"
DATABASE_NAME="data/sample.db"
# ... 其他配置
```

### 2. 启动服务

使用 Docker Compose 一键启动所有服务：

```bash
docker-compose up -d
```

服务将在 `http://localhost:8000` 上运行。您可以访问 `http://localhost:8000/docs` 查看交互式的 API 文档。

### 3. 发送您的第一个查询

使用 `curl` 或任何 API 客户端，带上默认的管理员 API 密钥，向 Pythagoras 发送一个自然语言查询：

```bash
curl -X POST "http://localhost:8000/v1/query" \
     -H "Content-Type: application/json" \
     -H "X-API-Key: super_secret_admin_token" \
     -d '{
       "query": "显示所有部门中薪水最高的员工"
     }'
```

**您将收到类似这样的响应：**

```json
{
  "id": "py-trace-a1b2c3d4e5f6",
  "source": "live",
  "request": {
    "nl": "显示所有部门中薪水最高的员工",
    "sql": "SELECT d.name AS department_name, e.name AS employee_name, e.salary FROM employees e JOIN (SELECT department_id, MAX(salary) as max_salary FROM employees GROUP BY department_id) AS max_sal ON e.department_id = max_sal.department_id AND e.salary = max_sal.max_salary JOIN departments d ON e.department_id = d.id"
  },
  "execution": {
    "status": "succeeded",
    "data": [
      {
        "department_name": "Sales",
        "employee_name": "Charlie",
        "salary": 82000
      },
      {
        "department_name": "HR",
        "employee_name": "Bob",
        "salary": 75000
      }
    ]
  }
}
```

就是这么简单！您刚刚用自然语言完成了一次复杂的 SQL 查询。

## ✨ 核心特性

Pythagoras 不仅仅是一个 NL-to-SQL 的转换器，它是一个为生产环境设计的完整解决方案。

| 特性 | 描述 |
| --- | --- |
| 🧠 **SOTA 模型** | 搭载 Socrates-SQL，一个基于物理信息神经网络（PINNs）启发式训练的先进模型，确保了极高的查询准确性和对复杂问题的理解能力。 |
| 🛡️ **企业级安全** | 内置基于角色的访问控制 (RBAC)，确保用户只能访问其权限边界内的数据。所有生成的 SQL 都经过验证，杜绝恶意操作。 |
| ⚡ **高性能缓存** | 智能的多层缓存系统，可根据用户权限和查询内容缓存结果，大幅降低延迟和 LLM API 成本。 |
| 🔌 **广泛的数据库支持** | 使用 SQLAlchemy 作为后端，开箱即用地支持 PostgreSQL, MySQL, SQLite, SQL Server 等多种主流数据库。 |
| 🌐 **兼容 OpenAI API** | 您可以轻松配置使用任何兼容 OpenAI API 格式的模型服务，无论是自托管模型还是其他云服务商。 |
| 🔍 **完整的可观测性** | 每个请求都会生成一个详细的执行轨迹 (Execution Trace)，包含从意图解析到最终结果的每一步，便于审计和调试。 |

## 🛠️ API 参考

我们提供了一个简洁而强大的 RESTful API。核心端点是 `/v1/query`。

### 端点: `POST /v1/query`

#### 请求头
- `X-API-Key`: (必需) 您的认证密钥。

#### 请求体
```json
{
  "query": "string" // 必需, 您的自然语言查询
}
```

#### 响应 (`200 OK`)
响应体是一个包含完整执行轨迹的 JSON 对象。关键字段包括：
- `id`: 唯一的追踪 ID。
- `request.nl`: 您的原始查询。
- `request.sql`: AI 生成的 SQL。
- `execution.data`: 查询结果数组。

> 详尽的 API 文档和示例，请参考我们启动服务后自动生成的 [Swagger UI](http://localhost:8000/docs)。

## 🤝 贡献指南

我们热烈欢迎来自社区的贡献！无论您是修复一个 bug、添加一个新功能，还是改进文档，您的帮助都至关重要。

### 如何开始
1.  **Fork** 这个仓库。
2.  创建一个新的分支 (`git checkout -b feature/your-amazing-feature`)。
3.  进行修改并提交 (`git commit -m 'feat: Add some amazing feature'`)。我们遵循 [Conventional Commits](https://www.conventionalcommits.org/) 规范。
4.  将您的分支推送到 Fork 的仓库 (`git push origin feature/your-amazing-feature`)。
5.  创建一个 **Pull Request**，并详细描述您的改动。

## 💬 加入我们的社区

有疑问？想要分享您的项目？或者只是想和志同道合的开发者交流？

-   **[加入我们的 QQ 群组](pass)**: 获取帮助、参与讨论和获取最新资讯。
-   **[开启一个 GitHub Issue](https://github.com/imbue-bit/pythagoras/issues)**: 提出功能建议或分享您的想法。
-   **[报告一个 Bug](https://github.com/your-org/pythagoras/issues/new/choose)**: 发现了问题？请告诉我们。

---

<div align="center">
  <p><strong>Pythagoras</strong> - 让数据对话如此简单。</p>
  <p><sub>根据 <a href="LICENSE">AGPL-3.0 许可证</a>发布。</sub></p>
</div>
