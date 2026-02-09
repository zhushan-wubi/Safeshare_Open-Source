// SafeShare 主JavaScript文件 - 修改版

// 复制到剪贴板函数
function copyToClipboard(elementId) {
    const element = document.getElementById(elementId);
    if (!element) return;
    
    // 选择文本
    element.select();
    element.setSelectionRange(0, 99999);
    
    // 执行复制
    try {
        const successful = document.execCommand('copy');
        if (successful) {
            showToast('✅ 已复制到剪贴板', 'success');
        } else {
            showToast('❌ 复制失败', 'error');
        }
    } catch (err) {
        console.error('复制失败:', err);
        // 使用现代API
        navigator.clipboard.writeText(element.value).then(() => {
            showToast('✅ 已复制到剪贴板', 'success');
        }).catch(() => {
            showToast('❌ 复制失败', 'error');
        });
    }
}

// 显示Toast提示
function showToast(message, type = 'info') {
    // 移除已有的toast
    const existingToast = document.getElementById('safeShareToast');
    if (existingToast) {
        existingToast.remove();
    }
    
    // 创建toast元素
    const toast = document.createElement('div');
    toast.id = 'safeShareToast';
    toast.className = `toast align-items-center text-bg-${type} border-0 position-fixed bottom-0 end-0 m-3`;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');
    
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    
    document.body.appendChild(toast);
    
    // 显示toast
    const bsToast = new bootstrap.Toast(toast, { delay: 3000 });
    bsToast.show();
    
    // 3秒后自动移除
    setTimeout(() => {
        toast.remove();
    }, 3000);
}

// 页面加载完成后执行
document.addEventListener('DOMContentLoaded', function() {
    console.log('SafeShare 前端脚本已加载');
    
    // 首页的生成按钮事件
    const generateBtn = document.getElementById('generateBtn');
    if (generateBtn) {
        generateBtn.addEventListener('click', async function() {
            const secret = document.getElementById('secretText').value;
            const passcode = document.getElementById('passcode').value;
            const confirmPasscode = document.getElementById('confirmPasscode').value;
            
            // 验证
            if (!secret.trim()) {
                showToast('请输入秘密内容', 'warning');
                document.getElementById('secretText').focus();
                return;
            }
            
            if (!passcode) {
                showToast('请输入访问密码', 'warning');
                document.getElementById('passcode').focus();
                return;
            }
            
            if (passcode !== confirmPasscode) {
                showToast('两次输入的密码不一致', 'error');
                document.getElementById('confirmPasscode').focus();
                return;
            }
            
            if (passcode.length < 4) {
                showToast('密码至少需要4个字符', 'warning');
                document.getElementById('passcode').focus();
                return;
            }
            
            // 显示加载状态
            const originalText = generateBtn.innerHTML;
            generateBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 生成中...';
            generateBtn.disabled = true;
            
            try {
                // 获取过期时间
                const expiry = document.querySelector('input[name="expiry"]:checked').value;
                
                // 调用真实API
                const response = await fetch('/api/secret', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        secret: secret,
                        passcode: passcode,
                        expiry: parseInt(expiry)
                    })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    // 生成分享链接
                    const shareUrl = `${window.location.origin}/view/${data.id}`;
                    
                    // 更新UI
                    document.getElementById('shareLink').value = shareUrl;
                    document.getElementById('generatedPasscode').value = passcode;
                    
                    // 设置过期时间显示
                    let expiryText = '阅后即焚';
                    if (expiry === '24') expiryText = '24小时';
                    if (expiry === '168') expiryText = '7天';
                    document.getElementById('expiryTime').textContent = expiryText;
                    
                    // 显示结果区域
                    document.getElementById('resultSection').style.display = 'block';
                    
                    // 滚动到结果区域
                    document.getElementById('resultSection').scrollIntoView({ 
                        behavior: 'smooth' 
                    });
                    
                    showToast('✅ 安全链接已生成！', 'success');
                    
                    // 重置表单
                    document.getElementById('secretText').value = '';
                    document.getElementById('passcode').value = '';
                    document.getElementById('confirmPasscode').value = '';
                    
                } else {
                    showToast(`❌ 生成失败: ${data.error}`, 'error');
                }
                
            } catch (error) {
                console.error('API调用错误:', error);
                showToast('❌ 网络错误，请检查连接', 'error');
            } finally {
                // 恢复按钮状态
                generateBtn.innerHTML = originalText;
                generateBtn.disabled = false;
            }
        });
    }
    
    // 查看页面的查看按钮事件
    const viewSecretBtn = document.getElementById('viewSecretBtn');
    if (viewSecretBtn) {
        viewSecretBtn.addEventListener('click', async function() {
            const passcode = document.getElementById('viewPasscode').value;
            
            if (!passcode) {
                showToast('请输入访问密码', 'warning');
                return;
            }
            
            // 显示加载状态
            const originalText = viewSecretBtn.innerHTML;
            viewSecretBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 验证中...';
            viewSecretBtn.disabled = true;
            
            try {
                // 从URL获取secret_id
                const pathParts = window.location.pathname.split('/');
                let secretId = pathParts[pathParts.length - 1];
                
                // 如果是在/view页面，需要先创建测试数据
                if (!secretId || secretId === 'view') {
                    // 这是一个演示模式
                    const sampleSecrets = [
                        "WiFi密码: HomeNetwork@2024",
                        "银行卡密码: 668899",
                        "服务器IP: 192.168.1.100",
                        "数据库密码: Admin@123",
                        "API密钥: sk_live_51H9x...",
                        "SSH私钥: -----BEGIN RSA PRIVATE KEY-----\nMIIEpAIBAAKCAQE...",
                        "双重验证恢复码: 1234 5678 9012 3456"
                    ];
                    
                    const randomSecret = sampleSecrets[Math.floor(Math.random() * sampleSecrets.length)];
                    
                    // 显示秘密
                    document.getElementById('secretContent').textContent = randomSecret;
                    document.getElementById('secretSection').style.display = 'block';
                    
                    // 开始倒计时
                    startCountdown(10);
                    
                    showToast('🔓 演示模式：秘密已解锁，请立即查看！', 'success');
                    return;
                }
                
                // 调用真实API获取秘密
                const response = await fetch(`/api/secret/${secretId}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        passcode: passcode
                    })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    // 显示秘密
                    document.getElementById('secretContent').textContent = data.secret;
                    document.getElementById('secretSection').style.display = 'block';
                    
                    // 开始倒计时
                    startCountdown(10);
                    
                    showToast('🔓 秘密已解锁，请立即查看！', 'success');
                    
                    // 隐藏密码输入区域
                    document.getElementById('viewPasscode').parentElement.style.display = 'none';
                    viewSecretBtn.style.display = 'none';
                    
                } else {
                    showToast(`❌ 验证失败: ${data.error}`, 'error');
                }
                
            } catch (error) {
                console.error('API调用错误:', error);
                showToast('❌ 网络错误，请检查连接', 'error');
            } finally {
                // 恢复按钮状态
                viewSecretBtn.innerHTML = originalText;
                viewSecretBtn.disabled = false;
            }
        });
    }
    
    // 密码强度检查
    const passcodeInput = document.getElementById('passcode');
    if (passcodeInput) {
        passcodeInput.addEventListener('input', function() {
            updatePasswordStrength(this.value);
        });
    }
});

// 密码强度检查
function checkPasswordStrength(password) {
    if (!password) return 0;
    
    let strength = 0;
    
    // 长度检查
    if (password.length >= 6) strength += 1;
    if (password.length >= 10) strength += 1;
    
    // 包含小写字母
    if (/[a-z]/.test(password)) strength += 1;
    
    // 包含大写字母
    if (/[A-Z]/.test(password)) strength += 1;
    
    // 包含数字
    if (/[0-9]/.test(password)) strength += 1;
    
    // 包含特殊字符
    if (/[^a-zA-Z0-9]/.test(password)) strength += 1;
    
    return Math.min(strength, 6);
}

// 显示密码强度
function updatePasswordStrength(password) {
    const strengthBar = document.getElementById('passwordStrength');
    const strengthText = document.getElementById('passwordStrengthText');
    
    if (!strengthBar || !strengthText) return;
    
    const strength = checkPasswordStrength(password);
    const colors = ['danger', 'danger', 'warning', 'warning', 'info', 'success', 'success'];
    const texts = ['非常弱', '弱', '一般', '中等', '良好', '强', '非常强'];
    
    const width = Math.min(100, (strength / 6) * 100);
    strengthBar.style.width = `${width}%`;
    strengthBar.className = `progress-bar bg-${colors[strength]}`;
    strengthText.textContent = `密码强度: ${texts[strength]}`;
    strengthText.className = `form-text text-${colors[strength]}`;
}

// 倒计时函数
function startCountdown(seconds) {
    const countdownElement = document.getElementById('countdown');
    const secretSection = document.getElementById('secretSection');
    
    if (!countdownElement || !secretSection) return;
    
    let timeLeft = seconds;
    
    const countdownInterval = setInterval(() => {
        countdownElement.textContent = timeLeft;
        timeLeft--;
        
        if (timeLeft < 0) {
            clearInterval(countdownInterval);
            secretSection.innerHTML = `
                <div class="card-body text-center py-5">
                    <i class="fas fa-fire fa-5x text-danger mb-3"></i>
                    <h3 class="text-danger">秘密已销毁</h3>
                    <p class="text-muted">此秘密已被永久删除，无法再次查看。</p>
                    <a href="/" class="btn btn-primary">
                        <i class="fas fa-home"></i> 返回首页
                    </a>
                </div>
            `;
            showToast('🔥 秘密已被销毁', 'warning');
        }
    }, 1000);
}

// 页面卸载前的警告
window.addEventListener('beforeunload', function(e) {
    const secretSection = document.getElementById('secretSection');
    if (secretSection && secretSection.style.display !== 'none') {
        e.preventDefault();
        e.returnValue = '您正在查看的秘密可能会丢失。确定要离开吗？';
    }
});