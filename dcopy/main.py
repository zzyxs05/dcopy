import os
import json
import argparse
import pyperclip
import sys

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

def can_read(filepath, blacklist, whitelist):
    ext = get_ext(filepath)
    if whitelist and ext in whitelist:
        return True
    if ext in blacklist:
        return False
    return True

def generate_content(root, blacklist, whitelist):
    lines = []
    root_name = os.path.basename(os.path.abspath(root))
    lines.append(f"{root_name} 📂")

    for dirpath, dirnames, filenames in os.walk(root):
        level = dirpath.replace(root, "").count(os.sep)
        indent = "   " * level + "   丨-"

        for d in dirnames:
            lines.append(f"{indent}{d} 📂")

        for f in filenames:
            full = os.path.join(dirpath, f)
            rel = os.path.relpath(full, root)
            lines.append(f"{indent}{f}")

            if can_read(full, blacklist, whitelist):
                try:
                    with open(full, "r", encoding="utf-8") as fobj:
                        content = fobj.read()
                    lines.append(f"\n{rel}:")
                    lines.append(content)
                    lines.append("")
                except Exception:
                    lines.append(f"\n{rel}:")
                    lines.append("[无法读取文件内容]")
                    lines.append("")
    return "\n".join(lines)

def run():
    if len(sys.argv) > 1 and sys.argv[1] in ("help", "-help", "--help"):
        print("=== dcopy 使用说明 ===")
        print("dcopy              复制当前目录结构+文本到剪贴板")
        print("dcopy -b 后缀      将后缀加入黑名单(后缀请勿带.)")
        print("dcopy -w 后缀      将后缀加入白名单")
        print("dcopy -v           查看当前黑白名单")
        print("dcopy help         查看帮助")
        return
    parser = argparse.ArgumentParser(description="dcopy - 目录结构复制到剪贴板")
    parser.add_argument("-b", nargs="+", help="添加到黑名单")
    parser.add_argument("-w", nargs="+", help="添加到白名单")
    parser.add_argument("-v", "--view", action="store_true", help="查看当前黑白名单")
    args = parser.parse_args()

    black, white = load_config()

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

    content = generate_content(os.getcwd(), black, white)
    pyperclip.copy(content)
    print("\n📋 已复制到剪贴板！\n")

if __name__ == "__main__":
    run()