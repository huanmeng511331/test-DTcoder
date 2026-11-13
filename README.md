# 油气生产日报自动生成系统（演示项目）

面向油气生产管理场景的演示系统：管理每日油气生产数据（原油产量、天然气产量、注水量、能耗、停井数量、异常说明），支持录入/维护、核心指标环比计算、日报自动生成与浏览器预览、近 7 天趋势展示。

> 本项目为演示用途，所有业务数据均为**模拟数据**，不包含任何真实生产数据、人员信息或未脱敏文档。

## 技术栈

| 分层 | 技术 | 用途 |
| --- | --- | --- |
| 前端框架 | Vue 3 | 页面组件、状态与交互逻辑 |
| 前端工程化 | Vite | 本机开发服务器、热更新与生产构建 |
| 前端组件库 | Element Plus | 表格、表单、按钮、弹窗、菜单、标签等管理后台组件 |
| 图表 | ECharts | 趋势分析折线图 |
| 后端框架 | FastAPI | REST API、请求校验、自动接口文档 |
| 数据库 | SQLite | 本机单文件数据库（`backend/demo.db`），保存业务数据和演示初始数据 |

## 目录结构

```
├── frontend/                 # Vue 3 + Vite + Element Plus
│   ├── src/
│   │   ├── api/              # 调用后端接口（axios 封装）
│   │   ├── views/            # 业务页面（列表/录入/日报/趋势）
│   │   ├── layout/           # 页面框架布局
│   │   ├── router/           # 页面路由
│   │   └── utils/            # 公共工具
│   └── package.json
├── backend/                  # FastAPI
│   ├── app/
│   │   ├── main.py           # 应用入口
│   │   ├── config.py         # 配置与日报阈值
│   │   ├── database.py       # SQLite 连接与建库
│   │   ├── models/           # 数据模型（表结构）
│   │   ├── schemas/          # 请求/响应模型（Pydantic）
│   │   ├── routers/          # API 路由
│   │   └── services/         # 业务逻辑（记录 CRUD、日报生成、初始数据）
│   ├── tests/                # 单元测试（pytest）
│   ├── requirements.txt
│   └── demo.db               # SQLite 数据库（首次启动自动创建并写入初始数据）
└── README.md
```

## 环境要求

- Python 3.10+（开发验证环境：3.12）
- Node.js 18+ 与 npm（开发验证环境：Node 20.18 / npm 10.x）
- 无需安装独立数据库服务

## 安装与启动

### 1. 后端（FastAPI，端口 8000）

```bash
cd backend
python3 -m venv .venv
# Windows: python -m venv .venv && .venv\Scripts\activate
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

- 接口文档：http://localhost:8000/docs
- 健康检查：http://localhost:8000/health
- 首次启动自动创建 `backend/demo.db` 并写入最近 7 天的模拟生产数据；删除 `demo.db` 后重启即可重新生成。

### 2. 前端（Vue 3 + Vite，端口 5173）

```bash
cd frontend
npm install
npm run dev
```

- 最终访问地址：**http://localhost:5173**（前端页面，`/api` 请求由 Vite 代理到后端 8000 端口）
- 端口可按实际环境调整；如调整请同步修改 `frontend/vite.config.js` 中代理目标地址。

### 3. 运行后端单元测试（可选）

```bash
cd backend
.venv/bin/pytest -q
```

## 业务页面

| 路由 | 页面 | 说明 |
| --- | --- | --- |
| `/records` | 生产数据列表页 | 按日期展示原油、天然气、注水、能耗、停井数与状态标签；支持日期范围筛选、分页 |
| `/records/new`、`/records/:id/edit` | 数据录入/编辑页 | 录入单日生产数据与异常说明，含必填与非负数值校验；日期重复时后端返回 409 提示 |
| `/reports` | 生产日报页 | 选择日期生成日报：核心指标卡片、与前后日环比、突出提示（告警）、自动生成摘要、当日明细 |
| `/trends` | 趋势分析页（可选） | 近 7/14 天原油、天然气、注水量、能耗趋势折线图 |

## 后端 API 概览

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| GET | `/api/production-records` | 分页查询生产记录，支持 `start_date`、`end_date` 日期范围筛选 |
| GET | `/api/production-records/{id}` | 查询单条生产记录 |
| POST | `/api/production-records` | 新增单日生产数据（日期唯一，重复返回 409） |
| PUT | `/api/production-records/{id}` | 修改生产数据 |
| GET | `/api/daily-reports/{date}` | 计算并返回指定日期的结构化日报数据（无数据返回 404） |
| GET | `/api/production-trends` | 返回最近 N 天（默认 7，最大 30）趋势数据 |

字段：`id`、`production_date`、`crude_oil_output`（吨）、`natural_gas_output`（万立方米）、`water_injection`（立方米）、`energy_consumption`（万千瓦时）、`shutdown_well_count`（口）、`abnormal_description`、`created_at`、`updated_at`。

## 演示路径（完整业务闭环）

1. 打开 http://localhost:5173 进入生产数据列表页，查看近 7 天模拟数据。
2. 点击「录入生产数据」录入某日数据（或点「编辑」修改已有日期的原油、天然气、能耗数据）。
3. 在列表页点该日期行的「日报」，或在「生产日报」页选择该日期，点「生成日报」。
4. 查看核心指标卡片、日环比变化（▲/▼ 与百分比）、突出提示（异常说明/停井/指标超阈值）和自动生成的 3–5 条文字摘要。
5. 进入「趋势分析」页查看近 7 天原油产量趋势图。

内置演示数据中，昨日（列表第 2 行）原油产量较前一日下降约 5.2%（超过 5% 阈值）且含停井与异常说明，打开该日日报可直接看到告警与摘要效果。

## 日报生成规则

1. 对比当天与前一有数日的原油、天然气、注水、能耗，计算增减量与增减比例（日期允许不连续）。
2. 突出提示触发条件：异常说明非空、停井数大于 0、或指标较前一日变化超过阈值——原油/天然气下降 > 5%、注水量下降 > 10%、能耗上升 > 10%（阈值见 `backend/app/config.py`，可按需调整）。
3. 自动生成 3–5 条简短摘要，采用规则模板（无 AI 依赖，结果稳定可复现）。

## 生成说明

- 本项目代码（后端 FastAPI + SQLite、前端 Vue 3 + Vite + Element Plus、单元测试、README）由 **AiWork 辅助生成**；人工可按需调整日报阈值、指标单位与页面样式。
- 初始演示数据与日报摘要均为规则模板生成的模拟数据。

## 注意事项

- 不接入真实中石油生产系统、真实账号或真实敏感数据；未实现生产级认证、权限、消息队列与分布式架构。
- 初始数据的生产日期按后端启动当天往前推 7 天生成，日期取本机时区。
