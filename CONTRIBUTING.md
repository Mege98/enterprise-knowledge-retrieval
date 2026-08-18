# 贡献指南

请从 `main` 创建功能分支，使用 Python 3.11 或 3.12 开发，并保持“无需登录、无需服务器即可进入检索界面”的默认体验。

提交前运行：

```powershell
python -m unittest -v test_release_readiness.py
powershell -ExecutionPolicy Bypass -File scripts/prepublish_check.ps1
```

不要提交 API Key、真实业务文档、索引数据库、设置、会话、日志或构建产物。界面改动请附前后截图；网络和存储改动需说明隐私影响。
