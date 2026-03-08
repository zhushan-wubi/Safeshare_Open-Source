# Safeshare\_Open-Source

A minimal, secure secret sharing tool for temporary secrets

**安全特性**



1.数据保护

\- AES-256-GCM加密：所有秘密在存储前已加密

\- bcrypt密码哈希：访问密码经过加盐哈希处理

\- 自动密钥轮换：支持定期更换主密钥

\- 内存安全：秘密仅在内存中短暂解密

2.安全防御

\- 速率限制：防止暴力破解攻击

\- 安全HTTP头：CSP、HSTS、XSS保护

\- 输入验证：所有用户输入经过严格清理

\- 审计日志：记录所有访问尝试（不含秘密内容）

3\.技术架构

客户端 (浏览器) → HTTPS → Flask应用 → SQLite数据库

↑ ↓

加密/解密 加密存储



技术栈

\- 后端框架: Python Flask

\- 加密库: cryptography (AES-256-GCM, bcrypt)

\- 数据库: SQLite (开发) / PostgreSQL (生产)

\- 前端: Bootstrap 5 + 原生JavaScript

\- 部署: Docker + Docker Compose

