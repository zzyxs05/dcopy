# 📂 dcopy

一键生成目录结构+文本内容，自动复制到剪贴板，方便粘贴分享

---
✨ 功能亮点

- 纯命令行操作，全局可用，无需打开编辑器
- 配置透明：仅在脚本目录保存配置，无隐形文件、无残留


---
🛠️ 安装方式

```
git clone https://github.com/zzyxs05/dcopy.git

cd dcopy

pip install -e .
```


---
📌 常用命令

```
dcopy     生成当前目录结构+文本，复制到剪贴板

dcopy -n  仅复制目录结构和文件名称(不读取文件内容)

dcopy help  查看帮助说明

dcopy -b 后缀   将文件后缀加入黑名单(后缀请勿带.)

dcopy -w 后缀   将文件后缀加入白名单

dcopy -v   查看当前黑白名单和配置路径

dcopy -u   更新到最新版本
```


---
🍓简易使用
<img width="1051" height="81" alt="a95415a9-5e42-4456-9819-12a348d0d700" src="https://github.com/user-attachments/assets/cb82a075-f253-4311-83d8-a4f24b5d8b39" />

直接在文件路径输入dcopy即可以当前文件夹为根路径进行复制

------



# 🗑️ 卸载方式

#### 1. 卸载全局命令

```bash
pip uninstall dcopy -y
```

#### 2. 删除项目文件夹（彻底清理）

**注意**：`pip uninstall` 只会卸载全局命令，不会删除 git clone 下载的项目文件夹。
如需完全清理，请手动删除项目文件夹：

```bash
# Windows (PowerShell)
Remove-Item -Recurse -Force <项目文件夹路径>

# Linux/Mac
rm -rf <项目文件夹路径>
```

- 配置文件存放在 `dcopy/dcopy_config.json`，删除项目即清空配置
- 默认已屏蔽图片、压缩包、可执行文件等非文本格式

---

# 🔄 更新方式

#### 自动更新（推荐）

```bash
dcopy -u
```

此命令会自动从 GitHub 拉取最新代码。如果更新了依赖，请运行：

```bash
pip install -e .
```

#### 手动更新

```bash
cd <项目文件夹路径>
git pull
pip install -e .
```
