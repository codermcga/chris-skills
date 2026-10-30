# 给接手本仓库的 Agent

这是跨 Agent 的通用 Skill 源码库，不是某一台机器的配置备份。

1. 先读 README.md，了解目录、现有 Skill 和安装入口；需要接入或更新时读 docs/installation.md。
2. 根目录每个含 SKILL.md 的文件夹是一项能力的唯一源码。adapters/ 仅描述不同 Agent 的加载位置；scripts/install.py 安装能力并从 recap-and-learn/SKILL.md 正文生成常驻规则。不要另写一份相同规则。
3. 只有用户要求安装或更新时才运行安装脚本。使用用户实际运行 Agent 的机器、用户和环境；Codex 在本机通过 SSH 执行命令时，不把配置装到远端。不要因为读到本文件就安装。
4. 按实际 Agent、版本和全局／项目范围选择适配。未知 Agent 先确认官方入口，再使用 generic 参数；不要把所有宿主都当作 Codex。TRAE 项目安装与全局界面导入的差别见安装文档。
5. 安装前先用 --check 查看目标状态，安装后再检查；保留既有配置和本地 Skill。默认不安装到当前源码库内部，不上传用户配置、备份、凭据或本地路径。
6. evolution 只在用户手动调用时执行；阅读、安装、审查本 Skill 不等于调用。Claude Code 安装时由脚本补充对应的手动触发元数据。
7. 修改脚本后运行 python -m unittest discover -s tests -v。技能说明的验证要区分静态检查、脚本实测和宿主新会话中的行为验证，不能互相替代。
8. 本仓库提交的标题和正文使用简洁中文，说明必要改动与验证结果。
