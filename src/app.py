from flask import Flask, request, jsonify, render_template
import uuid
import time
import json
import os

app = Flask(__name__)

# 🔐 数据存储文件
DATA_FILE = "data.json"

# 内存数据
secrets = {}

# ==============================
# 💾 数据持久化
# ==============================
def save_data():
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(secrets, f, ensure_ascii=False)

def load_data():
    global secrets
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            try:
                secrets = json.load(f)
            except:
                secrets = {}
    else:
        secrets = {}

# 启动时加载
load_data()

# ==============================
# 🌿 首页
# ==============================
@app.route('/')
def index():
    return render_template('index.html')


# ==============================
# 🔐 查看页面
# ==============================
@app.route('/view/<secret_id>')
def view(secret_id):
    return render_template('view.html')


# ==============================
# ✨ 创建秘密
# ==============================
@app.route('/api/secret', methods=['POST'])
def create_secret():
    data = request.json

    secret_text = data.get('secret')
    passcode = data.get('passcode')
    secret_type = data.get('type', 'tree')
    unlock_time = data.get('unlock_time')

    if not secret_text:
        return jsonify({'success': False, 'error': '内容不能为空'})

    secret_id = str(uuid.uuid4())[:8]

    secrets[secret_id] = {
        'secret': secret_text,
        'passcode': passcode,
        'type': secret_type,
        'unlock_time': unlock_time,
        'created': time.time()
    }

    save_data()  # 💾 保存

    return jsonify({
        'success': True,
        'id': secret_id
    })


# ==============================
# 🔓 获取秘密
# ==============================
@app.route('/api/secret/<secret_id>')
def get_secret(secret_id):
    passcode = request.args.get('passcode')
    secret = secrets.get(secret_id)

    if not secret:
        return jsonify({'success': False, 'error': '秘密不存在或已销毁'})

    # ⏳ 时间胶囊
    if secret.get('type') == 'time':
        unlock_time = secret.get('unlock_time')
        if unlock_time:
            now = int(time.time() * 1000)
            if now < int(unlock_time):
                return jsonify({
                    'success': False,
                    'error': '⏳ 还没到解锁时间'
                })

    # 🔐 密码
    if secret.get('passcode') != passcode:
        return jsonify({'success': False, 'error': '密码错误'})

    content = secret['secret']

    # ❗ 删除（一次性）
    del secrets[secret_id]
    save_data()

    return jsonify({
        'success': True,
        'secret': content
    })


# ==============================
# 🌳 获取树洞列表
# ==============================
@app.route('/api/treeholes')
def get_treeholes():
    result = []

    for key, value in secrets.items():
        if value.get("type") == "tree":
            result.append({
                "id": key,
                "content": value.get("secret"),
                "time": value.get("created")
            })

    return jsonify(result)


# ==============================
# 🤖 AI 回复
# ==============================
@app.route('/api/ai-reply', methods=['POST'])
def ai_reply():
    data = request.json
    content = data.get("content", "")
    emotion = data.get("emotion", "calm")

    if emotion == "sad":
        reply = "雨落在你心上，不需要急着撑伞。我会在这里，陪你慢慢等天晴。"
    elif emotion == "happy":
        reply = "听你开心，我也觉得今天的晚风会软一些。✨"
    elif emotion == "angry":
        reply = "像石头砸进水面。愤怒的波纹会慢慢散去，但那一刻的真实，我看见了。"
    elif emotion == "anxious":
        reply = "不用一下子走很远，我们一步一步来就好。"
    else:
        reply = "我在听，你可以慢慢说。"

    return jsonify({"reply": reply})


# ==============================
# 🚀 启动
# ==============================
if __name__ == '__main__':
    app.run(debug=True)