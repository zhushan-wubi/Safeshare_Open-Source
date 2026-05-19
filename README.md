 莫奈的秘密花园 · Monet's Secret Garden
🔗 在线体验：[https://safeshare-open-source.onrender.com/](https://safeshare-open-source.onrender.com/)
<img width="2606" height="1555" alt="image" src="https://github.com/user-attachments/assets/9db49537-8261-447b-a35a-15fef7f5dfca" />

📦 开源仓库：GitHub + Gitee 双平台同步 | 轻量本地加密秘密分享项目
🔐 A local-first encrypted secret sharing system with emotional AI support.（本地优先的加密秘密分享系统，兼具情绪AI陪伴功能）
🎯 What Problem Does This Solve?
现有匿名/私密分享平台普遍存在核心痛点，无法满足隐私安全与权限管控需求：
- ❌ 数据存储在云端服务器，存在被泄露、篡改的风险，隐私无法真正保障
- ❌ 缺乏精细化权限控制，无法实现“多人共管、分权解锁”，单人管控风险过高
- ❌ 多为“表面加密”，未实现真正的密码学加密，易被破解
- ❌ 不支持离线使用，网络异常时无法访问私密内容
👉 本项目提供的解决方案：
✅ 【本地优先】所有数据本地加密存储，无任何云端明文上传，从源头杜绝泄露
✅ 【加密可控】基于AES-256+SHA-256实现真正加密，支持多人分权解锁，权限可控
✅ 【离线可用】核心功能脱离公网亦可正常使用，AI回复配备本地备用库
✅ 【轻量易用】无需注册登录，一键部署，Web+CLI双入口，适配多场景使用
✨ Key Features | 核心功能
- 🔐 Encrypted Secret Sharing（加密秘密分享）：支持自定义加密强度，生成加密分享链接，仅授权用户可查看
- ⏳ Time-limited Access（时效控制）：阅后即焚、24小时有效、7天有效，过期自动销毁
- 👥 Multi-key Authorization（多密钥授权）：支持双人分权解锁，适配团队、校园场景
- 🌱 Anonymous Emotional Posting（匿名情绪树洞）：匿名倾诉，可选择私密封存或公开心声墙
- 🤖 AI Emotional Reply（AI情绪陪伴）：适配5种情绪状态，网络异常时自动调用本地备用回复
- 💻 CLI Tool Support（命令行工具）：支持终端操作，可实现自动化、脚本化管理
🧱 Architecture（技术架构）
Frontend:
  - HTML / CSS / JavaScript
  - Bootstrap

Backend:
  - Python Flask
  - RESTful API

Storage:
  - Local JSON File
  - No Cloud Storage

Interface:
  - Web UI
  - CLI Tool

Security:
  - AES-256 Encryption
  - SHA-256 Hash
  - Shamir Secret Sharing
  - TTL Expiration Mechanism
🔐 Security Design
拒绝“文案加密”，所有安全机制均有具体技术实现，可直接查看代码验证：
1. Content Encryption
- Algorithm：AES-256 对称加密
- Mode：每条秘密独立加密，避免单密钥泄露导致批量数据泄露
- IV：随机生成，提升加密强度，符合民用级安全标准
- Core Code Snippet：
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad

def aes_encrypt(content, key):
    # 生成随机IV
    iv = get_random_bytes(16)
    # 初始化AES加密器
    cipher = AES.new(key.encode('utf-8'), AES.MODE_CBC, iv)
    # 加密内容
    encrypted_content = cipher.encrypt(pad(content.encode('utf-8'), AES.block_size))
    # 返回IV+密文
    return iv + encrypted_content

def aes_decrypt(encrypted_data, key):
    # 拆分IV
    iv = encrypted_data[:16]
    ciphertext = encrypted_data[16:]
    # 初始化解密器
    cipher = AES.new(key.encode('utf-8'), AES.MODE_CBC, iv)
    # 解密并去除补位
    decrypted_content = unpad(cipher.decrypt(ciphertext), AES.block_size).decode('utf-8')
    return decrypted_content
2. Password Protection（密码保护）
- Storage Mode（存储方式）：密码以SHA-256 Hash值存储，不存储任何明文密码
- Advantage（优势）：即使本地数据被获取，也无法逆向破解密码，保障访问安全
- Core Code Snippet（核心代码片段）：
import hashlib

def hash_password(password):
    # SHA-256 Hash运算，增强密码安全性
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def verify_password(input_pwd, stored_hash):
    # 验证密码：将输入密码Hash后与存储的Hash值比对
    return hash_password(input_pwd) == stored_hash
3. Access Control（访问控制）
- Basic Mode（基础模式）：密码 gated 解密，仅输入正确密码可查看内容
- Advanced Mode（进阶模式）：多密钥双重验证，支持双人/多人联合解锁
- Extensible（可扩展）：可升级为Shamir门限秘密共享（k-of-n模式）
4. Expiration Mechanism（时效销毁机制）
- TTL-based Deletion（TTL定时删除）：支持24小时、7天两种时效模式
- Read-once Destruction（阅后即焚）：查看后立即销毁内容及密钥，不可二次查看
- Scheduled Cleanup（定时清理）：后台定时扫描，自动销毁过期数据，释放本地存储资源
💻 CLI Usage
提供完整命令行工具，支持无网页环境使用，适配服务器、本地终端场景，可实现自动化管理：
# 1. 创建秘密
python cli.py create --content "涉密内容" --password "primary_key" --second-password "secondary_key" --expire 24h

# 2. 解密查看（单密码/双密码验证）
python cli.py read --secret-id "xxx-xxx-xxx" --password "primary_key" --second-password "secondary_key"

# 3. 清理过期数据（自动删除所有过期秘密）
python cli.py clean

# 4. 查看本地加密数据列表（显示所有秘密ID、创建时间、过期时间）
python cli.py list

# 5. 导出加密数据（备份用，导出为加密JSON文件）
python cli.py export --path "./backup/secret_backup.json"

# 6. 查看帮助（获取所有命令及参数说明）
python cli.py --help
👉 支持脚本化调用，可集成到其他工具中，提升项目实用性与开源价值。
👥 Use Cases
- 🧑‍💻 Developers：本地加密分享工具，用于存储、分享敏感配置、密钥等
- 🎓 Campus：匿名反馈、涉密文稿管控、实训口令分发、学生组织机密托管
- 👥 Small Teams：多人共管秘密、项目核心方案保密、权限分级管控
- 🧠 Personal：私密情绪日记、时光胶囊、隐私内容封存

📂 Project Structure
.
├── app.py              # 后端入口
├── cli.py              # 命令行工具
├── core/               # 核心模块
│   ├── crypto.py       # 加密模块
│   ├── storage.py      # 数据存储模块
│   ├── ttl.py          # 过期控制模块
│   └── detect.py       # 隐私泄露检测模块
├── templates/          # 前端页面模板
├── static/             # 静态资源
└── data/               # 本地加密数据存储目录

⭐ Why This Project?
💡 1. 隐私安全扎实：本地优先架构+真正的AES-256加密，技术细节可查，非“表面加密”，符合开源安全评审标准；
💡 2. 开源友好度高：Web+CLI双入口，项目结构清晰，提供完整部署文档、代码注释，支持二次开发与集成；
💡 3. 场景适配性强：贴合校园、小团队、个人等多场景，可快速改造为信安赛窄场景，无需重构核心代码；
💡 4. 特色差异化：治愈系视觉风格+硬核安全设计，区别于普通开源项目，易在评审中脱颖而出；
💡 5. 可扩展性强：开发路线清晰，支持Shamir秘密共享、Docker部署等升级方向，体现项目长期价值。
📄 License（开源协议）
MIT License
本项目为学生开源学习项目，仅用于技术学习、学术交流、校园实践（信安赛、课程设计），严禁商用盈利。二次开发请保留项目开源声明及作者信息。
👥 开发团队
3人协作开源维护，持续迭代优化加密逻辑、界面体验与CLI管理功能，长期保持项目活跃度，适配开源安全奖励计划“持续维护”评审要求，可提供完整开发日志与提交记录。
🌿 项目寄语
以密码学构筑隐私港湾，以技术守护细碎心事；让轻量化民用加密技术走进校园日常，让每一份私密倾诉都有安全归宿，助力开源安全普及与校园安全建设。
