# 安装、更新与接入其他 Agent

## 先确定安装目标

配置属于实际运行 Agent 的用户和环境。如果 Codex 或 Claude Code 在服务器上运行，安装到服务器；如果在本机运行、仅通过 SSH 执行远程命令，就安装到本机。Windows、WSL、服务器和云端任务不自动共享配置，Git 登录账号也不会自动同步这些文件。

阅读本仓库不等于执行安装。用户要求安装时，先读 `README.md`、`AGENTS.md`，确认 Agent 和全局／项目范围，再运行脚本。没有明确目标的多 Agent 环境不要一次安装到所有宿主。

## 加载位置

| Agent | 默认 Skill 目录 | 常驻规则位置 | 本仓库支持 |
| --- | --- | --- | --- |
| Codex | `~/.agents/skills/` | `$CODEX_HOME/AGENTS.md`，未设置时为 `~/.codex/AGENTS.md`；非空 `AGENTS.override.md` 优先 | 全局或指定项目 |
| Claude Code | `~/.claude/skills/` | `~/.claude/CLAUDE.md` | 全局或指定项目 |
| TRAE | 项目中的 `.trae/skills/` | 项目中的 `.trae/rules/chris-skills.md`，`alwaysApply: true` | 脚本支持指定项目；全局按下文界面导入 |
| 其他 Agent | 由该 Agent 官方加载机制决定 | 由该 Agent 官方加载机制决定 | 确认入口后使用 `generic` 显式指定 |

路径中的 `~` 是实际用户的主目录。Codex 某些版本或环境仍使用 `$CODEX_HOME/skills`；如果实际已从该目录加载技能，使用 `--skills-dir` 指定它，避免同名 Skill 同时装到两处。`--codex-home` 只改变 Codex 全局指令目录，不自动改变 Skill 目录。

## 首次安装

以下示例在本仓库根目录运行。Linux 通常使用 `python3`，Windows 可用 `python` 或 `py -3`。

```bash
git clone https://github.com/codermcga/chris-skills.git
cd chris-skills
python3 scripts/install.py --agent codex --check
python3 scripts/install.py --agent codex
python3 scripts/install.py --agent codex --check
```

首次检查返回 `1` 是“尚未安装”，不是安装失败。检查返回 `2` 时先处理冲突，再安装。不要把三条命令用要求上一步成功的 `&&` 连接。

Claude Code 将 `--agent codex` 改成 `--agent claude`。Codex 与 Claude Code 均可添加 `--project /path/to/project` 仅接入指定业务项目；这不会产生跨项目全局效果。

Windows PowerShell 示例：

```powershell
python scripts/install.py --agent codex
python scripts/install.py --agent codex --check

# 实际使用旧版 Skill 目录时，安装和后续更新均保留这个参数
python scripts/install.py --agent codex --skills-dir "$env:USERPROFILE\.codex\skills"
```

默认安装所有根目录下包含 `SKILL.md` 的能力。只安装新能力时可用：

```bash
python3 scripts/install.py --agent codex --skill recap-and-learn
```

仅选择 `evolution` 时不会启用收尾规则。Codex 使用其原有 `agents/openai.yaml` 手动触发策略；Claude 安装器在目标副本中补充 `disable-model-invocation: true`，源文件保持不变。其他宿主须遵循 Skill 正文中的手动调用限制；不保证所有宿主支持同一种元数据。

## TRAE

### 指定项目安装（脚本支持）

```bash
python3 scripts/install.py --agent trae --project /path/to/business-project --check
python3 scripts/install.py --agent trae --project /path/to/business-project
python3 scripts/install.py --agent trae --project /path/to/business-project --check
```

Windows 的 `--project` 可以使用带引号的盘符路径。安装完成后，在 TRAE 中打开该业务项目，在技能列表与规则列表中确认能力存在、收尾规则为始终生效，再开新对话验证。项目配置是否提交到业务项目由用户决定，不由安装器自动提交。

### 全局接入（使用当前版本的设置界面）

1. 在“设置 → 技能与命令”创建全局技能，导入本仓库相应 `SKILL.md`；若 Skill 包含脚本／引用，保留完整目录资源。
2. 在“设置 → 规则与记忆”创建全局规则，把 `recap-and-learn/SKILL.md` 中 YAML 头之后的 Markdown 正文作为规则内容。
3. 在不同项目的新对话中验证规则已加载。

国内版官方文档当前将全局 Skill 目录列为 `~/.trae-cn/skills`，全局规则存储目录为 `~/.trae-cn/user_rules`。国际版／历史版本可能不同，规则存储格式也可能变化，所以脚本不猜测全局文件名与格式；使用界面或确认实际版本后采用 generic 接入。只有项目方式经过本仓库安装器的文件测试；TRAE 客户端的实际加载需在目标机器验证。

## 规则如何维护，已有配置如何保留

`recap-and-learn/SKILL.md` 正文是收尾行为的唯一源码。安装器将它复制到宿主常驻指令的下列标记之间，不要求每轮再读取仓库、不依赖固定机器路径：

```markdown
<!-- chris-skills:recap-and-learn:begin -->
（由脚本生成的规则正文）
<!-- chris-skills:recap-and-learn:end -->
```

重复安装只替换这个块，保留块外内容。Codex 已有非空全局 `AGENTS.override.md` 时，安装到该有效文件并打印真实位置；以后删除或新增覆盖文件后需重跑安装。标记缺失一半或重复时脚本停止，不猜测应删除哪些内容。

已安装 Skill 目录有 `.chris-skills-source` 所有权标记。遇到已有同名但非本脚本管理的目录时停止，不覆盖；先由 Agent 比对来源与本地改动，再由用户选择保留、迁移或改用其他明确的加载目录，不要直接抹掉冲突目录。不要在多个加载目录留同名副本。

改写现有文件前，安装器会在旁边留下 `.chris-skills.bak.<时间>` 备份；无变化时不写文件、不新增备份。已安装副本的修改会在更新时被仓库版本替换并备份，长期改动应回到源码仓库维护。安装器不会删除旧文件；未来 Skill 移除资源文件时需按实际引用另行清理。

## 后续更新

```bash
git pull --ff-only
python3 scripts/install.py --agent claude
python3 scripts/install.py --agent claude --check
```

替换为首次安装时相同的 Agent、`--project`、`--skills-dir` 等参数。常驻规则是安装时生成的副本，不会随着仓库拉取自动更新，也不随账号自动同步。更新后重新开启会话。

## 接入未知 Agent

先查看该 Agent 官方文档，确认支持的 Skill 结构、真实加载目录、常驻规则的格式和生效范围。确认它读取普通 Markdown 后，可执行：

```bash
python3 scripts/install.py --agent generic --skills-dir /actual/skills --rules-file /actual/instructions.md --check
python3 scripts/install.py --agent generic --skills-dir /actual/skills --rules-file /actual/instructions.md
```

这些路径是占位示例，必须替换。generic 只复制通用 Skill 并合并 Markdown 标记块，不生成未知宿主要求的 JSON、MDC 或其他包装，不保证该宿主会发现或加载文件。需要其他格式时新增小型适配或使用其设置界面；不复制整套个人配置、不修改系统提示词来冒充接入成功。

## 验证与回退

文件检查：原安装命令加 `--check` 返回 `0`。这是静态同步检查，不是宿主行为验证。

新会话验证：先让 Agent 说明加载了哪些相关规则，然后执行一个普通任务，确认末尾只有一次小结和1～2个知识点；再要求“只输出一个 JSON 对象”，确认没有附加收尾。Codex 可询问当前指令来源；Claude Code 可用 `/memory` 查看；TRAE 可在设置中查看生效范围。未在客户端运行时，应明确写“文件已安装，实际加载待验证”。

停用收尾时仅删除相应的完整标记块；保留块外内容。若需恢复被改写文件，可对照时间备份还原。移除 Skill 时先确认目录的所有权标记和实际加载位置，再移除对应能力目录，不递归删除整个用户配置目录。

## 官方依据（2026-10-31 核对）

- [Codex 全局与项目指令](https://learn.chatgpt.com/docs/agent-configuration/agents-md)
- [Codex Skill 加载与调用](https://learn.chatgpt.com/docs/build-skills)
- [Claude Code 指令与记忆](https://code.claude.com/docs/en/memory)
- [Claude Code Skill 与手动调用](https://code.claude.com/docs/en/skills)
- [TRAE 国内版 Skill 目录与导入](https://docs.trae.cn/ide_skills)
- [TRAE 国内版规则与作用范围](https://docs.trae.cn/ide_rules)
- [TRAE 国际版 Skill 导入说明](https://www.trae.ai/blog/trae_tutorial_0115)
