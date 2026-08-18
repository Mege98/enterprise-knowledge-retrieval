# 企业知识检索系统

一个下载后即可使用的 Windows 企业文档检索与 RAG 问答项目。基于成熟的 V4 桌面版本整理开源，保留原有界面、索引、精确检索、来源追溯和对话体验，仅移除组织专用名称及本机敏感信息。

**项目标签：** `enterprise-search` · `document-retrieval` · `enterprise-knowledge-base` · `knowledge-management` · `industrial-ai` · `manufacturing-ai` · `rag` · `local-first`

## 直接使用

从 GitHub Releases 下载 `EnterpriseKnowledgeRetrieval-Windows-x64-v0.4.0.zip`，完整解压后双击：

```text
EnterpriseKnowledgeRetrieval.exe
```

无需注册、无需登录、无需部署服务器。选择资料文件夹并建立索引后，即可使用本地精确检索。需要 RAG 问答时，再在设置中填写 OpenAI 兼容接口、模型和 API Key。

## 主要能力

- 索引 PDF、DOCX、XLSX、Markdown、TXT、CSV、HTML、JSON、源码等常见文件
- 精确关键词、短语、全部关键词和大小写匹配
- 结合文件名与内容候选进行检索，并展示位置、上下文和来源
- 使用 OpenAI 兼容 Chat Completions 接口生成可追溯回答
- 本地保存索引、设置和历史会话
- 适用于制度规范、工艺文件、设备手册、质量标准、SOP 和工程资料

## 从源码运行

推荐 Python 3.11 或 3.12：

```powershell
git clone https://github.com/Mege98/enterprise-knowledge-retrieval.git
cd enterprise-knowledge-retrieval
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -U pip
python -m pip install -r requirements.txt
python enterprise_knowledge_retrieval.py
```

环境变量清单见 `.env.example`。程序不会自动读取 `.env` 文件，也不会在仓库中保存 API Key。

## Windows 打包

```powershell
powershell -ExecutionPolicy Bypass -File scripts/build_windows.ps1
```

输出位于 `dist/EnterpriseKnowledgeRetrieval/`。发布前运行：

```powershell
powershell -ExecutionPolicy Bypass -File scripts/prepublish_check.ps1
```

## 数据与隐私

索引、设置和会话保存在使用者本机。精确检索不调用模型；RAG 问答会向用户配置的模型接口发送当前问题和必要的检索片段。请勿处理无权上传到该模型服务的资料。

## 许可证

源码按 [Apache License 2.0](LICENSE) 发布。第三方依赖遵循各自许可证，详见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。

English: [README_EN.md](README_EN.md)
