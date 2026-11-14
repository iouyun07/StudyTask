# AI 开发日志（AI_DEV_LOG）

记录 AI 参与开发过程中的重要提示词、关键设计决策、发现的问题与人工判断。不粘贴完整对话。

---

## 2026-11-12 项目初始化

**提示词（摘要）**：以 `StudyTask` 为项目文件夹初始化 git 仓库，边操作边讲解；执行前需确认。

**关键决定**
- 仓库初始化用 `git init -b main`，分支名为 `main`；
- 提交身份 `laibin <laibin_cs@163.com>`（全局配置）；
- 远程仓库暂不配置，实验完成后再连接。

**问题与处理**
- 首次初始化误在 `C:\Users\31864` 建库（cmd 跨盘未加 `/d`），已删除并重建；
- `git config --global user.name"laibin"` 缺空格导致键名非法，已用带空格的写法重配并核对。

**人工判断**：由用户主导操作步骤，AI 只提供命令与解释。

---

## 2026-11-12 开发环境搭建

**问题与处理**
- 旧项目目录创建于沙箱会话之前，缺少 Low 完整性标签，AI 进程无法写入 → 用户删除旧目录，重新创建后继承标签，写入恢复；
- pip 官方文件源在本机 DNS 解析失败 → 改用国内镜像；
- 沙箱下 `tempfile.mkdtemp()` 生成的目录不可访问，导致 pip 报 `PermissionError` → 在项目外放置 `sitecustomize.py` 补丁（不改动 pip 源码）绕过；
- `python -m venv` 的 ensurepip 以隔离模式运行、忽略补丁 → 改为 `--without-pip` 创建后手动执行 `ensurepip`。

**结果**：`.venv` 创建成功，Flask 3.1.3 / Werkzeug 3.1.9 安装并验证可用。

---

## 2026-11-13 需求确认与方案设计

**提示词（摘要）**：严格依据《附录A：实验一软件需求规格说明书》完成可本地运行的 Web 应用；先列实施步骤与验收清单，确认后再写代码；不增加范围外功能。

**关键决定**
- 技术栈：Flask + 标准库 `sqlite3` + Jinja2，服务端渲染，无前端框架、无 JavaScript 依赖；
- 删除确认采用独立确认页（GET 确认 → POST 删除），不依赖浏览器弹窗；
- 逾期/即将到期在查询时按当天日期实时计算，不落库，避免过期标记；
- 完成率取整数四舍五入，任务总数为 0 时显示 0%；
- “即将到期”口径：未完成且 `今天 ≤ 截止日期 ≤ 今天 + 3 天`（含今天）；
- “逾期”口径：未完成且截止日期早于今天；已完成任务不显示任何标记；
- 任务 ID 使用自增整数（SRS 允许整数或 UUID）。

**人工判断**
- 用户确认上述三个业务口径；
- 用户提供第二章 2.5 节 T1—T10 测试用例原文，测试按该表设计；
- 目录名保持 `StudyTask`，不改为“班级_学号_项目代号”；
- 实验报告暂缓，待功能完成后再写。

---

## 2026-11-13 功能实现与自动化测试

**实现内容**
- 数据层：`schema.sql` 建 `tasks` 表（含优先级/状态的 CHECK 约束与筛选索引），`db.py` 提供连接与初始化；
- 业务层：`tasks.py` 纯函数实现表单校验、逾期/即将到期判定、完成率统计；
- 页面层：列表（统计卡片 + 筛选 + 表格）、新建、详情、编辑、删除确认、404；
- 测试：`tests/test_studytask.py` 共 15 条用例，覆盖 T1–T10 与若干校验。

**关键设计决策**
- 筛选在 SQL 层用 `WHERE` 组合，课程下拉选项来自库中已有的课程；
- 统计卡片始终按全部任务计算，不受筛选影响（筛选后的条数体现在列表中）；
- 状态调整用 `POST /tasks/<id>/status` 配合普通表单按钮，提交后跳回来源页（`next` 参数只允许站内相对路径）；
- 删除确认页为独立 GET 页面，POST 才真正执行删除，全程不依赖 JavaScript。

**问题与处理**
- venv 中没有 pytest，用阿里云镜像补装 `pytest 9.2.0`；
- pytest 首次运行报 `PytestCacheWarning`（本机沙箱无法创建缓存临时目录）→ 在 `pytest.ini` 加 `-p no:cacheprovider`，复跑无警告；
- 该次运行残留一个不可读的 `pytest-cache-files-*` 目录，需人工删除（已记录在案，不影响仓库内容）；
- 真实服务器走查时发现：从工作区根目录启动 `python app.py`，数据库会被建到“启动目录/instance”而不是项目目录 → 改为相对 `app.py` 所在目录固定 `instance/studytask.db`，重启验证后库文件位置正确。

**结果**
- `.venv\Scripts\python.exe -m pytest -v` → **15 passed in 0.60s**；
- 真实 HTTP 验证（`python app.py` 后访问 `http://127.0.0.1:5000`）：首页 200、新建任务 302 跳转后列表可见、任务详情 200、不存在的任务 404；
- T10 真实重启验证：停止服务再启动，已保存任务仍可查询；测试数据已清理，数据库恢复为空。

---

## 2026-11-14 远程仓库与线上部署

**提示词（摘要）**：实验要求把项目部署到服务器；先用免费 PaaS 试水，询问具体操作。

**关键决定**
- 源码托管选 GitHub：PythonAnywhere 免费账号的对外访问有白名单，包含 GitHub 而不含 Gitee，服务器 `git clone` 只能走 GitHub；
- 平台选 PythonAnywhere 免费版：磁盘持久，SQLite 数据在线上不会因重启丢失，T10 在线上同样成立；Render 免费实例磁盘临时，会清空数据，仅作备选；
- 线上用 Manual configuration 配置（不选 Flask 模板，避免模板生成的文件覆盖现有结构）。

**过程**
- 本地 5 次提交推送到 <https://github.com/iouyun07/StudyTask>（main 分支）；
- 服务器 clone 后执行 `mkvirtualenv --python=/usr/bin/python3.13 studytask`，再 `pip install -r requirements.txt`（安装 12 个包）；
- WSGI 文件写入 `sys.path.insert(0, "/home/iouyun07/StudyTask")` 与 `from app import app as application`；
- Static files 映射：`/static/` → `/home/iouyun07/StudyTask/static`。

**验证**
- 服务器端 `python -m pytest -q` → **15 passed in 3.91s**；
- 线上站点 <https://iouyun07.pythonanywhere.com> 返回 200，首页统计（3 项 / 1 项已完成 / 33%）、逾期与「即将到期」标识显示正常；
- 用户人工走查确认可用。

**人工判断**：账号注册与服务器命令均由用户本人执行，AI 不接触账号密码与凭据。
