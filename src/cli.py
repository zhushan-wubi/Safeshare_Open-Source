
import argparse
import json
import os
from app import secrets, save_data, logger

def cmd_create():
    parser = argparse.ArgumentParser()
    parser.add_argument("text", help="秘密内容")
    parser.add_argument("--passcode", "-p", default="", help="密码")
    parser.add_argument("--type", "-t", default="normal", help="类型 normal/time/double/tree")
    parser.add_argument("--expire", "-e", default="burn_after_read", help="过期模式 burn_after_read/24h/7d")
    args = parser.parse_args()

    import time
    import uuid

    EXPIRE_MODES = {
        'burn_after_read': 0,
        '24h': 24 * 60 * 60 * 1000,
        '7d': 7 * 24 * 60 * 60 * 1000,
        'permanent': 0
    }

    secret_text = args.text.strip()
    passcode = args.passcode.strip()
    secret_type = args.type
    expire_mode = args.expire

    current_time = int(time.time() * 1000)

    if secret_type == "tree":
        expire_mode = "permanent"
        expire_time = 0
        is_deleted = False
    else:
        expire_time = current_time + EXPIRE_MODES[expire_mode] if EXPIRE_MODES[expire_mode] > 0 else 0
        is_deleted = False

    secret_id = str(uuid.uuid4())[:8]
    secrets[secret_id] = {
        'secret': secret_text,
        'passcode': passcode,
        'type': secret_type,
        'unlock_time': 0,
        'created': time.time(),
        'is_deleted': is_deleted,
        'expire_mode': expire_mode,
        'expire_time': expire_time
    }
    save_data()
    print("✅ 创建成功，ID：", secret_id)

def cmd_view():
    parser = argparse.ArgumentParser()
    parser.add_argument("id", help="秘密ID")
    parser.add_argument("--passcode", "-p", default="", help="密码")
    args = parser.parse_args()
    secret_id = args.id
    passcode = args.passcode.strip()

    if secret_id not in secrets:
        print("❌ 秘密不存在")
        return

    secret = secrets[secret_id]
    if secret.get('is_deleted'):
        print("❌ 秘密已销毁")
        return

    print("📄 内容：")
    print(secret["secret"])

def cmd_list():
    print("📋 所有树洞/秘密列表：")
    for sid, item in secrets.items():
        if not item.get("is_deleted"):
            print(f"- {sid}  类型:{item['type']}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("用法：")
        print("  python cli.py create '内容' -p 123456 -t tree")
        print("  python cli.py view 秘密ID -p 123456")
        print("  python cli.py list")
        sys.exit()

    cmd = sys.argv[1]
    sys.argv.pop(1)

    if cmd == "create":
        cmd_create()
    elif cmd == "view":
        cmd_view()
    elif cmd == "list":
        cmd_list()
    else:
        print("未知命令")