# chris-skills

跨 Agent、跨机器复用的通用 Skill 库。这里维护能力的源码和必要的安装适配，不保存某台机器的完整配置。新 Agent 请先阅读本页，再按 [安装说明](docs/installation.md) 接入。

## 现有能力

| 目录 | 用途 | 使用方式 |
| --- | --- | --- |
| [evolution/](evolution/SKILL.md) | 复盘相关工作，依据证据提出 Skill 或项目改进方案 | 仅手动调用；默认先给方案供用户评估 |
| [recap-and-learn/](recap-and-learn/SKILL.md) | 每轮最终回复附简短小结与1～2个相关知识点 | 可按需调用；安装时同步到常驻规则后持续启用 |

## 目录职责

| 路径 | 放什么、由谁使用 |
| --- | --- |
| `AGENTS.md` | 接手本仓库的 Agent 应遵守的阅读顺序、安装与维护约定；不代表自动授权安装 |
| `CLAUDE.md` | Claude Code 的薄入口，导入同一份 `AGENTS.md` |
| `.trae/rules/repository.md` | TRAE 在本仓库的薄入口，引导读取同一份说明 |
| `<skill-name>/SKILL.md` | 能力的唯一源码，采用通用 name、description 与 Markdown 正文 |
| `<skill-name>/agents/` | 宿主专用的可选元数据，例如 Codex 的显示信息和触发策略 |
| `adapters/*.json` | Codex、Claude Code、TRAE 各自的安装路径与规则包装；不存放业务规则副本 |
| `scripts/install.py` | Python 标准库安装器：复制 Skill、合并常驻规则、检查状态和备份修改前文件 |
| `docs/installation.md` | 首次安装、更新、其他 Agent 接入、回退与验证方法 |
| `tests/` | 安装器的隔离测试，不读写实际用户配置 |

## 让下一台机器的 Agent 帮你安装

可以直接把下面这段话发给新的 Agent：

> 请从 https://github.com/codermcga/chris-skills 下载这个通用 Skill 仓库，先阅读 README.md、AGENTS.md 和 docs/installation.md。根据你实际运行的 Agent、系统和环境，安装仓库中的 Skill，并启用每轮回复末尾的本轮小结和知识点。先检查目标状态，保留已有配置，安装后再检查，并告诉我实际安装位置及是否需要新开会话。如果你是 TRAE，先确认我需要指定项目接入还是全局界面导入；不要把另一个 Agent 的路径直接套用过来。

SSH 地址是 `git@github.com:codermcga/chris-skills.git`；新机器没有配置 GitHub SSH 时，可以使用上面的 HTTPS 地址克隆，无需为读取公开仓库配置密钥。

## 快速开始

需要 Git 和 Python 3.9+，无第三方 Python 依赖。`python` 可以替换成机器上的 `python3` 或 `py -3`。

```bash
git clone https://github.com/codermcga/chris-skills.git
cd chris-skills
```

从下列命令中选择实际使用的 Agent：

```bash
# Codex：当前用户全局安装
python scripts/install.py --agent codex

# Claude Code：当前用户全局安装
python scripts/install.py --agent claude

# TRAE：安装到明确指定的业务项目，路径替换为实际路径
python scripts/install.py --agent trae --project /path/to/project
```

不要把三条命令全部运行。TRAE 全局接入、Windows 路径和 Codex 旧版目录兼容方式见 [安装说明](docs/installation.md)。脚本拒绝将生成配置写回本源码库。

## 更新与验证

```bash
git pull --ff-only
python scripts/install.py --agent codex
python scripts/install.py --agent codex --check
```

替换为原来安装时的相同 Agent、范围与路径参数。脚本复制文件，因此仅 `git pull` 不会更新已安装内容。`--check` 只读取：返回码 `0` 表示文件已同步，`1` 表示需要安装或更新，`2` 表示目标冲突或参数等错误。

安装后新开 Agent 会话，确认它识别 Skill 和常驻规则，并用普通任务验证“小结 + 知识点”、用“只输出 JSON”验证格式例外。脚本检查通过只证明文件已同步，不证明宿主实际加载或每轮行为已验证。

维护脚本时运行：

```bash
python -m unittest discover -s tests -v
```
