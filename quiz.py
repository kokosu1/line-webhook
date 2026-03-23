# quiz.py
import random

QUIZ_LIST = [
    # 漢字読みクイズ
    {"type": "reading", "question": "「日本語」の読み方は？", "answer": "にほんご"},
    {"type": "reading", "question": "「学校」の読み方は？", "answer": "がっこう"},
    {"type": "reading", "question": "「食べ物」の読み方は？", "answer": "たべもの"},
    {"type": "reading", "question": "「電車」の読み方は？", "answer": "でんしゃ"},
    {"type": "reading", "question": "「友達」の読み方は？", "answer": "ともだち"},
    {"type": "reading", "question": "「仕事」の読み方は？", "answer": "しごと"},
    {"type": "reading", "question": "「時間」の読み方は？", "answer": "じかん"},
    {"type": "reading", "question": "「水」の読み方は？", "answer": "みず"},
    # 穴埋めクイズ
    {"type": "fill", "question": "「おはよう＿＿＿＿」朝の挨拶を完成させよう！", "answer": "ございます"},
    {"type": "fill", "question": "「___にちは」昼の挨拶は？（ひらがな3文字）", "answer": "こん"},
    {"type": "fill", "question": "「ありがとう＿＿＿＿＿」丁寧な感謝の言葉は？", "answer": "ございます"},
    {"type": "fill", "question": "「私は学生___」（〜です の「です」を入れよう）", "answer": "です"},
    {"type": "fill", "question": "「電車に___ります」（乗る）", "answer": "の"},
    {"type": "fill", "question": "「日本語を___強します」（勉強）", "answer": "べん"},
]

# 進行中のクイズを管理
user_quiz = {}

def get_random_quiz():
    return random.choice(QUIZ_LIST)

def start_quiz(user_id):
    quiz = get_random_quiz()
    user_quiz[user_id] = quiz
    return f"🇯🇵 日本語クイズ！\n\n{quiz['question']}\n\n答えをひらがなで送ってね！\n（やめる場合は「やめる」）"

def answer_quiz(user_id, text):
    if text == "やめる":
        del user_quiz[user_id]
        return "クイズを終了したよ！またね👋"
    
    correct = user_quiz[user_id]["answer"]
    if text == correct:
        next_quiz = get_random_quiz()
        user_quiz[user_id] = next_quiz
        return f"✅ 正解！すごい！\n\n次の問題！\n{next_quiz['question']}\n\n答えをひらがなで送ってね！"
    else:
        return f"❌ 惜しい！もう一度考えてみて！\n\n{user_quiz[user_id]['question']}"

def is_in_quiz(user_id):
    return user_id in user_quiz
