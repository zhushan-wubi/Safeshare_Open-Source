# app.py - 完整的Flask应用
from flask import Flask, render_template, request, jsonify, redirect, url_for
import os
import uuid
from datetime import datetime, timedelta

app = Flask(__name__)

# 临时存储（开发用）- 实际项目会用数据库
secrets_store = {}

@app.route('/')
def index():
    """主页"""
    return render_template('index.html')

@app.route('/view')
def view_page():
    """查看页面（无ID）"""
    return render_template('view.html')

@app.route('/view/<secret_id>')
def view_secret(secret_id):
    """查看特定秘密的页面"""
    return render_template('view.html', secret_id=secret_id)

@app.route('/api/secret', methods=['POST'])
def create_secret():
    """创建新秘密的API端点"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        secret_id = str(uuid.uuid4())[:8]  # 生成8位ID
        
        # 获取过期时间
        expiry = data.get('expiry', '1')
        expiry_hours = int(expiry)
        
        # 存储秘密（实际项目中应该加密存储）
        secrets_store[secret_id] = {
            'id': secret_id,
            'encrypted_secret': data.get('secret', ''),
            'passcode_hash': data.get('passcode', ''),
            'created_at': datetime.now(),
            'expires_at': datetime.now() + timedelta(hours=expiry_hours),
            'max_views': 1,
            'view_count': 0,
            'viewed': False
        }
        
        return jsonify({
            'success': True,
            'id': secret_id,
            'message': 'Secret created successfully'
        })
        
    except Exception as e:
        print(f"Error creating secret: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/secret/<secret_id>', methods=['POST'])
def get_secret(secret_id):
    """获取秘密的API端点"""
    try:
        data = request.get_json()
        if not data or 'passcode' not in data:
            return jsonify({'success': False, 'error': 'Missing passcode'}), 400
        
        # 检查秘密是否存在
        if secret_id not in secrets_store:
            return jsonify({'success': False, 'error': 'Secret not found'}), 404
        
        secret_data = secrets_store[secret_id]
        
        # 检查是否已查看
        if secret_data['viewed']:
            return jsonify({'success': False, 'error': 'Secret already viewed'}), 410
        
        # 检查密码（简化验证，实际应该使用hash验证）
        if data['passcode'] != secret_data['passcode_hash']:
            return jsonify({'success': False, 'error': 'Incorrect passcode'}), 401
        
        # 标记为已查看
        secrets_store[secret_id]['viewed'] = True
        secrets_store[secret_id]['view_count'] += 1
        
        # 返回秘密
        return jsonify({
            'success': True,
            'secret': secret_data['encrypted_secret'],
            'viewed': True,
            'remaining_views': 0
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/health')
def health_check():
    """健康检查"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '0.1.0'
    })

@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', 
                          error_code=404,
                          error_message='页面未找到'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('error.html',
                          error_code=500,
                          error_message='服务器内部错误'), 500

if __name__ == '__main__':
    print("🚀 启动 SafeShare 开发服务器...")
    print("🌐 访问地址: http://localhost:5000")
    print("📁 静态文件: http://localhost:5000/static/")
    print("🛑 按 Ctrl+C 停止服务器")
    
    app.run(
        port=5000,
        debug=True
    )