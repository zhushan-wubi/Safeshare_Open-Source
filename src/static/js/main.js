
let currentEmotion = "calm";
const quotes = [
    "今天也在被温柔地接住 🌿",
    "你不是一个人 🤍",
    "慢一点也没关系 ✨"
];

document.getElementById("welcomeText").innerText =
    quotes[Math.floor(Math.random() * quotes.length)];


function generateAIReply(emotion, text) {
    const replies = {
        happy: ["听到你的开心，我也忍不住笑了 🌼"],
        sad: ["没关系的，你已经很努力了 🤍"],
        angry: ["你的情绪是有理由的 🔥"],
        anxious: ["慢慢来就好 🌿"],
        calm: ["这一刻，就很好 ✨"]
    };

    const list = replies[emotion] || replies["calm"];
    return list[Math.floor(Math.random() * list.length)];
}


function copyText(text) {
    navigator.clipboard.writeText(text)
        .then(() => alert("✅ 已复制！直接打开链接即可查看"))
        .catch(() => alert("❌ 复制失败"));
}

function triggerTypingEffect(element) {
    element.style.animation = 'none';
    element.offsetHeight; 
    element.style.animation = null;
}


function initTypingCSS() {
    const style = document.createElement('style');
    style.textContent = `
        @keyframes typing {
            from { width: 0 }
            to { width: 100% }
        }
        @keyframes blink {
            50% { border-color: transparent }
        }
        .ai-typing {
            overflow: hidden;
            white-space: nowrap;
            border-right: 2px solid #aaa;
            width: 0;
            animation: typing 2s steps(30, end) forwards,
                       blink 0.8s infinite;
        }
        /* 过期模式按钮样式 */
        .expire-mode-btn {
            padding: 8px 20px;
            border: none;
            border-radius: 4px;
            margin: 0 5px;
            cursor: pointer;
            background: #f0f0f0;
        }
        .expire-mode-btn.active {
            background: #e6a8a8;
            color: white;
        }
    `;
    document.head.appendChild(style);
}

document.addEventListener("DOMContentLoaded", () => {
   
    initTypingCSS();

    
    document.querySelectorAll(".emotion-btn").forEach(btn => {
        btn.addEventListener("click", function () {
            currentEmotion = this.dataset.emotion;

            document.querySelectorAll(".emotion-btn")
                .forEach(b => b.classList.remove("active"));

            this.classList.add("active");

            document.body.setAttribute("data-theme", currentEmotion);
        });
    });


    const textarea = document.getElementById("secretText");
    const count = document.getElementById("charCount");

    if (textarea && count) {
        textarea.addEventListener("input", () => {
            count.textContent = textarea.value.length;
        });
    }


    const toggleBtn = document.getElementById("togglePassword");
    if (toggleBtn) {
        toggleBtn.addEventListener("click", () => {
            const input = document.getElementById("passcode");
            input.type = input.type === "password" ? "text" : "password";
        });
    }


    const generateBtn = document.getElementById("generateBtn");

    if (generateBtn) {
        generateBtn.addEventListener("click", () => {

            const secret = document.getElementById("secretText").value.trim();
            const pass = document.getElementById("passcode").value;
            const confirm = document.getElementById("confirmPasscode").value;


            let expireMode = 'burn_after_read'; 
            const selectedExpiry = document.querySelector('input[name="expiry"]:checked');
            if (selectedExpiry) {
                expireMode = selectedExpiry.dataset.mode || 'burn_after_read';
            }

            if (!secret) {
                alert("请输入内容");
                return;
            }

            if (pass.length < 4 || pass !== confirm) {
                alert("密码不符合要求");
                return;
            }

            fetch('/api/secret', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    secret: secret,
                    passcode: pass,
                    type: "normal",
                    expire_mode: expireMode 
                })
            })
            .then(res => res.json())
            .then(data => {

                if (!data.success) {
                    alert("生成失败");
                    return;
                }

                const id = data.id;
                const link = `${window.location.origin}/view/${id}`;

                showResult(secret, link, expireMode);

            })
            .catch(err => {
                console.error(err);
                alert("生成失败");
            });
        });
    }

    const saveCapsuleBtn = document.getElementById("saveCapsuleBtn");
    if (saveCapsuleBtn) {
        saveCapsuleBtn.addEventListener("click", () => {
            const content = document.getElementById("capsuleSecret").value.trim();
            const pass = document.getElementById("capsulePass").value || "";
            const date = document.getElementById("capsuleDate").value;

            let expireMode = 'burn_after_read';
            const selectedExpiry = document.querySelector('input[name="expiry"]:checked');
            if (selectedExpiry) {
                expireMode = selectedExpiry.dataset.mode || 'burn_after_read';
            }

            if (!content) {
                alert("请输入胶囊内容");
                return;
            }
            if (!date) {
                alert("请选择解锁日期");
                return;
            }

            fetch('/api/secret', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    secret: content,
                    passcode: pass,
                    type: "time",
                    unlock_time: new Date(date).getTime(),
                    expire_mode: expireMode // 传递过期模式给后端
                })
            })
            .then(res => res.json())
            .then(data => {
                if (!data.success) {
                    alert("时光胶囊创建失败");
                    return;
                }
                const id = data.id;
                const link = `${window.location.origin}/view/${id}`;
                showResult(content, link, expireMode);
                

                const modal = bootstrap.Modal.getInstance(document.getElementById("timeCapsuleModal"));
                if (modal) modal.hide();
            })
            .catch(err => {
                console.error(err);
                alert("时光胶囊创建失败");
            });
        });
    }


    const saveDoubleSecretBtn = document.getElementById("saveDoubleSecretBtn");
    if (saveDoubleSecretBtn) {
        saveDoubleSecretBtn.addEventListener("click", () => {
            const content = document.getElementById("doubleSecret").value.trim();
            const passA = document.getElementById("doublePassA").value;
            const passB = document.getElementById("doublePassB").value;

            let expireMode = 'burn_after_read';
            const selectedExpiry = document.querySelector('input[name="expiry"]:checked');
            if (selectedExpiry) {
                expireMode = selectedExpiry.dataset.mode || 'burn_after_read';
            }

            if (!content) {
                alert("请输入秘密内容");
                return;
            }
            if (!passA || !passB) {
                alert("请设置两组密码");
                return;
            }

            const doublePass = passA + "|" + passB; 
            const showPass = passA + passB; 

            fetch('/api/secret', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    secret: content,
                    passcode: doublePass,
                    type: "double",
                    expire_mode: expireMode 
                })
            })
            .then(res => res.json())
            .then(data => {
                if (!data.success) {
                    alert("双人秘密创建失败");
                    return;
                }
                const id = data.id;
                const link = `${window.location.origin}/view/${id}`;
                

                const expireText = expireMode === 'burn_after_read' ? '阅后即焚' : 
                                   expireMode === '24h' ? '24小时有效' : '7天有效';
                const resultBox = document.createElement("div");
                resultBox.className = "card p-4 mt-4";
                resultBox.innerHTML = `
                    <h5>✅ 双人秘密已生成（${expireText}）</h5>
                    <div class="mb-2">
                        <input class="form-control" value="${link}" readonly>
                    </div>
                    <div class="mb-2">
                        <input class="form-control" value="${showPass}" readonly placeholder="访问密码（纯拼接格式）">
                    </div>
                    <div class="d-flex gap-2 mb-2">
                        <button class="btn btn-primary copy-btn">复制链接</button>
                        <button class="btn btn-secondary copy-pass-btn">复制密码</button>
                        <button class="btn btn-secondary close-btn">关闭</button>
                    </div>
                    <p class="text-muted small">
                        🔒 密码为两组密码拼接（无空格/加号），${expireText}
                    </p>
                    <div class="p-3 rounded ai-typing typing-text" style="background: rgba(255,255,255,0.6)">
                        🤖 双人秘密已封存，等待相遇～
                    </div>
                `;
                document.querySelector(".container").appendChild(resultBox);
                resultBox.querySelector(".copy-btn").onclick = () => copyText(link);
                resultBox.querySelector(".copy-pass-btn").onclick = () => copyText(showPass);
                resultBox.querySelector(".close-btn").onclick = () => resultBox.remove();
                

                const typingBox = resultBox.querySelector(".typing-text");
                triggerTypingEffect(typingBox);
                

                document.getElementById("doubleSecret").value = "";
                document.getElementById("doublePassA").value = "";
                document.getElementById("doublePassB").value = "";
                const modal = bootstrap.Modal.getInstance(document.getElementById("doubleSecretModal"));
                if (modal) modal.hide();
            })
            .catch(err => {
                console.error(err);
                alert("双人秘密创建失败");
            });
        });
    }


    const treeBtn = document.getElementById("saveTreeWhisperBtn");

    if (treeBtn) {
        treeBtn.addEventListener("click", () => {

            const content = document.getElementById("treeWhisper").value.trim();

            if (!content) {
                alert("请输入内容");
                return;
            }

            fetch('/api/secret', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    secret: content,
                    type: "tree"
                })
            })
            .then(res => res.json())
            .then(() => {
                return fetch('/api/ai-reply', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        content: content,
                        emotion: currentEmotion
                    })
                });
            })
            .then(res => res.json())
            .then(data => {

                addTreeHole(content, data.reply);

                alert("🌳 已被温柔接住了");

                document.getElementById("treeWhisper").value = "";

                try {
                    const modal = bootstrap.Modal.getInstance(
                        document.getElementById("emotionTreeModal")
                    );
                    if (modal) modal.hide();
                } catch (e) {}

            })
            .catch(err => {
                console.error(err);

                const fakeReply = generateAIReply(currentEmotion, content);
                addTreeHole(content, fakeReply);

                alert("⚠️ AI连接失败，已使用本地回复");
            });
        });
    }


    fetch('/api/treeholes')
        .then(res => res.json())
        .then(list => {
            list.reverse().forEach(item => {
                addTreeHole(item.content, "🌱 一段被留下的心声", "calm");
            });
        });

});



function addTreeHole(content, aiReply, emotion = currentEmotion) {

    const list = document.getElementById("publicTreeholeList");
    if (!list) return;

    const div = document.createElement("div");
    div.className = "col-md-6";

    div.innerHTML = `
        <div class="card p-3 mb-3">
            <p>${content}</p>
            <p class="small text-muted">匿名用户 · 刚刚 · ${emotion}</p>

            <div class="mt-3 p-2 rounded ai-typing typing-text" style="background: rgba(255,255,255,0.6)">
                🤖 ${aiReply}
            </div>
        </div>
    `;

    list.prepend(div);
    

    const typingBox = div.querySelector(".typing-text");
    triggerTypingEffect(typingBox);
}


function showResult(secret, link, expireMode = 'burn_after_read') {

    const aiReply = generateAIReply(currentEmotion, secret);

    const expireText = expireMode === 'burn_after_read' ? '阅后即焚' : 
                       expireMode === '24h' ? '24小时有效' : '7天有效';

    const box = document.createElement("div");
    box.className = "card p-4 mt-4";

    box.innerHTML = `
        <h5>✅ 分享已生成（${expireText}）</h5>

        <div class="mb-2">
            <input class="form-control" value="${link}" readonly>
        </div>

        <div class="d-flex gap-2 mb-2">
            <button class="btn btn-primary copy-btn">复制链接</button>
            <button class="btn btn-secondary close-btn">关闭</button>
        </div>

        <p class="text-muted small">
            🔒 打开后需要输入密码查看，${expireText}
        </p>

        <div class="p-3 rounded ai-typing typing-text" style="background: rgba(255,255,255,0.6)">
            🤖 ${aiReply}
        </div>
    `;

    document.querySelector(".container").appendChild(box);

    box.querySelector(".copy-btn").onclick = () => copyText(link);
    box.querySelector(".close-btn").onclick = () => box.remove();


    const typingBox = box.querySelector(".typing-text");
    triggerTypingEffect(typingBox);


    if (document.getElementById("secretText")) document.getElementById("secretText").value = "";
    if (document.getElementById("passcode")) document.getElementById("passcode").value = "";
    if (document.getElementById("confirmPasscode")) document.getElementById("confirmPasscode").value = "";
    if (document.getElementById("capsuleSecret")) document.getElementById("capsuleSecret").value = "";
    if (document.getElementById("capsulePass")) document.getElementById("capsulePass").value = "";
    if (document.getElementById("capsuleDate")) document.getElementById("capsuleDate").value = "";
}
