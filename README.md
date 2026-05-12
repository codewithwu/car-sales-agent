# car-sales-agent

基于 LangChain/LangGraph 的汽车销售数据分析助手，结合规则引擎与 LLM 实现自然语言查询汽车库存、销售业绩等功能。

## 特性

- **意图识别**：基于规则引擎快速识别用户查询意图（品牌、车型、颜色、价格区间、销售员等）
- **混合查询**：规则引擎无法处理时，自动切换到 LLM Agent 进行语义理解
- **自然语言接口**：用户可以用自然语言查询汽车数据，如"丰田轿车有哪些"、"价格在5万至8万之间"等

## 技术架构

### Agent 工作流程图

```
                    ┌─────────────────┐
                    │      START      │
                    └────────┬────────┘
                             │
                             ▼
               ┌─────────────────────────┐
               │  rule_based_query_node  │  ← 规则引擎解析用户输入
               └────────────┬────────────┘
                            │
                   is_true? │
              ┌─────────────┴─────────────┐
              │                           │
          Pass                         Fail
              │                           │
              ▼                           ▼
    ┌─────────────────┐      ┌──────────────────┐
    │    call_llm      │      │   call_llm_tool   │  ← LLM 带工具解析
    └────────┬─────────┘      └─────────┬─────────┘
             │                          │
             │                 is_true? │
             │            ┌────────────┴────────────┐
             │            │                         │
             │        Pass                       Fail
             │            │                         │
             │            ▼                         ▼
             │   ┌─────────────────┐    ┌─────────────────┐
             │   │    call_llm     │    │  false_message  │
             │   └────────┬────────┘    └────────┬────────┘
             │            │                     │
             │            └──────────┬──────────┘
             │                       │
             └───────────┬───────────┘
                         │
                         ▼
                    ┌─────────┐
                    │   END   │
                    └─────────┘
```

### 核心节点说明

| 节点 | 功能 |
|------|------|
| `rule_based_query_node` | 规则引擎解析用户输入，提取品牌/车型/颜色/价格等参数 |
| `call_llm` | 直接调用 LLM 生成自然语言回复 |
| `call_llm_tool` | 调用 LLM 并绑定工具进行语义解析 |
| `false_message` | 无法理解时的回复 |

### 条件边

| 边 | 条件 | 目标 |
|----|------|------|
| `rule_based_query_node → call_llm` | `is_true == True` | 规则引擎成功匹配 |
| `rule_based_query_node → call_llm_tool` | `is_true == False` | 规则引擎无法匹配 |
| `call_llm_tool → call_llm` | `is_true == True` | 工具调用成功 |
| `call_llm_tool → false_message` | `is_true == False` | 工具调用失败 |

## 项目结构

```
car-sales-agent/
├── src/
│   ├── main.py              # FastAPI 服务入口
│   ├── api/
│   │   └── main.py          # API 接口
│   ├── agents/
│   │   ├── __init__.py      # 模块导出
│   │   ├── data.py          # 模拟数据生成（带缓存）
│   │   ├── graph.py         # LangGraph StateGraph
│   │   ├── nodes.py         # 图节点函数
│   │   ├── rule_engine.py   # 规则引擎
│   │   ├── state.py         # State 类定义
│   │   └── tools.py         # LangChain tools
│   └── templates/
│       └── index.html       # 前端聊天页面
├── pyproject.toml
└── README.md
```

## 快速开始

### 1. 安装依赖

```bash
uv sync
```

### 2. 启动服务

```bash
uv run python src/main.py
```

### 3. 访问应用

- 聊天界面：http://localhost:8000
- API 接口：http://localhost:8000/docs

![聊天界面截图](image.png)

### 4. API 调用示例

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "丰田轿车有哪些？"}'
```

## 环境变量

创建 `.env` 文件，配置 LLM API：

```env
LONGCAT_API_KEY=your_api_key
LONGCAT_BASEURL=your_base_url
LONGCAT_MODEL_NAME=your_model_name
```

## 可查询字段

| 字段 | 示例 |
|------|------|
| 品牌 | 丰田、本田、宝马、奔驰等 |
| 车型 | 轿车、SUV、卡车、两厢车等 |
| 颜色 | 红色、蓝色、黑色、白色等 |
| 价格 | "5万至8万"、"不超过6万" |
| 销售员 | 张三、李四、王五等 |

## 示例问题

- "查询丰田轿车的价格"
- "红色SUV有哪些？"
- "价格在5万到8万之间的有哪些？"
- "哪个销售员卖得最多？"