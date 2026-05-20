import random

reply_library = {
    "sad": [
        "🌧️ 有些夜晚会很长，但黎明从不会失约。",
        "🍂 情绪像落叶一样堆积时，也别忘了风终会吹来。",
        "🌙 世界偶尔灰暗，但你依然值得被温柔对待。",
        "🌱 难过的时候，就把自己交给时间慢慢照顾。",
    ],

    "happy": [
        "🌸 快乐是花园里短暂却明亮的花。",
        "☀️ 有些瞬间会照亮很久以后的生活。",
        "🌿 愿你的开心，能在未来某天再次救你一次。",
    ],

    "angry": [
        "🔥 风暴会经过，但别让自己困在雷雨里。",
        "🍃 有些情绪不必压抑，只是不必永远停留。",
        "🌊 等潮水退去，很多事情都会慢慢平静。",
    ],

    "lonely": [
        "🌌 孤独不是没人同行，而是还没找到共鸣。",
        "🕯️ 有时候沉默，也是另一种被理解。",
        "🌙 即使无人回应，花园也会记住你的声音。",
    ],

    "default": [
        "🌿 谢谢你愿意把心事留在这里。",
        "🌸 每一句秘密，都值得被认真收藏。",
        "🍀 世界很吵，但这里愿意安静听你说话。",
        "💫 有些情绪无法解释，但依然值得存在。",
    ]
}


def detect_emotion(text):
    text = text.lower()

    sad_words = ["难过", "伤心", "崩溃", "痛苦", "哭"]
    happy_words = ["开心", "幸福", "快乐", "兴奋"]
    angry_words = ["生气", "愤怒", "烦", "讨厌"]
    lonely_words = ["孤独", "寂寞", "没人", "一个人"]

    for word in sad_words:
        if word in text:
            return "sad"

    for word in happy_words:
        if word in text:
            return "happy"

    for word in angry_words:
        if word in text:
            return "angry"

    for word in lonely_words:
        if word in text:
            return "lonely"

    return "default"


def generate_reply(text):
    emotion = detect_emotion(text)
    return random.choice(reply_library[emotion])
