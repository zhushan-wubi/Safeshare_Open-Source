// SafeShare 秘密花园 - 完善版
document.addEventListener('DOMContentLoaded', function() {
    console.log('🌿 莫奈秘密花园 加载完成');
    initPasswordStrength();
    initCopyFunction();
    initCharacterCount();
    initTogglePassword();
});

// ========== 1. 复制到剪贴板（现代API，兼容所有浏览器） ==========
function copyToClipboard(elementId) {
    const element = document.getElementById(elementId);
    if (!element) return;

    navigator.clipboard.writeText(element.value)
        .then(() => showToast('✅ 已复制到剪贴板', 'success'))
        .catch(() => showToast('❌ 复制失败，请手动复制', 'error'));
}

// ========== 2. 自定义Toast提示（贴合油画风格） ==========
function showToast(message, type = 'info') {
    // 清除已有Toast
    const existing = document.querySelector('.custom-toast');
    if (existing) existing.remove();

    const toast = document.createElement('div');
    toast.className = `custom-toast toast align-items-center text-bg-${type} border-0 position-fixed bottom-0 end-0 m-3 p-3`;
    toast.setAttribute('role', 'alert');
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">${message}</div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    document.body.appendChild(toast);
    const bsToast = new bootstrap.Toast(toast, { delay: 3000 });
    bsToast.show();
}

// ========== 3. 密码强度检测 ==========
function initPasswordStrength() {
    const passInput = document.getElementById('passcode');
    if (!passInput) return;

    passInput.addEventListener('input', function() {
        const strength = checkPasswordStrength(this.value);
        updateStrengthUI(strength);
    });
}

function checkPasswordStrength(password) {
    if (!password) return 0;
    let score = 0;
    if (password.length >= 6) score++;
    if (password.length >= 10) score++;
    if (/[a-z]/.test(password)) score++;
    if (/[A-Z]/.test(password)) score++;
    if (/[0-9]/.test(password)) score++;
    if (/[^a-zA-Z0-9]/.test(password)) score++;
    return Math.min(score, 6);
}

function updateStrengthUI(strength) {
    const bar = document.getElementById('passwordStrength');
    const text = document.getElementById('passwordStrengthText');
    if (!bar || !text) return;

    const config = [
        { cls: 'bg-danger', text: '非常弱' },
        { cls: 'bg-danger', text: '弱' },
        { cls: 'bg-warning', text: '一般' },
        { cls: 'bg-warning', text: '中等' },
        { cls: 'bg-info', text: '良好' },
        { cls: 'bg-success', text: '强' },
        { cls: 'bg-success', text: '非常强' }
    ];
    const width = (strength / 6) * 100;
    bar.style.width = `${width}%`;
    bar.className = `progress-bar ${config[strength].cls}`;
    text.textContent = `密码强度: ${config[strength].text}`;
    text.className = `form-text ${config[strength].cls.replace('bg-', 'text-')}`;
}

// ========== 4. 输入框字符计数 ==========
function initCharacterCount() {
    const textarea = document.getElementById('secretText');
    const count = document.getElementById('charCount');
    if (!textarea || !count) return;
    textarea.addEventListener('input', () => {
        count.textContent = textarea.value.length;
        textarea.value.length > 1800 && showToast('⚠️ 接近最大字符限制', 'warning');
    });
}

// ========== 5. 密码显示/隐藏 ==========
function initTogglePassword() {
    const btn = document.getElementById('togglePassword');
    const input = document.getElementById('passcode');
    if (!btn || !input) return;
    btn.addEventListener('click', function() {
        const type = input.type === 'password' ? 'text' : 'password';
        input.type = type;
        this.innerHTML = type === 'password' ? '<i class="fas fa-eye"></i>' : '<i class="fas fa-eye-slash"></i>';
    });
}

// ========== 6. 倒计时销毁逻辑 ==========
function startCountdown(seconds, element) {
    let time = seconds;
    const timer = setInterval(() => {
        element.textContent = time;
        time--;
        if (time < 0) {
            clearInterval(timer);
            element.closest('.card').innerHTML = `
                <div class="card-body text-center py-5">
                    <i class="fas fa-fire fa-4x text-danger mb-3"></i>
                    <h3>秘密已销毁</h3>
                    <p class="text-muted">已永久删除，无法恢复</p>
                    <a href="/" class="btn btn-primary mt-2">返回首页</a>
                </div>
            `;
            showToast('🔥 秘密已自动销毁', 'warning');
        }
    }, 1000);
}

// ========== 7. 通用ID生成 ==========
function generateId() {
    return Date.now().toString(36) + Math.random().toString(36).substr(2, 8);
}

// 离开页面警告
window.addEventListener('beforeunload', (e) => {
    const secretBox = document.getElementById('secretDisplay');
    if (secretBox && secretBox.style.display === 'block') {
        e.returnValue = '秘密正在查看，离开将销毁！';
    }
});