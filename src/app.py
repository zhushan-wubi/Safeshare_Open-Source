from flask import Flask, request, jsonify, render_template
import uuid
import time
import json
import os

app = Flask(__name__)

# 🔐 数据存储文件
DATA_FILE = "secrets_data.json"

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
# ✨ 新增：兼容前端/api/store接口（核心修复404）
# 说明：不修改原有/api/secret，新增/api/store映射到原有逻辑
# ==============================
@app.route('/api/store', methods=['POST'])
def store_secret():
    # 1. 接收前端传的参数（适配前端的字段名）
    data = request.json
    secret_text = data.get('secret')
    password = data.get('password')  # 前端传的是password
    secret_type = data.get('type', 'normal')
    unlock_time = data.get('unlock_time')
    expire_mode = data.get('expiry_mode', 'burn_after_read')  # 前端传的是expiry_mode
    expiry_hours = data.get('expiry_hours', 1)
    
    # 2. 转换为你原有代码的字段名（保证逻辑不变）
    # 映射expiry_mode到expire_mode，兼容前端参数
    expire_mode_map = {
        'burn_after_read': 'burn_after_read',
        '24h': '24h',
        '7d': '7d'
    }
    final_expire_mode = expire_mode_map.get(expire_mode, 'burn_after_read')
    
    # 3. 复用你原有/create_secret的核心逻辑（完全不改动）
    current_time = int(time.time() * 1000)
    expire_time = 0  # 默认阅后即焚
    
    # 根据过期模式计算过期时间（复用你的逻辑）
    if final_expire_mode == '24h':
        expire_time = current_time + 24 * 60 * 60 * 1000  # 24小时后（毫秒）
    elif final_expire_mode == '7d':
        expire_time = current_time + 7 * 24 * 60 * 60 * 1000  # 7天后（毫秒）

    if not secret_text:
        return jsonify({'success': False, 'error': '内容不能为空'})

    secret_id = str(uuid.uuid4())[:8]

    # 存储数据（完全复用你的字段结构）
    secrets[secret_id] = {
        'secret': secret_text,
        'passcode': password,  # 映射到你原有passcode字段
        'type': secret_type,
        'unlock_time': unlock_time,
        'created': time.time(),
        'is_deleted': False,
        'expire_mode': final_expire_mode,  # 存储过期模式
        'expire_time': expire_time   # 存储过期时间（毫秒级）
    }

    save_data()  # 💾 保存

    # 4. 返回前端需要的格式（兼容前端接收id的逻辑）
    return jsonify({
        'success': True,
        'id': secret_id,
        # 保留你原有返回字段，保证兼容性
        'error': None
    })

# ==============================
# ✨ 原有创建秘密接口（完全保留，不修改）
# ==============================
@app.route('/api/secret', methods=['POST'])
def create_secret():
    data = request.json

    secret_text = data.get('secret')
    passcode = data.get('passcode')
    secret_type = data.get('type', 'tree')
    unlock_time = data.get('unlock_time')
    # 🔥 强制设置为24h模式（测试用）
    # 取消硬编码，恢复动态获取
    expire_mode = data.get('expire_mode', 'burn_after_read')  
    current_time = int(time.time() * 1000)
    expire_time = 0  # 默认阅后即焚
    
    # 根据过期模式计算过期时间
    if expire_mode == '24h':
        expire_time = current_time + 24 * 60 * 60 * 1000  # 24小时后（毫秒）
    elif expire_mode == '7d':
        expire_time = current_time + 7 * 24 * 60 * 60 * 1000  # 7天后（毫秒）

    if not secret_text:
        return jsonify({'success': False, 'error': '内容不能为空'})

    secret_id = str(uuid.uuid4())[:8]

    secrets[secret_id] = {
        'secret': secret_text,
        'passcode': passcode,
        'type': secret_type,
        'unlock_time': unlock_time,
        'created': time.time(),
        'is_deleted': False,
        'expire_mode': expire_mode,  # 存储过期模式
        'expire_time': expire_time   # 存储过期时间（毫秒级）
    }

    save_data()  # 💾 保存

    return jsonify({
        'success': True,
        'id': secret_id
    })

## 🔓 获取秘密（修复版：核心修改过期逻辑）
@app.route('/api/secret/<secret_id>', methods=['POST'])
@app.route('/api/secret/<secret_id>', methods=['POST'])
def get_secret(secret_id):
    data = request.json
    passcode = data.get('passcode', '').strip()
    current_time = int(time.time() * 1000)  # 统一毫秒级时间戳
    
    # 1. 先检查秘密是否存在
    if secret_id not in secrets:
        return jsonify({'success': False, 'error': '秘密不存在', 'error_type': 'not_exist'})
    
    # 2. 检查是否已被标记删除（真销毁）
    secret = secrets[secret_id]
    if secret.get('is_deleted', False):
        return jsonify({'success': False, 'error': '秘密已销毁，无法再次查看', 'error_type': 'destroyed'})

    # 核心修复：3. 校验过期时间（非阅后即焚模式）
    expire_mode = secret.get('expire_mode', 'burn_after_read')
    expire_time = secret.get('expire_time', 0)
    
    # 只有非阅后即焚模式才校验过期时间
    if expire_mode != 'burn_after_read':
        # 确保过期时间有效（>0）且当前时间已超过过期时间
        if expire_time > 0 and current_time > expire_time:
            # 超时自动标记删除
            secrets[secret_id]['is_deleted'] = True
            save_data()
            # 友好的中文提示
            expire_text = '24小时' if expire_mode == '24h' else '7天'
            return jsonify({
                'success': False, 
                'error': f'秘密已过期（{expire_text}有效），无法查看', 
                'error_type': 'expired'
            })

    # 4. 时光胶囊：校验解锁时间（原有逻辑，保留）
    if secret.get('type') == 'time':
        unlock_time = secret.get('unlock_time')
        if unlock_time:
            # 统一转换为毫秒级对比
            if current_time < int(unlock_time):
                return jsonify({
                    'success': False,
                    'error': '⏳ 还没到解锁时间，暂时无法查看',
                    'error_type': 'not_unlock'
                })

    # 5. 双人秘密：校验密码（原有逻辑，保留）
    if secret.get('type') == 'double':
        stored_pass = secret.get('passcode', '').strip()
        passcodes = stored_pass.split("|")
        
        if len(passcodes) != 2 or not passcodes[0] or not passcodes[1]:
            return jsonify({'success': False, 'error': '双人秘密密码格式错误', 'error_type': 'pass_error'})
        
        valid_pass1 = stored_pass       
        valid_pass2 = passcodes[0] + passcodes[1]
        
        if passcode != valid_pass1 and passcode != valid_pass2:
            return jsonify({'success': False, 'error': '密码错误', 'error_type': 'pass_error'})
    
    # 6. 普通秘密：校验密码（原有逻辑，保留）
    else:
        stored_pass = secret.get('passcode', '').strip()
        if stored_pass and passcode != stored_pass:
            return jsonify({'success': False, 'error': '密码错误', 'error_type': 'pass_error'})

    # 核心修复：7. 仅阅后即焚模式标记删除
    secret_content = secret['secret']
    # 只有 expire_mode 是 burn_after_read 时，才标记删除
    if expire_mode == 'burn_after_read':  
        secrets[secret_id]['is_deleted'] = True
        save_data()  # 立即保存修改
        # 返回标记：告诉前端是阅后即焚
        return jsonify({
            'success': True, 
            'secret': secret_content,
            'expire_mode': expire_mode,
            'is_burn': True
        })
    # 24h/7d 模式：不标记删除，返回模式信息
    else:
        expire_text = '24小时' if expire_mode == '24h' else '7天'
        return jsonify({
            'success': True, 
            'secret': secret_content,
            'expire_mode': expire_mode,
            'expire_text': expire_text,
            'is_burn': False
        })
# ==============================
# 🌳 获取树洞列表（原有逻辑，无修改）
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
# 🤖 AI 回复（原有逻辑，无修改）
# ==============================
@app.route('/api/ai-reply', methods=['POST'])
def ai_reply():
    data = request.json
    content = data.get("content", "")
    emotion = data.get("emotion", "calm")

    if emotion == "sad":
        reply = "像下雨天坐在窗边。雨会停，但不用现在停 🤍"
    elif emotion == "happy":
        reply = "听你开心，我也觉得今天的晚风会软一些 ✨"
    elif emotion == "angry":
        reply = "像石头砸进水面。愤怒的波纹会慢慢散去，但那一刻的真实，我看见了 🔥"
    elif emotion == "anxious":
        reply = "慢慢走，我在这。快慢都没关系 🌿"
    else:
        reply = "心里的声音终于小下去了。值得为此停一分钟 ✨"

    return jsonify({"reply": reply})


# ==============================
# 🚀 启动（原有逻辑，无修改）
# ==============================
if __name__ == '__main__':
    # Render会自动分配端口，读取环境变量PORT
    port = int(os.environ.get('PORT', 5000))
    # 必须绑定0.0.0.0，否则Render无法访问
    app.run(host='0.0.0.0', port=port, debug=False)
