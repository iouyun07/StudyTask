# StudyTask 个人学习任务管理系统

单用户、本地运行的 Web 学习任务管理应用。后端 Python + Flask + SQLite，前端为服务端渲染的 HTML 页面，不需要联网、不需要登录。

> 状态：实验一功能已完成，自动化测试覆盖 T1–T10（15 条用例全部通过，见「测试记录」）。

## 在线访问

- 演示地址：<https://iouyun07.pythonanywhere.com>
- 代码仓库：<https://github.com/iouyun07/StudyTask>
- 部署方式：PythonAnywhere 免费版（Manual configuration + WSGI + virtualenv），代码从 GitHub 仓库克隆；
- 线上与本地是同一套代码；线上数据保存在服务器 `~/StudyTask/instance/studytask.db`，服务重启不丢失，与本地数据库互相独立。

### 部署说明（PythonAnywhere）

1. Bash 控制台执行：`git clone https://github.com/iouyun07/StudyTask.git` 并 `cd StudyTask`；
2. 创建并激活虚拟环境：`mkvirtualenv --python=/usr/bin/python3.13 studytask`；
3. 安装依赖：`pip install -r requirements.txt`；
4. Web 标签 → Add a new web app → **Manual configuration** → Python 3.13；
   - Source code / Working directory：`/home/iouyun07/StudyTask`
   - Virtualenv：`/home/iouyun07/.virtualenvs/studytask`
5. 编辑 WSGI 配置文件（`/var/www/iouyun07_pythonanywhere_com_wsgi.py`）：

   ```python
   import sys

   path = "/home/iouyun07/StudyTask"
   if path not in sys.path:
       sys.path.insert(0, path)

   from app import app as application
   ```

6. Static files：URL `/static/` → Directory `/home/iouyun07/StudyTask/static`；
7. 点 Reload，访问演示地址。

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

## 测试记录

- 执行日期：2026-11-13
- 执行环境：Windows 11 / Python 3.13.6 / pytest 9.2.0
- 执行命令：`.venv\Scripts\python.exe -m pytest -v`
- 结果：**15 passed**（0 失败）
- 线上复跑（PythonAnywhere，2026-11-14，Python 3.13.1 / pytest 9.2.0）：`python -m pytest -q` → **15 passed in 3.91s**

| 用例 | 测试内容 | 对应测试函数 | 结果 |
|---|---|---|---|
| T1 | 新建任务（课程「数据结构」、次日截止、高优先级），列表显示新增任务 | `test_t1_create_task_shows_in_list` | 通过 |
| T2 | 名称为空提交，提示错误且不产生脏数据 | `test_t2_empty_name_rejected_without_dirty_data` | 通过 |
| T3 | 修改描述与优先级，刷新后保留 | `test_t3_edit_description_and_priority_persists` | 通过 |
| T4 | 待完成 → 进行中 → 已完成，状态逐次正确更新 | `test_t4_status_transitions`、`test_t4_status_rejects_unknown_value` | 通过 |
| T5 | 按课程、状态、优先级筛选（含组合筛选），结果只含匹配任务 | `test_t5_filter_by_course_status_priority` | 通过 |
| T6 | 昨日到期且未完成，显示「逾期」标识；已完成的旧任务不显示 | `test_t6_overdue_badge`、`test_t6_completed_task_has_no_overdue_badge` | 通过 |
| T7 | 明日到期且未完成，显示「即将到期」标识 | `test_t7_due_soon_badge` | 通过 |
| T8 | 创建 5 项、完成 2 项，总数 5、完成数 2、完成率 40% | `test_t8_stats_total_done_rate`、`test_stats_zero_when_empty` | 通过 |
| T9 | 打开删除确认页不删除，确认后才删除 | `test_t9_delete_keeps_data_until_confirmed` | 通过 |
| T10 | 关闭并重新启动系统，已保存数据仍可查询 | `test_t10_data_survives_restart` | 通过 |

补充用例：非法日期被拒绝（`test_invalid_due_date_rejected`）、不存在的任务返回 404（`test_missing_task_returns_404`）。

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
├─ pytest.ini          # pytest 配置
├─ requirements.txt    # 依赖清单
├─ README.md
├─ AI_DEV_LOG.md       # AI 辅助开发记录
└─ docs/               # 交付文档
   ├─ 需求验收表.md / .docx
   └─ 实验报告.md / .docx
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
