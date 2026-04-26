from flask import Flask, request, jsonify
from realize_aesgcm import encrypt_secret, decrypt_secret, hash_password, verify_password
import uuid

app = Flask(__name__)

# 模拟数据库
storage = {}

# =========================
# 🌿 存储秘密
# =========================
@app.route("/store", methods=["POST"])
def store_secret():

    data = request.json

    secret = data.get("secret")
    # ✅ 兼容前端 passcode / password
    password = data.get("passcode") or data.get("password")

    if not secret or not password:
        return jsonify({
            "success": False,
            "error": "缺少内容或密码"
        })

    # 🔐 加密秘密
    nonce, ciphertext = encrypt_secret(secret)

    # 🔑 哈希密码
    password_hash = hash_password(password)

    # 🆔 生成ID
    secret_id = str(uuid.uuid4())

    storage[secret_id] = {
        "nonce": nonce,
        "ciphertext": ciphertext,
        "password_hash": password_hash
    }

    return jsonify({
        "success": True,
        "id": secret_id
    })


# =========================
# 🔍 获取秘密（阅后即焚）
# =========================
@app.route("/retrieve", methods=["POST"])
def retrieve_secret():

    data = request.json

    secret_id = data.get("id")
    password = data.get("password")

    if not secret_id or not password:
        return jsonify({"error": "参数缺失"}), 400

    if secret_id not in storage:
        return jsonify({"error": "Secret not found"}), 404

    record = storage[secret_id]

    # 🔐 验证密码
    if not verify_password(password, record["password_hash"]):
        return jsonify({"error": "Wrong password"}), 403

    # 🔓 解密
    plaintext = decrypt_secret(
        record["nonce"],
        record["ciphertext"]
    )

    # 💥 一次性销毁
    del storage[secret_id]

    return jsonify({
        "secret": plaintext
    })


# =========================
# 🤖 AI温柔回复（新增）
# =========================
@app.route('/api/ai-reply', methods=['POST'])
def ai_reply():
    data = request.json

    content = data.get("content", "")
    emotion = data.get("emotion", "calm")

    # 🌈 情绪驱动回复
    if emotion == "sad":
        reply = "抱抱你…有些难过不用急着好起来，我在这里陪你。"
    elif emotion == "happy":
        reply = "听起来很棒！你的快乐也感染到我了 ✨"
    elif emotion == "angry":
        reply = "你的情绪很真实，被理解很重要，可以慢慢说出来。"
    elif emotion == "anxious":
        reply = "慢一点也没关系，你已经在努力了，我会陪着你。"
    else:
        reply = "我在听，你可以慢慢说。"

    return jsonify({
        "reply": reply
    })


# =========================
# 🚀 启动
# =========================
if __name__ == "__main__":
    app.run(debug=True)
