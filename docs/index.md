# Pythagoras

## 介绍

Pythagoras 是一种新型的数据交互接口 (Data Interaction Interface, DII)，它从根本上改变了人类与结构化数据协作的方式。通过将自然语言的直观性与 SQL 数据库的强大功能相结合，Pythagoras 使任何人——从数据分析师到业务主管——都能以对话的形式探索、分析和操作数据。

该接口通过一个简单、一致的 RESTful API 暴露其功能，使其能够轻松集成到任何现代应用程序、BI 工具或自动化工作流中。

## 核心概念

Pythagoras 的工作流围绕着几个核心概念构建，这些概念共同确保了每一次交互都是安全、高效和智能的。

-   **查询意图**: 我们不只是逐字翻译。Pythagoras 会解析用户请求背后的真实意图。例如，“上个月谁是我们最好的销售？” 这个查询会被理解为需要查找销售额最高的员工，而不是简单地寻找名为“最好”的销售人员。

-   **数据脉络**: 在启动时，Pythagoras 会对连接的数据库进行一次**模式感应 (Schema Ingestion)**，构建一个包含表、列、类型和关系的内部知识图谱。这个“数据脉络”是模型理解数据结构、生成精确查询的基础。

-   **执行轨迹**: 每个通过 Pythagoras 的请求都会生成一个完整的“执行轨迹”。这不仅包括原始查询、生成的 SQL 和结果，还包括权限验证、缓存决策和性能指标。这为审计、调试和性能调优提供了无与伦比的透明度。

-   **权限边界**: 安全是我们的首要设计原则。每个 API 密钥都与一个或多个角色绑定，这些角色定义了清晰的“权限边界”。系统确保用户的任何请求，无论多么复杂，都不会逾越这些边界。

## Pythagoras 模型：Socrates-SQL

为了在自然语言到 SQL (NL2SQL) 任务上实现前所未有的准确性，我们开发了 Socrates-SQL，这是一个专为此任务设计的专有模型。

Socrates-v2 的基础是我们对一个高度优化的开源模型 Socrates-nano (0.6B 参数) 进行的微调。我们创新的训练方法受到了物理信息神经网络 (PINNs) 的启发。在传统训练中，模型仅从“语言-SQL”对中学习。而我们的方法引入了一个结构化约束层 (Structured Constraint Layer)。

这个约束层在训练过程中充当了一个“虚拟数据库”。它会实时验证模型生成的 SQL 是否在语法上有效、是否符合数据库模式的逻辑约束（如数据类型、外键关系）。这迫使模型不仅学习语言模式，还要内化 SQL 和数据库结构的“物理规则”。

这种方法使得 Socrates-v2 即使在面对模糊查询、复杂的连接和特定数据库方言时，也能表现出卓越的鲁棒性和准确性，达到了该领域的最先进水平 (State-of-the-Art, SOTA)。

---

## API 参考

### 认证

所有 API 请求都需要通过 `X-API-Key` HTTP 请求头进行认证。您的 API 密钥携带了您的身份和角色信息。

```http
POST /v1/query
Host: api.pythagoras.ai
Content-Type: application/json
X-API-Key: sk-proj-xxxxxxxxxxxxxxxxxxxxxxxx
```

未能提供有效密钥将导致 `403 Forbidden` 响应。

### 端点

#### `POST /v1/query`

这是执行所有数据交互的主要端点。它接收一个自然语言查询，并返回一个包含完整执行轨迹的响应。

##### 请求体

| 字段    | 类型   | 必须 | 描述                                                                                              |
|---------|--------|------|---------------------------------------------------------------------------------------------------|
| `query` | `string` | 是   | 要执行的自然语言查询。查询可以是一个简单的问题、一个分析指令，或是一个数据修改请求。               |
| `mode`  | `string` | 否   | (即将推出) 查询模式，如 `"exploratory"` 或 `"production"`，用于影响缓存策略和资源分配。默认为 `"production"`。 |

**示例请求:**
```json
{
  "query": "Compare the average order value between customers in New York and California for the last quarter."
}
```

##### 响应体

| 字段            | 类型     | 描述                                                                                                                                                               |
|-----------------|----------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `id`            | `string`   | 此次查询的唯一标识符，格式为 `py-trace-xxxxxxxx`。可用于支持和调试。                                                                                                    |
| `object`        | `string`   | 对象类型，始终为 `"query.result"`。                                                                                                                                      |
| `created`       | `integer`  | 查询创建时间的 Unix 时间戳。                                                                                                                                       |
| `source`        | `string`   | 结果来源，`"live"` 表示实时查询数据库，`"cache"` 表示从缓存中获取。                                                                                                 |
| `request`       | `object`   | 包含原始请求的详细信息。                                                                                                                                             |
| `request.nl`    | `string`   | 用户提交的原始自然语言查询。                                                                                                                                       |
| `request.sql`   | `string`   | Socrates-v2 模型为该请求生成的 SQL 语句。                                                                                                                            |
| `execution`     | `object`   | 数据库执行的结果。                                                                                                                                                   |
| `execution.status` | `string` | 执行状态，`"succeeded"` 或 `"failed"`。                                                                                                                                  |
| `execution.data`   | `array`  | (如果成功且有返回行) 一个对象数组，每个对象代表一行数据。对于无返回值的操作（如 `UPDATE`），此字段为 `null`。                                                |
| `execution.metadata` | `object` | 包含执行元数据，如受影响的行数和查询延迟。                                                                                                                     |
| `usage`         | `object`   | (未来规划) 关于此次请求的资源使用情况，例如消耗的计算单元。                                                                                                        |


**成功响应示例:**
```json
{
  "id": "py-trace-ab12cd34ef56",
  "object": "query.result",
  "created": 1678886400,
  "source": "live",
  "request": {
    "nl": "What is the total revenue per product category?",
    "sql": "SELECT category, SUM(price * quantity) as total_revenue FROM products JOIN orders ON products.id = orders.product_id GROUP BY category ORDER BY total_revenue DESC"
  },
  "execution": {
    "status": "succeeded",
    "data": [
      {
        "category": "Electronics",
        "total_revenue": 125000.50
      },
      {
        "category": "Books",
        "total_revenue": 78000.75
      }
    ],
    "metadata": {
      "rows_returned": 2,
      "latency_ms": 125
    }
  }
}
```

#### `GET /health`

用于监控服务可用性的端点。

##### 响应

-   `200 OK`: `{"status": "available"}`
-   `503 Service Unavailable`: `{"status": "degraded", "details": "Database connection failed"}`

### 错误处理

Pythagoras API 使用标准的 HTTP 状态码来指示请求的结果。当发生错误时，响应体将包含一个标准化的错误对象。

| 字段      | 类型     | 描述                                                           |
|-----------|----------|----------------------------------------------------------------|
| `error`   | `object` | 包含错误信息的对象。                                           |
| `error.code` | `string` | 一个机器可读的错误代码，例如 `permission_denied`。              |
| `error.message` | `string` | 对错误的详细、人类可读的描述。                             |
| `error.type`  | `string` | 错误的类型，例如 `api_error`, `authentication_error`。 |

**错误响应示例 (`403 Forbidden`):**
```json
{
  "error": {
    "code": "permission_denied",
    "message": "Access to table 'employees' is outside of your defined permission boundary.",
    "type": "api_error"
  }
}
```

---
## 高级主题

### 缓存行为

为了最大限度地提高性能和效率，Pythagoras 实现了一个智能的多层缓存系统。当您发出查询时，系统会基于您的查询文本和您的**权限哈希 (Permission Hash)** 生成一个唯一的缓存键。

这意味着，即使用户A和用户B发出完全相同的自然语言查询，如果他们的角色权限不同，他们也将访问不同的缓存条目。这保证了数据隔离和安全性，同时为具有相同权限的团队提供了共享缓存的性能优势。

默认的缓存 TTL (Time-To-Live) 是 3600 秒，但可以通过请求头进行覆盖（功能即将上线）。

### 安全与合规

Pythagoras 的设计将安全性置于核心。

-   **端到端加密**: 所有传输中的数据都使用 TLS 1.3 进行加密。
-   **无状态架构**: API 服务器本身不存储任何用户数据，这减少了攻击面。
-   **执行轨迹审计**: 所有的 `Execution Trace` 都可以被导出到您的日志记录或 SIEM 系统中，以满足合规性要求，如 SOC 2 或 GDPR。
