// 🌈 当前情绪
let currentEmotion = "calm";

// 🧠 AI温柔回复系统（备用）
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

// 📋 复制
function copyText(text) {
    navigator.clipboard.writeText(text)
        .then(() => alert("✅ 已复制！"))
        .catch(() => alert("❌ 复制失败"));
}

document.addEventListener("DOMContentLoaded", () => {

    // 🌈 情绪选择
    document.querySelectorAll(".emotion-btn").forEach(btn => {
        btn.addEventListener("click", function () {
            currentEmotion = this.dataset.emotion;

            document.querySelectorAll(".emotion-btn")
                .forEach(b => b.classList.remove("active"));

            this.classList.add("active");

            document.body.setAttribute("data-theme", currentEmotion);
        });
    });

    // ✍️ 字数统计
    const textarea = document.getElementById("secretText");
    const count = document.getElementById("charCount");

    if (textarea && count) {
        textarea.addEventListener("input", () => {
            count.textContent = textarea.value.length;
        });
    }

    // 👁️ 密码显示
    const toggleBtn = document.getElementById("togglePassword");
    if (toggleBtn) {
        toggleBtn.addEventListener("click", () => {
            const input = document.getElementById("passcode");
            input.type = input.type === "password" ? "text" : "password";
        });
    }

    // 🚀 生成分享链接（✅ 已修复）
    const generateBtn = document.getElementById("generateBtn");

    if (generateBtn) {
        generateBtn.addEventListener("click", () => {

            const secret = document.getElementById("secretText").value.trim();
            const pass = document.getElementById("passcode").value;
            const confirm = document.getElementById("confirmPasscode").value;

            if (!secret) {
                alert("请输入内容");
                return;
            }

            if (pass.length < 4 || pass !== confirm) {
                alert("密码不符合要求");
                return;
            }

            // ✅ 调用后端生成真实ID
            fetch('/api/secret', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    secret: secret,
                    passcode: pass,
                    type: "normal"
                })
            })
            .then(res => res.json())
            .then(data => {

                if (!data.success) {
                    alert("生成失败");
                    return;
                }

                const id = data.id;

                // ✅ 正确链接格式（关键修复点）
                const link = window.location.origin + "/view/" + id;

                showResult(secret, link);

            })
            .catch(err => {
                console.error(err);
                alert("生成失败");
            });
        });
    }

    // 🌳 树洞功能
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

    // 🌱 加载历史树洞（优化：不覆盖情绪）
    fetch('/api/treeholes')
        .then(res => res.json())
        .then(list => {
            list.reverse().forEach(item => {
                addTreeHole(item.content, "🌱 一段被留下的心声", "calm");
            });
        });

});


// 🌳 渲染树洞（✅ 修复情绪混乱bug）
function addTreeHole(content, aiReply, emotion = currentEmotion) {

    const list = document.getElementById("publicTreeholeList");
    if (!list) return;

    const div = document.createElement("div");
    div.className = "col-md-6";

    div.innerHTML = `
        <div class="card p-3 mb-3">
            <p>${content}</p>
            <p class="small text-muted">匿名用户 · 刚刚 · ${emotion}</p>

            <div class="mt-3 p-2 rounded ai-typing" style="background: rgba(255,255,255,0.6)">
                🤖 ${aiReply}
            </div>
        </div>
    `;

    list.prepend(div);
}


// 🌸 分享结果
function showResult(secret, link) {

    const aiReply = generateAIReply(currentEmotion, secret);

    const box = document.createElement("div");
    box.className = "card p-4 mt-4";

    box.innerHTML = `
        <h5>✅ 分享已生成</h5>

        <div class="mb-2">
            <input class="form-control" value="${link}" readonly>
        </div>

        <div class="d-flex gap-2 mb-2">
            <button class="btn btn-primary copy-btn">复制链接</button>
            <button class="btn btn-secondary close-btn">关闭</button>
        </div>

        <p class="text-muted small">
            🔒 打开后需要输入密码查看，且仅可查看一次
        </p>

        <div class="p-3 rounded ai-typing" style="background: rgba(255,255,255,0.6)">
            🤖 ${aiReply}
        </div>
    `;

    document.querySelector(".container").appendChild(box);

    box.querySelector(".copy-btn").onclick = () => copyText(link);
    box.querySelector(".close-btn").onclick = () => box.remove();

    document.getElementById("secretText").value = "";
    document.getElementById("passcode").value = "";
    document.getElementById("confirmPasscode").value = "";
}