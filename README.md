# StudyTask 个人学习任务管理系统

单用户、本地运行的 Web 学习任务管理应用。后端 Python + Flask + SQLite，前端为服务端渲染的 HTML 页面，不需要联网、不需要登录。

> 状态：实验一开发中。本文件在交付前会补全“测试记录”和“已知限制”的最终结论。

## 功能

| 编号 | 功能 |
|---|---|
| FR-01 | 新建任务，校验名称、课程、截止日期 |
| FR-02 | 列表展示与任务详情页 |
| FR-03 | 编辑任务 |
| FR-04 | 删除任务（二次确认） |
| FR-05 | 状态调整：待完成 / 进行中 / 已完成 |
| FR-06 | 按课程、状态、优先级筛选（可组合） |
| FR-07 | 逾期、即将到期标记 |
| FR-08 | 首页统计：总数、已完成数、完成率 |
| FR-09 | 数据本地持久化 |
| FR-10 | 中文界面与错误提示 |

## 环境要求

- Windows 10/11（其他系统同样可用，路径写法略有不同）
- Python 3.11 及以上（开发环境为 3.13.6）
- 不需要数据库服务，SQLite 随 Python 自带

## 快速开始（从零）

```bat
:: 1. 进入项目目录
cd /d D:\install\software\StudyTask

:: 2. 创建虚拟环境
python -m venv .venv

:: 3. 激活虚拟环境
.venv\Scripts\activate

:: 4. 安装依赖
pip install -r requirements.txt

:: 5. 启动应用
python app.py
```

浏览器打开 <http://127.0.0.1:5000>。

> macOS / Linux 下激活命令为 `source .venv/bin/activate`，其余相同。
> 如果 pip 下载缓慢，可临时指定国内镜像：
> `pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/`

## 运行

```bat
.venv\Scripts\python.exe app.py
```

默认监听 `127.0.0.1:5000`。首次启动会自动创建数据库文件 `instance/studytask.db`。

## 测试

```bat
.venv\Scripts\python.exe -m pytest -q
```

测试使用独立的临时数据库，不会影响 `instance/studytask.db` 中的真实数据。

## 项目结构

```
StudyTask/
├─ app.py              # 应用入口与路由
├─ db.py               # 数据库连接与初始化
├─ schema.sql          # 建表语句
├─ tasks.py            # 业务逻辑：校验、逾期判定、统计
├─ templates/          # 页面模板（Jinja2）
├─ static/             # 样式文件
├─ tests/              # 自动化测试
├─ requirements.txt    # 依赖清单
├─ README.md
└─ AI_DEV_LOG.md       # AI 辅助开发记录
```

## 数据存储

- 数据库：SQLite 单文件，位置 `instance/studytask.db`；
- 该文件属于运行数据，已由 `.gitignore` 排除，不会提交到仓库；
- 备份数据只需复制该文件。

## 已知限制

- 单用户使用，无登录与权限控制（需求范围外）；
- SQLite 单文件，不适合高并发写入；
- 任务列表不分页，按需求规模（约 200 条）设计；
- 日期以本机当天为准，不做时区转换；
- 逾期/即将到期只做页面标记，不发送任何提醒；
- 未做移动端适配。
