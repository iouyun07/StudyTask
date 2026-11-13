-- StudyTask 数据库结构
-- 说明：任务 ID 使用自增整数；日期以 YYYY-MM-DD 文本保存；
-- 逾期/即将到期属于展示状态，按当天日期实时计算，不落库。

CREATE TABLE IF NOT EXISTS tasks (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT    NOT NULL,                       -- 任务名称，1-100 字
    course      TEXT    NOT NULL,                       -- 所属课程，1-60 字
    description TEXT    NOT NULL DEFAULT '',            -- 任务描述，可为空，最多 1000 字
    due_date    TEXT    NOT NULL,                       -- 截止日期，YYYY-MM-DD
    priority    TEXT    NOT NULL DEFAULT '中',          -- 高 / 中 / 低
    status      TEXT    NOT NULL DEFAULT '待完成',      -- 待完成 / 进行中 / 已完成
    created_at  TEXT    NOT NULL,                       -- 创建时间
    updated_at  TEXT    NOT NULL,                       -- 更新时间
    CHECK (priority IN ('高', '中', '低')),
    CHECK (status IN ('待完成', '进行中', '已完成'))
);

CREATE INDEX IF NOT EXISTS idx_tasks_course   ON tasks (course);
CREATE INDEX IF NOT EXISTS idx_tasks_status   ON tasks (status);
CREATE INDEX IF NOT EXISTS idx_tasks_priority ON tasks (priority);
