import time
import uuid
import json
import os
import logging
from flask import Flask, request, jsonify, render_template, redirect, url_for
import requests



app = Flask(__name__)
app.config['SECRET_KEY'] = 'monet-secret-garden-2025'


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


EXPIRE_MODES = {
    'burn_after_read': 0,    
    '24h': 24 * 60 * 60 * 1000,  
    '7d': 7 * 24 * 60 * 60 * 1000, 
    'permanent': 0  
}


DATA_FILE = 'secrets.json'


DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY", "")
DASHSCOPE_URL = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"


def load_data():

    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    except Exception as e:
        logger.error(f"加载数据失败: {e}")
        return {}

def save_data(data=None):

    try:
        save_data = data if data else secrets
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, ensure_ascii=False, indent=2)
        logger.info("数据保存成功")
    except Exception as e:
        logger.error(f"保存数据失败: {e}")

secrets = load_data()


@app.route('/')
def index():

    return render_template('index.html')

@app.route('/view/<secret_id>')
def view_secret(secret_id):

    return render_template('view.html', secret_id=secret_id)


@app.route('/api/secret', methods=['POST'])
def create_secret():

    try:
        data = request.json or {}
        secret_text = data.get('secret', '').strip()
        passcode = data.get('passcode', '').strip()
        secret_type = data.get('type', 'normal')  
        unlock_time = data.get('unlock_time', 0)
        # 仅此处做兼容修改，接收前端双字段，解决过期模式识别失效
        expire_mode = data.get('expire_mode') or data.get('expiry_mode') or 'burn_after_read'

        if not secret_text:
            return jsonify({'success': False, 'error': '秘密内容不能为空'}), 400

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
            'unlock_time': unlock_time,
            'created': time.time(),
            'is_deleted': is_deleted,
            'expire_mode': expire_mode,
            'expire_time': expire_time
        }


        save_data()
        logger.info(f"创建新秘密: {secret_id} (类型: {secret_type})")

        return jsonify({
            'success': True,
            'id': secret_id,
            'message': '秘密创建成功'
        }), 201

    except Exception as e:
        logger.error(f"创建秘密失败: {e}")
        return jsonify({'success': False, 'error': '服务器错误'}), 500

@app.route('/api/secret/<secret_id>', methods=['POST'])
def get_secret(secret_id):
    """获取秘密内容（支持密码验证和过期检查）"""
    try:
        data = request.json or {}
        passcode = data.get('passcode', '').strip()
        current_time = int(time.time() * 1000)
        

        if secret_id not in secrets:
            return jsonify({'success': False, 'error': '秘密不存在', 'error_type': 'not_exist'}), 404
        
        secret = secrets[secret_id]

        secret_type = secret.get('type', 'normal')
        

        if secret.get('is_deleted', False):
            return jsonify({'success': False, 'error': '秘密已销毁，无法再次查看', 'error_type': 'destroyed'}), 410
        
        expire_mode = secret.get('expire_mode', 'burn_after_read')
        expire_time = secret.get('expire_time', 0)
        

        if expire_mode != 'burn_after_read' and expire_mode != 'permanent' and expire_time > 0 and current_time > expire_time:
            secrets[secret_id]['is_deleted'] = True
            save_data()
            expire_text = '24小时' if expire_mode == '24h' else '7天'
            return jsonify({
                'success': False, 
                'error': f'秘密已过期（{expire_text}有效），无法查看', 
                'error_type': 'expired'
            }), 410
        

        if secret_type == 'time':
            unlock_time = secret.get('unlock_time')
            if unlock_time and current_time < int(unlock_time):
                return jsonify({
                    'success': False,
                    'error': '⏳ 还没到解锁时间，暂时无法查看',
                    'error_type': 'not_unlock'
                }), 403
        

        if secret_type == 'double':
            stored_pass = secret.get('passcode', '').strip()
            passcodes = stored_pass.split("|")
            
            if len(passcodes) != 2 or not all(passcodes):
                logger.warning(f"双人秘密格式异常: {secret_id}")
                return jsonify({'success': False, 'error': '双人秘密格式错误', 'error_type': 'pass_error'}), 400
            
            valid_pass1 = stored_pass
            valid_pass2 = ''.join(passcodes)
            
            if passcode not in (valid_pass1, valid_pass2):
                return jsonify({'success': False, 'error': '密码错误', 'error_type': 'pass_error'}), 401
        

        elif secret_type != "tree":
            stored_pass = secret.get('passcode', '').strip()
            if stored_pass and passcode != stored_pass:
                return jsonify({'success': False, 'error': '密码错误', 'error_type': 'pass_error'}), 401
        

        secret_content = secret['secret']
        if expire_mode == 'burn_after_read' and secret_type != "tree":
            secrets[secret_id]['is_deleted'] = True
            save_data()
            logger.info(f"秘密已销毁: {secret_id} (阅后即焚)")
            return jsonify({
                'success': True, 
                'secret': secret_content,
                'expire_mode': expire_mode,
                'is_burn': True
            }), 200
        

        if expire_mode == 'permanent':
            expire_text = '永久有效'
        else:
            expire_text = '24小时' if expire_mode == '24h' else '7天'
            
        logger.info(f"秘密已查看: {secret_id}, 过期模式: {expire_mode}")
        return jsonify({
            'success': True, 
            'secret': secret_content,
            'expire_mode': expire_mode,
            'expire_text': expire_text,
            'is_burn': False
        }), 200
    
    except Exception as e:
        logger.error(f"获取秘密失败 ({secret_id}): {e}")
        return jsonify({'success': False, 'error': '服务器错误'}), 500

@app.route('/api/treeholes', methods=['GET'])
def get_treeholes():

    try:

        treeholes = []
        for secret_id, secret in secrets.items():
            if secret.get('type') == 'tree' and not secret.get('is_deleted', False):
                treeholes.append({
                    'id': secret_id,
                    'content': secret['secret'],
                    'created': secret['created']
                })
        

        treeholes.sort(key=lambda x: x['created'], reverse=True)
        return jsonify(treeholes), 200
    
    except Exception as e:
        logger.error(f"获取树洞失败: {e}")
        return jsonify([]), 500

@app.route('/api/ai-reply', methods=['POST'])
def ai_reply():

    try:
        data = request.json or {}
        emotion = data.get('emotion', 'calm')
        content = data.get('content', '')

        base_replies = {
            "happy": [
                "听你开心，我也觉得今天的晚风会软一些 🌼",
                "真好呀，能感受到你的快乐在发光 ✨",
                "把这份开心好好收藏，慢慢回味～ 🎈"
            ],
            "sad": [
                "像下雨天坐在窗边。雨会停，但不用现在停 🤍",
                "难过的时候不用假装坚强，我陪着你 💛",
                "你的情绪值得被看见，慢慢来，不着急 🕯️"
            ],
            "angry": [
                "像石头砸进水面。愤怒的波纹会慢慢散去，但那一刻的真实，我看见了 🔥",
                "生气是正常的，不用压抑自己的感受 🗣️",
                "等情绪稍微平复一点，我们再慢慢说 💨"
            ],
            "anxious": [
                "慢慢走，我在这。快慢都没关系 🌿",
                "不用逼自己立刻解决所有事，先喘口气吧 🫂",
                "焦虑的时候，就专注于当下的每一秒 🕰️"
            ],
            "calm": [
                "心里的声音终于小下去了。值得为此停一分钟 ✨",
                "这份平静真的很珍贵，好好感受吧 🌊",
                "慢慢来，生活本来就是这样的 🍵"
            ]
        }
        
        # 随机选一个回复
        replies = base_replies.get(emotion, base_replies['calm'])
        reply = replies[len(replies) // 2] 
        
        return jsonify({'success': True, 'reply': reply}), 200
    
    except Exception as e:
        logger.error(f"AI回复失败: {e}")
        return jsonify({'success': True, 'reply': '🌱 温柔的回响'}), 200

@app.route('/ai/privacy-detect', methods=['POST'])
def ai_privacy_detect():
    """AI识别文本中的隐私信息并打码（通义千问）"""
    try:
        data = request.json or {}
        text = data.get("text", "").strip()
        if not text:
            return jsonify({"masked_text": text, "has_sensitive": False}), 200

        prompt = f"""
        你是一个隐私保护助手，请识别以下文本中的所有隐私信息并打码：
        1. 手机号、身份证、邮箱、地址、微信号、QQ号等
        2. 打码规则：手机号显示前3后4，中间用****代替；地址只保留到市/区，后面用****代替；微信号/QQ号显示前1后1，中间用**代替
        3. 只返回处理后的文本，不要额外解释，格式为JSON：{{"masked_text": "处理后的文本", "has_sensitive": true/false}}
        
        文本：{text}
        """

        headers = {
            "Authorization": f"Bearer {DASHSCOPE_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "qwen-turbo",
            "input": {"prompt": prompt},
            "parameters": {"response_format": "json"}
        }

        response = requests.post(DASHSCOPE_URL, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()
        output = result["output"]["text"]

        import json as json_lib
        parsed = json_lib.loads(output)
        return jsonify({
            "masked_text": parsed.get("masked_text", text),
            "has_sensitive": parsed.get("has_sensitive", False)
        }), 200

    except Exception as e:
        logger.error(f"AI隐私检测失败: {e}")

        return jsonify({"masked_text": text, "has_sensitive": False}), 200


if __name__ == '__main__':
    # 确保数据文件目录存在
    if not os.path.exists(os.path.dirname(DATA_FILE)) and os.path.dirname(DATA_FILE):
        os.makedirs(os.path.dirname(DATA_FILE))
    
    # 启动Flask应用
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True  # 开发环境开启debug，生产环境关闭
    )
