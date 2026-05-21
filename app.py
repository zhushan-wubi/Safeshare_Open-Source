from flask import Flask, request, jsonify, render_template
from realize_aesgcm import encrypt_secret, decrypt_secret, hash_password, verify_password
import uuid
import time
import json
import os

app = Flask(__name__)
storage = {}

DATA_FILE = "encrypted_secrets.json"

def save_encrypted_data():
    """保存加密后的秘密到文件（持久化）"""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(storage, f, ensure_ascii=False)

def load_encrypted_data():
    """启动时加载加密数据"""
    global storage
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            try:
                storage = json.load(f)
            except:
                storage = {}
    else:
        storage = {}


load_encrypted_data()


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/view/<secret_id>')
def view_secret(secret_id):
    return render_template('view.html', secret_id=secret_id)


@app.route("/api/store", methods=["POST"])
def store_secret():
    try:
        data = request.json
        # 1. 接收前端参数（兼容前端字段名）
        secret = data.get("secret")          # 秘密内容
        password = data.get("password")      # 密码
        secret_type = data.get("type", "normal")  # 秘密类型（time/double/tree/normal）
        expiry_mode = data.get("expiry_mode", "burn_after_read")  # 过期模式
        expiry_hours = data.get("expiry_hours", 1)  # 过期小时数
        unlock_time = data.get("unlock_time")       # 时光胶囊解锁时间

        # 2. 基础校验
        if not secret:
            return jsonify({"error": "内容不能为空", "success": False}), 400
        if not password:
            return jsonify({"error": "请设置密码", "success": False}), 400


        nonce, ciphertext = encrypt_secret(secret)  # AES-GCM加密
        password_hash = hash_password(password)     # 密码哈希
        secret_id = str(uuid.uuid4())               # 生成唯一ID

        # 4. 扩展字段
        current_time = int(time.time() * 1000)
        expire_time = 0  # 默认阅后即焚
        
        # 计算过期时间
        if expiry_mode == '24h':
            expire_time = current_time + 24 * 60 * 60 * 1000
        elif expiry_mode == '7d':
            expire_time = current_time + 7 * 24 * 60 * 60 * 1000

        # 5. 存储
        storage[secret_id] = {
     
            "nonce": nonce,
            "ciphertext": ciphertext,
            "password_hash": password_hash,
            "type": secret_type,
            "expiry_mode": expiry_mode,
            "expire_time": expire_time,
            "unlock_time": unlock_time,
            "created_at": current_time,
            "is_deleted": False
        }

        # 持久化保存
        save_encrypted_data()

        # 6. 返回前端需要的格式
        return jsonify({
            "id": secret_id,
            "message": "Secret stored",
            "success": True
        }), 200

    except Exception as e:
        print(f"存储失败：{str(e)}")
        return jsonify({"error": str(e), "success": False}), 500


@app.route("/api/retrieve", methods=["POST"])
def retrieve_secret():
    try:
        data = request.json
        secret_id = data.get("id")
        password = data.get("password")

        # 1. 基础校验
        if not secret_id or not password:
            return jsonify({"error": "ID和密码不能为空", "success": False}), 400

        # 2. 检查秘密是否存在/已删除
        if secret_id not in storage:
            return jsonify({"error": "Secret not found", "success": False, "error_type": "not_exist"}), 404
        
        record = storage[secret_id]
        if record.get("is_deleted", False):
            return jsonify({"error": "秘密已销毁", "success": False, "error_type": "destroyed"}), 404

        # 3. 新增：过期时间校验（非阅后即焚模式）
        current_time = int(time.time() * 1000)
        expiry_mode = record.get("expiry_mode", "burn_after_read")
        expire_time = record.get("expire_time", 0)
        
        if expiry_mode != 'burn_after_read' and expire_time > 0 and current_time > expire_time:
            storage[secret_id]["is_deleted"] = True
            save_encrypted_data()
            expire_text = '24小时' if expiry_mode == '24h' else '7天'
            return jsonify({
                "error": f'秘密已过期（{expire_text}有效）', 
                "success": False, 
                "error_type": "expired"
            }), 403

        # 4. 新增：时光胶囊解锁时间校验
        if record.get("type") == "time" and record.get("unlock_time"):
            if current_time < int(record["unlock_time"]):
                return jsonify({
                    "error": "还没到解锁时间", 
                    "success": False, 
                    "error_type": "not_unlock"
                }), 403

        # 5. 新增：双人秘密密码校验
        if record.get("type") == "double":
            # 双人秘密密码格式：passA|passB，哈希后存储
            stored_hash = record["password_hash"]
            # 拆分密码（前端传的是passA+passB）
            passcodes = password.split("|") if "|" in password else [password]
            if len(passcodes) == 2:
                # 验证组合密码
                valid_pass = passcodes[0] + passcodes[1]
                if verify_password(valid_pass, stored_hash) or verify_password(password, stored_hash):
                    pass
                else:
                    return jsonify({"error": "Wrong password", "success": False, "error_type": "pass_error"}), 403
            else:
                # 普通验证
                if not verify_password(password, stored_hash):
                    return jsonify({"error": "Wrong password", "success": False, "error_type": "pass_error"}), 403
        else:

            if not verify_password(password, record["password_hash"]):
                return jsonify({"error": "Wrong password", "success": False, "error_type": "pass_error"}), 403


        plaintext = decrypt_secret(record["nonce"], record["ciphertext"])


        if expiry_mode == "burn_after_read":
            del storage[secret_id]
            save_encrypted_data()
            is_burn = True
        else:
            storage[secret_id]["is_deleted"] = False  # 非阅后即焚不删除
            is_burn = False


        return jsonify({
            "secret": plaintext,
            "success": True,
            "expiry_mode": expiry_mode,
            "is_burn": is_burn,
            "expire_text": '24小时' if expiry_mode == '24h' else '7天' if expiry_mode == '7d' else '阅后即焚'
        }), 200

    except Exception as e:
        print(f"解密失败：{str(e)}")
        return jsonify({"error": str(e), "success": False}), 500


@app.route('/api/treeholes')
def get_treeholes():
    """获取树洞列表（仅返回tree类型的秘密）"""
    result = []
    for secret_id, record in storage.items():
        if record.get("type") == "tree" and not record.get("is_deleted"):

            try:
                plaintext = decrypt_secret(record["nonce"], record["ciphertext"])
                result.append({
                    "id": secret_id,
                    "content": plaintext,
                    "time": record.get("created_at")
                })
            except:
                continue
    return jsonify(result), 200

@app.route('/api/ai-reply', methods=['POST'])
def ai_reply():
    """AI温柔回复接口"""
    data = request.json
    emotion = data.get("emotion", "calm")
    
    replies = {
        'happy': '听你开心，我也觉得今天的晚风会软一些 🌼',
        'sad': '像下雨天坐在窗边。雨会停，但不用现在停 🤍',
        'angry': '像石头砸进水面。愤怒的波纹会慢慢散去，但那一刻的真实，我看见了 🔥',
        'anxious': '慢慢走，我在这。快慢都没关系 🌿',
        'calm': '心里的声音终于小下去了。值得为此停一分钟 ✨'
    }
    return jsonify({"reply": replies[emotion]}), 200

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
