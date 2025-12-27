# Streamlit Community Cloud 部署指南

## 部署前准备

### 1. 已创建的文件
- ✅ `streamlit_app.py` - Streamlit Cloud 入口文件
- ✅ `.gitignore` - Git 忽略文件配置
- ✅ `.streamlit/config.toml` - Streamlit 配置文件
- ✅ `requirements.txt` - Python 依赖（已更新）

### 2. 文件结构
```
eastmoney_tool/
├── streamlit_app.py          # ← Streamlit Cloud 入口文件
├── requirements.txt           # Python 依赖
├── setup.py                   # 包安装配置
├── .gitignore                 # Git 忽略规则
├── .streamlit/
│   └── config.toml           # Streamlit 配置
├── src/
│   └── eastmoney_tool/       # 主包代码
│       └── ui/
│           └── app.py        # 主应用文件
└── README.md
```

## 部署步骤

### 步骤 1: 推送到 GitHub

如果还没有 Git 仓库，执行：

```bash
# 初始化 Git 仓库
git init

# 添加所有文件
git add .

# 提交
git commit -m "Initial commit for Streamlit Cloud deployment"

# 在 GitHub 上创建新仓库，然后添加远程仓库
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git

# 推送到 GitHub
git branch -M main
git push -u origin main
```

### 步骤 2: 在 Streamlit Community Cloud 部署

1. 访问 https://share.streamlit.io/
2. 使用 GitHub 账号登录
3. 点击 **"New app"** 按钮
4. 填写部署信息：
   - **Repository**: 选择你的 GitHub 仓库
   - **Branch**: `main` (或你使用的主分支)
   - **Main file path**: `streamlit_app.py`
   - **Python version**: 选择 `3.9` 或 `3.10` (推荐)
5. 点击 **"Deploy"** 按钮

### 步骤 3: 等待部署完成

- Streamlit Cloud 会自动安装 `requirements.txt` 中的依赖
- 首次部署可能需要几分钟
- 部署成功后，会显示你的应用 URL

## 配置说明

### Main file path
- 使用: `streamlit_app.py`
- 这个文件会导入主应用代码并执行

### Python 版本
- 推荐: `3.9` 或 `3.10`
- 确保与本地开发环境兼容

### requirements.txt
确保包含所有依赖：
```
requests>=2.31.0
pandas>=2.1.0
pyarrow>=15.0.0
streamlit>=1.32.0
python-dateutil>=2.9.0.post0
setuptools>=65.0.0
```

## 验证部署

部署成功后，访问你的应用 URL，检查：

1. ✅ 应用正常加载
2. ✅ 所有 tab 可以正常切换
3. ✅ 数据拉取功能正常
4. ✅ 金额显示为"万元"单位
5. ✅ 没有错误提示

## 常见问题

### 问题 1: 导入错误 (ModuleNotFoundError)
- **原因**: 路径配置问题
- **解决**: `streamlit_app.py` 已经配置了路径，确保 `src/` 目录结构正确

### 问题 2: 依赖安装失败
- **原因**: `requirements.txt` 中版本不兼容
- **解决**: 检查 Python 版本兼容性，更新依赖版本

### 问题 3: 应用运行缓慢
- **原因**: 网络请求延迟或数据量大
- **解决**: 这是正常的，数据来自外部 API，受网络影响

## 更新应用

更新代码后，只需：

```bash
git add .
git commit -m "Update app"
git push
```

Streamlit Cloud 会自动检测更改并重新部署。

## 注意事项

1. **API 请求频率**: 工具会调用东方财富 API，注意合理控制请求频率
2. **数据隐私**: 所有数据都在客户端处理，不会存储在服务器
3. **免费额度**: Streamlit Community Cloud 有使用限制，注意查看服务条款

