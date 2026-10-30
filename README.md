# chris-skills

跨 Agent、跨机器复用的通用 Skill 和常驻提示词库。由新环境中的 Agent 阅读说明，按自身加载机制接入和更新，无需专用安装器。

## 内容怎么区分

| 内容类型 | 来源 | 如何使用 |
| --- | --- | --- |
| 常驻提示词 | `recap-and-learn/SKILL.md` 的 YAML 头之后的 Markdown 正文 | 合并到当前 Agent 的用户级常驻指令中，让每轮最终回复附小结与知识点 |
| 全局 Skill | `evolution/`、`recap-and-learn/` 完整目录 | 放入当前 Agent 支持的用户级 Skill 加载位置，供跨项目使用 |
| 仓库说明 | 本页、`AGENTS.md` 和 `docs/usage.md` | 供接手仓库的 Agent 理解结构、接入与维护方式，不作为全局工作规则复制 |

这里的“常驻提示词”对应你希望长期生效的个人规则，有时也被称为“系统提示词”；实际接入使用 Agent 提供的用户指令／规则机制，不修改产品内部的系统提示词。

同一份收尾规则复用 `recap-and-learn/SKILL.md` 正文，不维护第二份副本。只需要每轮收尾时，接入常驻提示词即可；也希望保留按需调用入口时，再把它作为全局 Skill 接入。

## 现有能力

| 目录 | 用途 | 使用方式 |
| --- | --- | --- |
| [evolution/](evolution/SKILL.md) | 复盘相关工作，依据证据提出 Skill 或项目改进方案 | 仅手动调用；默认先给方案供用户评估 |
| [recap-and-learn/](recap-and-learn/SKILL.md) | 每轮最终回复附简短小结与1～2个相关知识点 | 正文可作为常驻提示词，也可作为 Skill 按需调用 |

## 目录职责

| 路径 | 放什么、由谁使用 |
| --- | --- |
| `AGENTS.md` | 接手本仓库的 Agent 应遵守的阅读顺序、接入与维护约定 |
| `CLAUDE.md` | Claude Code 的薄入口，导入同一份 `AGENTS.md` |
| `.trae/rules/repository.md` | TRAE 在本仓库的薄入口，引导读取同一份说明 |
| `<skill-name>/SKILL.md` | 能力的唯一源码，采用通用 name、description 与 Markdown 正文 |
| `<skill-name>/agents/` | 宿主专用的可选元数据，例如 Codex 的显示信息和触发策略 |
| `docs/usage.md` | 新环境接入、同步仓库更新，以及把新经验维护回仓库的方法 |

## 让下一台机器的 Agent 帮你接入

可以直接把下面这段话发给新的 Agent：

> 请读取 https://github.com/codermcga/chris-skills 的 README.md 和 docs/usage.md，理解哪些是常驻提示词、哪些是全局 Skill，再按你所在 Agent 和环境的加载机制接入。启用每轮回复的小结与知识点，保留其他已有配置，并说明实际接入位置和验证情况。如果已经接入过，就对比仓库最新内容更新，不要重复追加。

SSH 地址是 `git@github.com:codermcga/chris-skills.git`；新机器没有配置 GitHub SSH 时，可以使用上面的 HTTPS 地址克隆，无需为读取公开仓库配置密钥。

## 后续更新

仓库是共享内容的来源，各机器的接入内容由 Agent 根据仓库同步。你可以直接说：

> 请读取 chris-skills 仓库最新说明，对比并更新当前环境中已接入的提示词和 Skill，保留无关配置及本地改动，避免重复规则。

如果是希望把新的通用经验维护回仓库，可以说：

> 请把这次确定的通用规则更新到 chris-skills 的对应源码中，检查是否与已有内容重复或冲突；按我授权的范围修改、提交或推送。

新增能力放入新的 `<skill-name>/` 目录，并更新本页的能力清单；新增常驻偏好注明其来源和使用范围。不要把一次性的项目路径、临时参数或整台机器的配置带入通用规则。具体接入与更新原则见 [使用说明](docs/usage.md)。
