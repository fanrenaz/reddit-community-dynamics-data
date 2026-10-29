# Reddit Community Dynamics Reference Dataset

面向社区互动建模与社会模拟研究的数据参考包：四个 Reddit 社区在 **2026 年 1 月**的帖子与评论，保留原始 JSONL 记录。

这份数据用于共同理解事件、用户、文本、时间和回复关系，讨论模型的输入输出，并开展初步实验。它是指定社区的月度归档切片，**不是全站随机样本，也不保证覆盖 Reddit 上曾经存在的全部内容**。

## 数据概览

时间范围以记录的 `created_utc` 为准：

```text
2026-01-01T00:00:00Z <= created_utc < 2026-02-01T00:00:00Z
```

| 社区 | 帖子 | 评论 | 不同作者名 | 跨日重复作者名 |
|---|---:|---:|---:|---:|
| r/askscience | 21,982 | 6,629 | 4,513 | 1,103 |
| r/changemyview | 3,180 | 195,016 | 33,509 | 11,921 |
| r/technology | 3,474 | 265,475 | 88,108 | 29,488 |
| r/CasualConversation | 8,353 | 132,426 | 44,933 | 13,626 |
| **合计** | **36,989** | **599,546** | — | — |

作者统计排除缺失作者及 `[deleted]`、`[removed]` 占位值，包含机器人账号。跨日重复指在至少两个不同 UTC 日期出现。各社区之间的作者可能重叠，因此不合计作者数。

- JSONL 数据总计 **1,224,778,628 bytes**，约 1.22 GB。
- ZIP 数据包 **127,512,985 bytes**，约 128 MB。
- 四个社区分别提供科学问答、观点辩论、科技讨论、日常交流的参考场景；实际归档内容包含移除记录、广告和其他噪声。

## 下载

完整数据放在 [v2026-01.1 Release](https://github.com/fanrenaz/reddit-community-dynamics-data/releases/tag/v2026-01.1)。如果仓库是私有的，需要具有仓库访问权限并登录 GitHub。

使用 GitHub CLI：

```bash
gh auth login
gh repo clone fanrenaz/reddit-community-dynamics-data
cd reddit-community-dynamics-data
gh release download v2026-01.1 --repo fanrenaz/reddit-community-dynamics-data --pattern "four_communities_2026-01_v1.zip" --dir downloads
python scripts/verify_dataset.py --archive downloads/four_communities_2026-01_v1.zip
python -m zipfile -e downloads/four_communities_2026-01_v1.zip data
```

也可以直接在 Release 页面下载 ZIP，再解压。`git clone` 只下载说明、元数据和校验脚本，**不会自动下载完整数据包**。

ZIP 的 SHA-256：

```text
c80b9cd21a09313e5cfc17c70b38111b45357aa1db0a0af77e48446ca6b49403
```

部分 JSONL 超过 GitHub 普通 Git 仓库的 100 MiB 单文件限制，因此通过 Releases 分发完整数据，避免把大文件写入 Git 历史。参见 [GitHub 大文件说明](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github)。

## 目录结构

仓库内容：

```text
README.md
metadata/
  manifest.json
  askscience/manifest.json
  changemyview/manifest.json
  technology/manifest.json
  CasualConversation/manifest.json
scripts/
  verify_dataset.py
```

数据包解压后：

```text
data/four_communities_2026-01_v1/
  manifest.json
  askscience/
    submissions.jsonl
    comments.jsonl
    manifest.json
  changemyview/
    submissions.jsonl
    comments.jsonl
    manifest.json
  technology/
    submissions.jsonl
    comments.jsonl
    manifest.json
  CasualConversation/
    submissions.jsonl
    comments.jsonl
    manifest.json
```

## 抽取规则与来源

来源是 [Arctic Shift](https://github.com/ArthurHeitmann/arctic_shift) 的月度归档 `RS_2026-01.zst` 和 `RC_2026-01.zst`。

1. 流式读取两份月度归档。
2. 按 `subreddit` 选择上述四个社区，匹配时忽略大小写。
3. 检查记录的 `created_utc` 位于上述 UTC 月份区间。
4. 将入选记录的原始 JSON 行写入对应社区的文件。

没有按正文、得分、活跃程度或讨论完整性过滤；没有添加记录字段、补齐缺失字段、匿名化或改写内容。抽取时未发现重复 ID；重复检查失败会使任务报错，而不是静默去重。帖子和评论分别按其自身创建时间选择，**不是先选主帖，再提取完整生命周期的讨论串**。

[总 manifest](metadata/manifest.json) 记录来源文件、范围、保存方式和各社区统计。各社区 manifest 还包含逐日数量、观察到的字段类型及出现次数、最大的讨论串、关联缺失数量，以及 JSONL 的记录数、字节数和 SHA-256。字段统计描述的是这份切片，不是全量 Reddit 的固定 schema。

## 核心数据结构

一行是一个 JSON 对象。字段可能缺失，或者取 `null`、空字符串、空数组及空对象；这些情况保留原样。

### 帖子：`submissions.jsonl`

| 字段 | 含义 |
|---|---|
| `id` | 帖子短 ID |
| `name` | 带类型前缀的帖子 ID，`t3_<id>` |
| `author` / `author_fullname` | 作者名 / 用户标识，可能缺失或为占位值 |
| `subreddit` / `subreddit_id` | 所属社区 |
| `title` / `selftext` | 标题 / 文字正文；正文可能为空或为移除提示 |
| `created_utc` | 创建时间，Unix 秒级时间戳 |
| `retrieved_on` | 归档抓取时间 |
| `score` / `num_comments` | 抓取时的分数 / 评论数 |
| `url` / `permalink` | 链接目标 / Reddit 路径 |
| `media` / `media_metadata` / `preview` | 可选的嵌套媒体信息，不能据此认定媒体文件本体已下载 |
| `removed_by_category` | 归档记录中的移除类别 |

### 评论：`comments.jsonl`

| 字段 | 含义 |
|---|---|
| `id` / `name` | 短 ID / 带 `t1_` 前缀的评论 ID |
| `author` | 评论作者 |
| `body` | 评论文本 |
| `link_id` | 所属主帖的 `t3_` ID |
| `parent_id` | 直接回复的对象：`t3_` 为主帖，`t1_` 为评论 |
| `created_utc` / `retrieved_on` | 创建时间 / 抓取时间 |
| `score` | 抓取时的分数 |
| `is_submitter` | 评论作者是否为主帖作者 |

以下仅为关系示意，ID 和正文均为演示值：

```json
{"name":"t3_postA","title":"问题","selftext":"主帖正文"}
{"name":"t1_commentB","link_id":"t3_postA","parent_id":"t3_postA","body":"一级回复"}
{"name":"t1_commentC","link_id":"t3_postA","parent_id":"t1_commentB","body":"回复 commentB"}
```

按 `link_id` 聚合同一讨论串，再用 `parent_id` 连接父子节点。不要把 `replies` 字段当成已包含完整子评论的讨论树。

## 最小读取示例

只使用 Python 标准库，Python 3.9 或以上：

```python
import json
from pathlib import Path

root = Path("data/four_communities_2026-01_v1/changemyview")

def records(path):
    with path.open(encoding="utf-8") as stream:
        for line in stream:
            yield json.loads(line)

first_post = next(records(root / "submissions.jsonl"))
print(first_post.keys())
print(first_post["name"], first_post["title"])

# 用评论找到一个主帖也在当前切片中的讨论串。
posts = {post["name"]: post for post in records(root / "submissions.jsonl")}
first_comment = next(
    comment for comment in records(root / "comments.jsonl")
    if comment["link_id"] in posts
)
thread_id = first_comment["link_id"]
thread = [
    comment for comment in records(root / "comments.jsonl")
    if comment["link_id"] == thread_id
]
thread.sort(key=lambda comment: (comment["created_utc"], comment["id"]))
nodes = {thread_id: posts[thread_id]}
nodes.update({comment["name"]: comment for comment in thread})

for comment in thread[:10]:
    print(comment["name"], "->", comment["parent_id"],
          "parent_present=", comment["parent_id"] in nodes)
```

也可以校验解压后的文件：

```bash
python scripts/verify_dataset.py --root data/four_communities_2026-01_v1
```

## 已知数据特点与建模边界

- **askscience 的移除记录很多。** 21,982 条帖子中有 21,977 条被移除类别或删除正文标记命中，部分常见标题是重复广告；这些是归档快照中的状态。不要仅因社区名称就把它视为干净的科学讨论语料。
- **月度切片存在边界。** 月内评论可能回复月外的帖子或评论。`comments_with_parent_outside_package` 和 `comments_with_submission_outside_package` 统计引用对象不在包内的记录数，不能据此判定其在 Reddit 上不存在。
- **用户历史有范围限制。** 仅覆盖所选四个社区的这个月；不能把某个作者的缺席解释为不活跃或不感兴趣。
- **快照字段不等于创建时状态。** 得分、评论数、编辑及移除状态等可能在创建后抓取。按时间构建预测任务时，需要防止把这些后验信息当作当时已知输入。
- **互动不等于曝光或因果。** 数据没有完整的阅读曝光、沉默用户或内部信念记录，回复边不能直接解释为因果影响。
- **从局部讨论开始。** `changemyview` 可用于探索多层辩论，`CasualConversation` 可用于探索日常交流；先明确历史窗口和未来目标，再划分训练、验证和测试集。

底层内容来自 Reddit 与 Arctic Shift 归档；本仓库未为第三方原始内容另行授予新的许可。
