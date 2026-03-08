from flask import Flask, request, jsonify
from realize_aesgcm import encrypt_secret, decrypt_secret, hash_password, verify_password
import uuid

app = Flask(__name__)

# 模拟数据库
storage = {}

# 存储秘密
@app.route("/store", methods=["POST"])
def store_secret():

    data = request.json

    secret = data["secret"]
    password = data["password"]

    # 加密秘密
    nonce, ciphertext = encrypt_secret(secret)

    # 哈希密码
    password_hash = hash_password(password)

    # 生成ID
    secret_id = str(uuid.uuid4())

    storage[secret_id] = {
        "nonce": nonce,
        "ciphertext": ciphertext,
        "password_hash": password_hash
    }

    return jsonify({
        "id": secret_id,
        "message": "Secret stored"
    })


# 获取秘密
@app.route("/retrieve", methods=["POST"])
def retrieve_secret():

    data = request.json

    secret_id = data["id"]
    password = data["password"]

    if secret_id not in storage:
        return jsonify({"error": "Secret not found"}), 404

    record = storage[secret_id]

    # 验证密码
    if not verify_password(password, record["password_hash"]):
        return jsonify({"error": "Wrong password"}), 403

    # 解密
    plaintext = decrypt_secret(
        record["nonce"],
        record["ciphertext"]
    )

    # 一次性销毁
    del storage[secret_id]

    return jsonify({
        "secret": plaintext
    })


if __name__ == "__main__":
    app.run(debug=True)