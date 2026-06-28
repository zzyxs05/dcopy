import os
import json
import argparse
import pyperclip
import sys
import subprocess

# ===================== 核心配置 =====================
DEFAULT_BLACKLIST = {
    "dll", "exe", "png", "jpg", "jpeg", "gif", "bmp", "ico",
    "zip", "rar", "7z", "tar", "gz", "bin", "so", "pyc", "pyo",
    "pdf", "doc", "docx", "xls", "xlsx", "mp3", "mp4", "avi",
    "svg", "webp", "db", "sqlite", "cache", "tmp"
}

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(SCRIPT_DIR, "dcopy_config.json")
# ====================================================

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        black = set(data.get("blacklist", []))
        white = set(data.get("whitelist", []))
    else:
        black = set(DEFAULT_BLACKLIST)
        white = set()
        save_config(black, white)
    return black, white

def save_config(blacklist, whitelist):
    data = {
        "blacklist": sorted(list(blacklist)),
        "whitelist": sorted(list(whitelist))
    }
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def get_ext(filename):
    return os.path.splitext(filename)[1][1:].lower()

def has_ext(path):
    """判断路径是否包含文件后缀"""
    _, ext = os.path.splitext(path)
    return bool(ext)

def can_read(filepath, blacklist, whitelist):
    ext = get_ext(filepath)
    if whitelist and ext in whitelist:
        return True
    if ext in blacklist:
        return False
    return True

def should_skip_content(filepath, exclude_content):
    """检查文件是否在排除内容列表中"""
    if not exclude_content:
        return False
    filepath = os.path.normpath(filepath)
    for exc in exclude_content:
        exc_norm = os.path.normpath(exc)
        # 精确匹配文件
        if filepath == exc_norm:
            return True
        # 检查文件是否在排除的目录下
        if os.path.isdir(exc) and filepath.startswith(exc_norm + os.sep):
            return True
    return False

def should_exclude(filepath, exclude_all):
    """检查文件/目录是否在完全排除列表中"""
    if not exclude_all:
        return False
    filepath = os.path.normpath(filepath)
    for exc in exclude_all:
        exc_norm = os.path.normpath(exc)
        if filepath == exc_norm or filepath.startswith(exc_norm + os.sep):
            return True
    return False

def generate_content(root, blacklist, whitelist, names_only=False, exclude_content=None, exclude_all=None):
    lines = []
    root = os.path.abspath(root)
    root_name = os.path.basename(root)
    lines.append(f"{root_name} 📂")

    # 将相对路径转换为绝对路径用于比较
    def to_abs(path):
        if os.path.isabs(path):
            return os.path.normpath(path)
        return os.path.normpath(os.path.join(root, path))
    
    exclude_content_abs = set()
    if exclude_content:
        for p in exclude_content:
            abs_p = to_abs(p)
            if not has_ext(p) and os.path.isdir(abs_p):
                # 目录：添加目录本身
                exclude_content_abs.add(abs_p)
            else:
                exclude_content_abs.add(abs_p)
    
    exclude_all_abs = set()
    if exclude_all:
        for p in exclude_all:
            exclude_all_abs.add(to_abs(p))

    # 先收集目录结构和需要读取内容的文件
    structure_lines = []
    content_files = []

    for dirpath, dirnames, filenames in os.walk(root):
        # 计算当前目录相对于根目录的层级
        rel_dir = os.path.relpath(dirpath, root)
        if rel_dir == ".":
            level = 0
        else:
            level = rel_dir.count(os.sep) + 1
        indent = "   " * level + "   丨-"

        # 过滤完全排除的目录
        dirnames_to_show = []
        for d in dirnames:
            full_dir = os.path.normpath(os.path.join(dirpath, d))
            if not should_exclude(full_dir, exclude_all_abs):
                dirnames_to_show.append(d)
                structure_lines.append(f"{indent}{d} 📂")
        # 更新 dirnames 以跳过完全排除的目录
        dirnames[:] = [d for d in dirnames if d in dirnames_to_show]

        for f in filenames:
            full = os.path.normpath(os.path.join(dirpath, f))
            rel = os.path.relpath(full, root)
            
            # 完全排除
            if should_exclude(full, exclude_all_abs):
                continue
            
            structure_lines.append(f"{indent}{f}")

            # 内容排除
            skip_content = should_skip_content(full, exclude_content_abs)
            if not names_only and not skip_content and can_read(full, blacklist, whitelist):
                content_files.append((full, rel))

    # 先输出目录结构
    lines.extend(structure_lines)

    # 如果不是仅显示名称，再输出文件内容
    if not names_only and content_files:
        lines.append("\n" + "=" * 50)
        lines.append("📄 文件内容")
        lines.append("=" * 50)
        
        for full, rel in content_files:
            # 使用斜杠格式的路径
            rel_path = "/" + rel.replace(os.sep, "/")
            try:
                with open(full, "r", encoding="utf-8") as fobj:
                    content = fobj.read()
                lines.append(f"\n{rel_path}:")
                lines.append(content)
            except Exception:
                lines.append(f"\n{rel_path}:")
                lines.append("[无法读取文件内容]")

    return "\n".join(lines)

def update_project():
    """更新项目到最新版本"""
    try:
        print("\n🔄 正在检查更新...")
        # 获取当前脚本所在目录
        project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # 检查是否是 git 仓库
        if not os.path.exists(os.path.join(project_dir, ".git")):
            print("❌ 错误：当前安装不是通过 git clone 安装的，无法自动更新")
            print("💡 建议：请重新通过 git clone 安装以支持自动更新功能")
            return
        
        # 执行 git pull
        print("📥 正在从远程仓库拉取最新代码...")
        result = subprocess.run(
            ["git", "pull"],
            cwd=project_dir,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            if "Already up to date" in result.stdout or "已经是最新的" in result.stdout:
                print("✅ 当前已是最新版本！")
            else:
                print("✅ 更新成功！")
                print(result.stdout)
                print("\n💡 提示：如果更新了依赖，请运行 'pip install -e .' 重新安装")
        else:
            print(f"❌ 更新失败：{result.stderr}")
            
    except subprocess.TimeoutExpired:
        print("❌ 更新超时，请检查网络连接")
    except Exception as e:
        print(f"❌ 更新出错：{str(e)}")

def run():
    if len(sys.argv) > 1 and sys.argv[1] in ("help", "-help", "--help"):
        print("=== dcopy 使用说明 ===")
        print("dcopy              复制当前目录结构+文本到剪贴板")
        print("dcopy -n           仅复制目录结构和文件名称(不读取文件内容)")
        print("dcopy -b 后缀      将后缀加入黑名单(后缀请勿带.)")
        print("dcopy -w 后缀      将后缀加入白名单")
        print("dcopy -v           查看当前黑白名单")
        print("dcopy -u           更新到最新版本")
        print("dcopy -r 路径       排除指定文件/目录的内容复制(仍显示结构)")
        print("dcopy -R 路径       完全排除指定文件/目录(不显示结构和内容)")
        print("dcopy help         查看帮助")
        return
    parser = argparse.ArgumentParser(description="dcopy - 目录结构复制到剪贴板")
    parser.add_argument("-b", nargs="+", help="添加到黑名单")
    parser.add_argument("-w", nargs="+", help="添加到白名单")
    parser.add_argument("-v", "--view", action="store_true", help="查看当前黑白名单")
    parser.add_argument("-n", action="store_true", help="仅复制目录结构和文件名称(不读取文件内容)")
    parser.add_argument("-u", "--update", action="store_true", help="更新到最新版本")
    parser.add_argument("-r", nargs="+", help="排除指定文件/目录的内容复制(仍显示结构)")
    parser.add_argument("-R", nargs="+", help="完全排除指定文件/目录(不显示结构和内容)")
    args = parser.parse_args()

    black, white = load_config()

    # 处理更新命令
    if args.update:
        update_project()
        return

    if args.b or args.w or args.view:
        if args.view:
            print("\n📋 dcopy 当前规则")
            print(f"✅ 黑名单：{sorted(black)}")
            print(f"✅ 白名单：{sorted(white) if white else '无'}")
            print(f"📂 配置文件：{CONFIG_FILE}\n")
            return

        # 添加到黑名单 → 自动从白名单移除
        if args.b:
            for ext in args.b:
                ext = ext.lower()
                if ext in white:
                    white.remove(ext)
                    print(f"ℹ️ 已从白名单移除 {ext}")
                if ext not in black:
                    black.add(ext)
                    print(f"✅ 已将 {ext} 加入黑名单")
                else:
                    print(f"ℹ️ {ext} 已在黑名单中")

        # 添加到白名单 → 自动从黑名单移除
        if args.w:
            for ext in args.w:
                ext = ext.lower()
                if ext in black:
                    black.remove(ext)
                    print(f"ℹ️ 已从黑名单移除 {ext}")
                if ext not in white:
                    white.add(ext)
                    print(f"✅ 已将 {ext} 加入白名单")
                else:
                    print(f"ℹ️ {ext} 已在白名单中")

        save_config(black, white)
        return

    content = generate_content(
        os.getcwd(), black, white,
        names_only=args.n,
        exclude_content=args.r,
        exclude_all=args.R
    )
    pyperclip.copy(content)
    if args.n:
        print("\n📋 已复制目录结构及文件名称到剪贴板！\n")
    else:
        print("\n📋 已复制到剪贴板！\n")

if __name__ == "__main__":
    run()