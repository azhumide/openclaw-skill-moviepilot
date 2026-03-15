---
name: moviepilot
description: MoviePilot-2 API 全功能管理插件，支持影视库统计、站点、订阅、下载、媒体元数据及系统维护的深度控制。
homepage: http://10.10.10.80:3000
metadata: { "openclaw": { "emoji": "🎞️", "requires": { "bins": [], "python_packages": ["requests"] } } }
---

# MoviePilot-2 综合管理技能

本技能是一个全功能的 API 客户端，让 OpenClaw 能够深度接管 MoviePilot-2 自动化媒体管理系统。

- **当前配置地址**: `http://10.10.10.80:3000`
- **配置文件**: 插件目录下的 `config.json`（URL + Token）
- **调用方式**: `python3 /home/rs/.openclaw/skills/moviepilot/moviepilot_client.py <模块> <子命令>`

---

## ⚡ 快速上手

```bash
# 查看影视库统计（电影数、剧集数、存储用量）
python3 /home/rs/.openclaw/skills/moviepilot/moviepilot_client.py status

# 搜索电影
python3 /home/rs/.openclaw/skills/moviepilot/moviepilot_client.py media search "奥本海默"

# 查看当前订阅
python3 /home/rs/.openclaw/skills/moviepilot/moviepilot_client.py sub list

# 查看下载队列
python3 /home/rs/.openclaw/skills/moviepilot/moviepilot_client.py dl list
```

---

## 🛠️ 命令参考

### 1. `status` — 仪表盘总览

```bash
python3 moviepilot_client.py status
```

返回：电影数、剧集数、集数、总存储、已用存储。

---

### 2. `site` — 站点中心

| 子命令 | 说明 | 示例 |
|--------|------|------|
| `list` | 列出所有站点 | `site list` |
| `test --id <ID>` | 测试站点连通性 | `site test --id 1` |
| `sync` | 触发 CookieCloud 同步 | `site sync` |
| `rss` | 查看 RSS 站点列表 | `site rss` |
| `resource --id <ID> --key <词>` | 浏览站点资源 | `site resource --id 1 --key 哈利波特` |
| `user --id <ID>` | 查看站点个人数据（上传/下载/等级） | `site user --id 1` |

---

### 3. `sub` — 订阅管理

| 子命令 | 说明 | 示例 |
|--------|------|------|
| `list` | 查看当前所有订阅 | `sub list` |
| `history --type movie/tv` | 订阅历史 | `sub history --type movie` |
| `popular --type movie/tv` | 热门推荐 | `sub popular --type tv` |
| `refresh` | 强制刷新所有订阅 | `sub refresh` |
| `search` | 搜索所有订阅资源 | `sub search` |
| `del --id <ID>` | 删除指定订阅 | `sub del --id 5` |

---

### 4. `media` — 媒体元数据

| 子命令 | 说明 | 示例 |
|--------|------|------|
| `search <关键词>` | 模糊搜索资源 | `media search 奥本海默` |
| `rec <标题>` | 精准媒体识别（获取 TMDBID） | `media rec "Oppenheimer 2023"` |
| `library --type movie/tv --page N --count N` | 查看媒体库列表 | `media library --type movie --page 1 --count 20` |
| `detail <ID> --type movie/tv` | 获取媒体详情 | `media detail 872585 --type movie` |
| `douban <豆瓣ID>` | 获取豆瓣评分/简介 | `media douban 35512316` |
| `tmdb <TMDBID>` | 获取剧集所有季信息 | `media tmdb 1396` |

---

### 5. `dl` — 下载器控制

| 子命令 | 说明 | 示例 |
|--------|------|------|
| `list` | 查看当前下载队列 | `dl list` |
| `info` | 实时上传/下载速率 | `dl info` |
| `add --url <链接>` | 添加下载任务 | `dl add --url "magnet:?xt=..."` |
| `start --hash <Hash>` | 启动任务 | `dl start --hash abc123` |
| `stop --hash <Hash>` | 暂停任务 | `dl stop --hash abc123` |
| `del --hash <Hash>` | 删除任务 | `dl del --hash abc123` |

---

### 6. `sys` — 系统维护

| 子命令 | 说明 | 示例 |
|--------|------|------|
| `info` | 查看定时任务及下次执行时间 | `sys info` |
| `env` | 查看系统配置 | `sys env` |
| `run --job <任务名>` | 手动触发定时任务 | `sys run --job rss_download` |
| `user` | 查看所有注册用户 | `sys user` |
| `msg --text <内容>` | 向消息中心发送通知 | `sys msg --text "测试消息"` |
| `restart` | 远程重启 MoviePilot | `sys restart` |

---

## ⚙️ 配置文件 (`config.json`)

```json
{
  "MOVIEPILOT_URL": "http://10.10.10.80:3000",
  "MOVIEPILOT_API_TOKEN": "your_token_here"
}
```

Token 失效时：登录 MoviePilot → 设置 → 用户 → 重新生成 API Token，更新到 `config.json` 即可。

---

## 🧠 Agent 调用建议

- **查影视库统计** → `status`
- **找片子** → `media search <关键词>`
- **查当前有什么在下** → `dl list`
- **追剧管理** → `media rec` 精准识别后用 `sub` 添加订阅
- **诊断下载卡住** → 依次 `dl info` → `site test --id <ID>` → `sys info`
- **获取豆瓣评价** → `media douban <豆瓣ID>`

## 📝 全功能使用示例

本插件通过 `python3 /home/rs/.openclaw/skills/moviepilot/moviepilot_client.py <模块> <子命令> [参数]` 进行调用。

### 1. 📊 系统与状态 (Status & Sys)
```bash
# 获取影视库整体统计（电影数、剧集数等）及存储空间占用
python3 /home/rs/.openclaw/skills/moviepilot/moviepilot_client.py status

# 查询系统环境变量
python3 /home/rs/.openclaw/skills/moviepilot/moviepilot_client.py sys env

# 查看当前运行的后台任务
python3 /home/rs/.openclaw/skills/moviepilot/moviepilot_client.py sys jobs

# 发送系统消息测试
python3 /home/rs/.openclaw/skills/moviepilot/moviepilot_client.py sys msg --text "老猪发来贺电"
```

### 2. 🎬 订阅管理 (Sub)
```bash
# 查看当前所有订阅列表
python3 /home/rs/.openclaw/skills/moviepilot/moviepilot_client.py sub list

# 订阅电影 (如 寻秦记 TMDB ID: 650524)
python3 /home/rs/.openclaw/skills/moviepilot/moviepilot_client.py sub add --id 650524 --type movie

# 订阅剧集 (如 权利的游戏 TMDB ID: 1399)
python3 /home/rs/.openclaw/skills/moviepilot/moviepilot_client.py sub add --id 1399 --type tv

# 订阅指定剧集的特定季 (如 第二季)
python3 /home/rs/.openclaw/skills/moviepilot/moviepilot_client.py sub add --id 1399 --type tv --season 2

# 删除订阅 (需提供订阅记录ID，可通过 sub list 查询)
python3 /home/rs/.openclaw/skills/moviepilot/moviepilot_client.py sub del --id <订阅ID>
```

### 3. 🔍 媒体库与检索 (Media)
```bash
# 搜索影视剧信息
python3 /home/rs/.openclaw/skills/moviepilot/moviepilot_client.py media search "阿凡达"

# 获取豆瓣影视详情信息
python3 /home/rs/.openclaw/skills/moviepilot/moviepilot_client.py media douban --id <豆瓣ID>

# 获取 TMDB 剧集季详情
python3 /home/rs/.openclaw/skills/moviepilot/moviepilot_client.py media tmdb --id <TMDB_ID> --type tv
```

### 4. 🌐 站点管理 (Site)
```bash
# 列出所有配置的 PT/BT 站点
python3 /home/rs/.openclaw/skills/moviepilot/moviepilot_client.py site list

# 搜索特定站点的资源
python3 /home/rs/.openclaw/skills/moviepilot/moviepilot_client.py site resource --key "黑客帝国"
```

### 5. ⬇️ 下载管理 (DL)
```bash
# 查看当前活动下载任务
python3 /home/rs/.openclaw/skills/moviepilot/moviepilot_client.py dl list

# 添加下载任务 (磁力链接/种子URL)
python3 /home/rs/.openclaw/skills/moviepilot/moviepilot_client.py dl add --url "magnet:?xt=urn:btih:..."

# 暂停/继续/删除下载任务
python3 /home/rs/.openclaw/skills/moviepilot/moviepilot_client.py dl stop --hash <任务Hash>
python3 /home/rs/.openclaw/skills/moviepilot/moviepilot_client.py dl start --hash <任务Hash>
python3 /home/rs/.openclaw/skills/moviepilot/moviepilot_client.py dl del --hash <任务Hash>
```

### 6. 🕒 历史记录 (History)
```bash
# 查看下载历史记录 (支持分页)
python3 /home/rs/.openclaw/skills/moviepilot/moviepilot_client.py history download --page 1

# 查看媒体整理转移历史
python3 /home/rs/.openclaw/skills/moviepilot/moviepilot_client.py history transfer --page 1
```
