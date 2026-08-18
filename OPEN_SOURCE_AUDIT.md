# 开源发布审计

## 已完成

- 以用户指定的 V4 构建源码为唯一代码基准重新整理。
- 源码、文件名、可执行文件名、应用标识、数据目录和环境变量前缀已中性化。
- 未发现已填写的 API Key、私钥、访问令牌、真实用户凭据或硬编码本机绝对路径。
- 构建产物、设置、索引、会话和日志均被 `.gitignore` 排除。
- 启动诊断不再记录 PATH、工作目录和可执行文件绝对路径。

## 仓库所有者发布前确认

- [ ] 对源码和 `app_icon.png/.ico` 拥有公开发布及再许可权。
- [x] README 与 `pyproject.toml` 已使用 GitHub 用户名 `Mege98`。
- [x] 首次推送前检查 `git diff --cached`，并运行 `scripts/prepublish_check.ps1`。
- [x] 在 GitHub 启用 Secret scanning、Dependabot 和 Private vulnerability reporting。
- [x] 设置 Topics：`enterprise-search`、`document-retrieval`、`enterprise-knowledge-base`、`knowledge-management`、`industrial-ai`、`manufacturing-ai`、`rag`、`local-first`。
