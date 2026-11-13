## Step 4: 模块—接口映射

## 4. 功能模块与接口设计

### 4.1 模块—接口映射

接口分类说明：

- **oneapi（前端接口）**：全部 7 个 HTTP 接口，路径前缀 /api，与需求 6.4 完全一致。
- **对外 OpenAPI**：本项不适用，原因：无外部系统调用方（需求 3.3）。
- **内部接口**：本项不适用，原因：单体应用，无跨服务/跨应用调用。
- **集成接口**：本项不适用，原因：无外部系统依赖。
- **任务接口**：启动初始化任务 T01（建库与种子，无 HTTP 入口）。

| 接口编号 | 接口名称 | 类型 | 方法/触发方式 | 路径/方法签名 | 所属模块 | 对应功能点 |
|---|---|---|---|---|---|---|
| W01 | 隐患列表查询 | oneapi | GET | /api/hazards | 隐患管理 | F01、F02、F12 |
| W02 | 隐患上报 | oneapi | POST | /api/hazards | 隐患管理 | F03、F13 |
| W03 | 隐患详情查询 | oneapi | GET | /api/hazards/{id} | 隐患管理 | F04、F09、F12 |
| W04 | 审核并分派 | oneapi | PATCH | /api/hazards/{id}/assign | 隐患管理 | F05、F10、F13 |
| W05 | 提交整改 | oneapi | PATCH | /api/hazards/{id}/rectification | 隐患管理 | F06、F10、F13 |
| W06 | 验收并关闭/退回 | oneapi | PATCH | /api/hazards/{id}/acceptance | 隐患管理 | F07、F10、F12、F13 |
| W07 | 隐患统计查询 | oneapi | GET | /api/hazards/statistics | 统计 | F08、F12 |
| T01 | 启动建库与种子初始化 | 任务 | 应用启动钩子（FastAPI lifespan） | hse-backend.StartupInitializer.initialize() | 公共基础 | F11 |

功能点覆盖说明：

| 功能点 | 落点 |
|---|---|
| F01/F02 | W01 |
| F03 | W02（编号生成由公共基础 IdGenerator 支撑） |
| F04/F09 | W03 |
| F05/F06/F07 | W04/W05/W06 |
| F08 | W07 |
| F10 | 前端页面逻辑（角色×状态显隐，见 2.1/4.2.3）；operator 经 W04/W05/W06 入参提交并落流转记录 |
| F11 | T01 |
| F12 | W01/W03/W07 的 overdue 派生计算与超期统计 |
| F13 | 前端表单校验与组件反馈（2.1/4.2.3）+ W02/W04/W05/W06 服务端入参校验 |
| F14 | 文档交付项（README），无运行时接口，交付要求见需求 3.1.7 与 PRD 4.4 |
