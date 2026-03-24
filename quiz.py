import random

# ==================== クイズデータ ====================

QUIZ_DATA = {
“N5”: [
# 漢字読み
{“type”: “reading”, “question”: “「日本語」の読み方は？”, “answer”: “にほんご”},
{“type”: “reading”, “question”: “「学校」の読み方は？”, “answer”: “がっこう”},
{“type”: “reading”, “question”: “「食べ物」の読み方は？”, “answer”: “たべもの”},
{“type”: “reading”, “question”: “「電車」の読み方は？”, “answer”: “でんしゃ”},
{“type”: “reading”, “question”: “「友達」の読み方は？”, “answer”: “ともだち”},
{“type”: “reading”, “question”: “「水」の読み方は？”, “answer”: “みず”},
{“type”: “reading”, “question”: “「山」の読み方は？”, “answer”: “やま”},
{“type”: “reading”, “question”: “「川」の読み方は？”, “answer”: “かわ”},
# 語彙（意味）
{“type”: “vocab”, “question”: “「おおきい」の意味は？（漢字で書いてね）”, “answer”: “大きい”},
{“type”: “vocab”, “question”: “「たかい」の意味は？（漢字で書いてね）”, “answer”: “高い”},
{“type”: “vocab”, “question”: “「やすい」の意味は？（漢字で書いてね）”, “answer”: “安い”},
{“type”: “vocab”, “question”: “「あたらしい」の意味は？（漢字で書いてね）”, “answer”: “新しい”},
# 穴埋め
{“type”: “fill”, “question”: “「おはよう＿＿＿＿」朝の挨拶を完成させよう！”, “answer”: “ございます”},
{“type”: “fill”, “question”: “「***にちは」昼の挨拶は？（ひらがな3文字）”, “answer”: “こん”},
{“type”: “fill”, “question”: “「私は学生***」（〜です の「です」を入れよう）”, “answer”: “です”},
{“type”: “fill”, “question”: “「電車に___ります」（乗る）”, “answer”: “の”},
# 反対語
{“type”: “antonym”, “question”: “「大きい」の反対語は？”, “answer”: “小さい”},
{“type”: “antonym”, “question”: “「高い」の反対語は？”, “answer”: “低い”},
{“type”: “antonym”, “question”: “「新しい」の反対語は？”, “answer”: “古い”},
{“type”: “antonym”, “question”: “「長い」の反対語は？”, “answer”: “短い”},
],
“N4”: [
# 漢字読み
{“type”: “reading”, “question”: “「仕事」の読み方は？”, “answer”: “しごと”},
{“type”: “reading”, “question”: “「時間」の読み方は？”, “answer”: “じかん”},
{“type”: “reading”, “question”: “「旅行」の読み方は？”, “answer”: “りょこう”},
{“type”: “reading”, “question”: “「練習」の読み方は？”, “answer”: “れんしゅう”},
{“type”: “reading”, “question”: “「説明」の読み方は？”, “answer”: “せつめい”},
{“type”: “reading”, “question”: “「運動」の読み方は？”, “answer”: “うんどう”},
# 語彙
{“type”: “vocab”, “question”: “「かんたん」を漢字で書くと？”, “answer”: “簡単”},
{“type”: “vocab”, “question”: “「べんり」を漢字で書くと？”, “answer”: “便利”},
{“type”: “vocab”, “question”: “「しんぱい」を漢字で書くと？”, “answer”: “心配”},
{“type”: “vocab”, “question”: “「きけん」を漢字で書くと？”, “answer”: “危険”},
# 穴埋め（文法）
{“type”: “fill”, “question”: “「雨が降り___、出かけられない」（〜なので）”, “answer”: “そうで”},
{“type”: “fill”, “question”: “「日本語を勉強___います」（〜して）”, “answer”: “して”},
{“type”: “fill”, “question”: “「映画を見___行きませんか」（〜に）”, “answer”: “に”},
{“type”: “fill”, “question”: “「この本は難し___です」（〜すぎる）”, “answer”: “すぎる”},
# 反対語
{“type”: “antonym”, “question”: “「安全」の反対語は？”, “answer”: “危険”},
{“type”: “antonym”, “question”: “「簡単」の反対語は？”, “answer”: “難しい”},
{“type”: “antonym”, “question”: “「便利」の反対語は？”, “answer”: “不便”},
# 敬語変換
{“type”: “keigo”, “question”: “「食べる」の丁寧語は？”, “answer”: “いただく”},
{“type”: “keigo”, “question”: “「言う」の謙譲語は？”, “answer”: “申す”},
{“type”: “keigo”, “question”: “「いる」の尊敬語は？”, “answer”: “いらっしゃる”},
],
“N3”: [
# 漢字読み
{“type”: “reading”, “question”: “「経験」の読み方は？”, “answer”: “けいけん”},
{“type”: “reading”, “question”: “「政治」の読み方は？”, “answer”: “せいじ”},
{“type”: “reading”, “question”: “「環境」の読み方は？”, “answer”: “かんきょう”},
{“type”: “reading”, “question”: “「機会」の読み方は？”, “answer”: “きかい”},
{“type”: “reading”, “question”: “「判断」の読み方は？”, “answer”: “はんだん”},
{“type”: “reading”, “question”: “「影響」の読み方は？”, “answer”: “えいきょう”},
# 語彙
{“type”: “vocab”, “question”: “「あいまい」を漢字で書くと？”, “answer”: “曖昧”},
{“type”: “vocab”, “question”: “「かくじつ」を漢字で書くと？”, “answer”: “確実”},
{“type”: “vocab”, “question”: “「じょうきょう」を漢字で書くと？”, “answer”: “状況”},
# 穴埋め（文法）
{“type”: “fill”, “question”: “「試験に合格する___、毎日勉強している」（〜ために）”, “answer”: “ために”},
{“type”: “fill”, “question”: “「彼は来る___来なかった」（〜はずなのに）”, “answer”: “はずなのに”},
{“type”: “fill”, “question”: “「困った___は相談してください」（〜とき）”, “answer”: “とき”},
# 反対語
{“type”: “antonym”, “question”: “「積極的」の反対語は？”, “answer”: “消極的”},
{“type”: “antonym”, “question”: “「具体的」の反対語は？”, “answer”: “抽象的”},
{“type”: “antonym”, “question”: “「楽観的」の反対語は？”, “answer”: “悲観的”},
# 敬語
{“type”: “keigo”, “question”: “「もらう」の謙譲語は？”, “answer”: “いただく”},
{“type”: “keigo”, “question”: “「見る」の尊敬語は？”, “answer”: “ご覧になる”},
{“type”: “keigo”, “question”: “「する」の謙譲語は？”, “answer”: “いたす”},
],
“N2”: [
# 漢字読み
{“type”: “reading”, “question”: “「懸念」の読み方は？”, “answer”: “けねん”},
{“type”: “reading”, “question”: “「概念」の読み方は？”, “answer”: “がいねん”},
{“type”: “reading”, “question”: “「恩恵」の読み方は？”, “answer”: “おんけい”},
{“type”: “reading”, “question”: “「矛盾」の読み方は？”, “answer”: “むじゅん”},
{“type”: “reading”, “question”: “「妥協」の読み方は？”, “answer”: “だきょう”},
{“type”: “reading”, “question”: “「貢献」の読み方は？”, “answer”: “こうけん”},
# 語彙
{“type”: “vocab”, “question”: “「ひっし」を漢字で書くと？”, “answer”: “必死”},
{“type”: “vocab”, “question”: “「ふくざつ」を漢字で書くと？”, “answer”: “複雑”},
{“type”: “vocab”, “question”: “「こうりつ」を漢字で書くと？”, “answer”: “効率”},
{“type”: “vocab”, “question”: “「ぎむ」を漢字で書くと？”, “answer”: “義務”},
# 穴埋め（文法）
{“type”: “fill”, “question”: “「彼___失敗するとは思わなかった」（〜に限って）”, “answer”: “に限って”},
{“type”: “fill”, “question”: “「努力した___、結果が出た」（〜かいがあって）”, “answer”: “かいがあって”},
{“type”: “fill”, “question”: “「どう考え___理解できない」（〜ても）”, “answer”: “ても”},
# 反対語
{“type”: “antonym”, “question”: “「抽象的」の反対語は？”, “answer”: “具体的”},
{“type”: “antonym”, “question”: “「主観的」の反対語は？”, “answer”: “客観的”},
# 敬語
{“type”: “keigo”, “question”: “「知っている」の尊敬語は？”, “answer”: “ご存知である”},
{“type”: “keigo”, “question”: “「来る」の謙譲語は？”, “answer”: “参る”},
{“type”: “keigo”, “question”: “「あげる」の謙譲語は？”, “answer”: “差し上げる”},
],
“N1”: [
# 漢字読み
{“type”: “reading”, “question”: “「忌避」の読み方は？”, “answer”: “きひ”},
{“type”: “reading”, “question”: “「逡巡」の読み方は？”, “answer”: “しゅんじゅん”},
{“type”: “reading”, “question”: “「蹉跌」の読み方は？”, “answer”: “さてつ”},
{“type”: “reading”, “question”: “「齟齬」の読み方は？”, “answer”: “そご”},
{“type”: “reading”, “question”: “「払拭」の読み方は？”, “answer”: “ふっしょく”},
{“type”: “reading”, “question”: “「示唆」の読み方は？”, “answer”: “しさ”},
# 語彙
{“type”: “vocab”, “question”: “「ぜいじゃく」を漢字で書くと？”, “answer”: “脆弱”},
{“type”: “vocab”, “question”: “「きゅうきょく」を漢字で書くと？”, “answer”: “究極”},
{“type”: “vocab”, “question”: “「いっかん」を漢字で書くと？（一貫）”, “answer”: “一貫”},
{“type”: “vocab”, “question”: “「ふへん」を漢字で書くと？（普遍）”, “answer”: “普遍”},
# 穴埋め（高度な文法）
{“type”: “fill”, “question”: “「彼の言葉___、プロジェクトは中止になった」（〜をもって）”, “answer”: “をもって”},
{“type”: “fill”, “question”: “「失敗を恐れる___、挑戦できない」（〜あまり）”, “answer”: “あまり”},
{“type”: “fill”, “question”: “「規則___、例外もある」（〜とはいえ）”, “answer”: “とはいえ”},
{“type”: “fill”, “question”: “「成功する___努力が必要だ」（〜いかんによって）”, “answer”: “いかんによって”},
# 反対語
{“type”: “antonym”, “question”: “「普遍的」の反対語は？”, “answer”: “特殊的”},
{“type”: “antonym”, “question”: “「冗長」の反対語は？”, “answer”: “簡潔”},
# 敬語
{“type”: “keigo”, “question”: “「食べる」の最上級尊敬語は？”, “answer”: “召し上がる”},
{“type”: “keigo”, “question”: “「もらう」の最上級謙譲語は？”, “answer”: “頂戴する”},
],
}

TYPE_LABELS = {
“reading”: “📖 漢字読み”,
“vocab”: “📝 語彙”,
“fill”: “✏️ 穴埋め”,
“antonym”: “🔄 反対語”,
“keigo”: “🎩 敬語”,
}

LEVELS = [“N5”, “N4”, “N3”, “N2”, “N1”]

# ==================== ユーザー状態管理 ====================

user_quiz = {}      # {user_id: current_quiz}
user_level = {}     # {user_id: level}
user_score = {}     # {user_id: {“correct”: int, “total”: int}}

# ==================== ヘルパー関数 ====================

def get_random_quiz(level):
return random.choice(QUIZ_DATA[level])

def format_quiz(quiz):
label = TYPE_LABELS.get(quiz[“type”], “❓”)
return f”{label}\n\n{quiz[‘question’]}\n\nひらがな・漢字で答えてね！\n（やめる場合は「やめる」／レベル変更は「レベル変更」）”

def format_score(user_id):
score = user_score.get(user_id, {“correct”: 0, “total”: 0})
correct = score[“correct”]
total = score[“total”]
rate = int(correct / total * 100) if total > 0 else 0
return f”📊 正解数：{correct}/{total}問 （正答率{rate}%）”

# ==================== メイン関数 ====================

def select_level(user_id, level):
if level not in LEVELS:
return f”レベルは N5 / N4 / N3 / N2 / N1 から選んでね！”
user_level[user_id] = level
user_score[user_id] = {“correct”: 0, “total”: 0}
quiz = get_random_quiz(level)
user_quiz[user_id] = quiz
return f”🎌 {level}レベルでスタート！\n\n{format_quiz(quiz)}”

def start_quiz(user_id):
levels_text = “ / “.join(LEVELS)
return f”🇯🇵 日本語クイズへようこそ！\n\nレベルを選んでね！\n{levels_text}\n\n（難しい順：N1 > N2 > N3 > N4 > N5）”

def answer_quiz(user_id, text):
# やめる
if text == “やめる”:
score_text = format_score(user_id)
del user_quiz[user_id]
del user_level[user_id]
return f”クイズを終了したよ！お疲れ様！👋\n\n{score_text}”

```
# レベル変更
if text == "レベル変更":
    del user_quiz[user_id]
    return start_quiz(user_id)

level = user_level[user_id]
current_quiz = user_quiz[user_id]
correct = current_quiz["answer"]

# スコア更新
if user_id not in user_score:
    user_score[user_id] = {"correct": 0, "total": 0}
user_score[user_id]["total"] += 1

if text == correct:
    user_score[user_id]["correct"] += 1
    score_text = format_score(user_id)
    next_quiz = get_random_quiz(level)
    user_quiz[user_id] = next_quiz
    return f"✅ 正解！すごい！\n{score_text}\n\n次の問題！\n{format_quiz(next_quiz)}"
else:
    return f"❌ 惜しい！もう一度考えてみて！\n\n{format_quiz(current_quiz)}"
```

def is_in_quiz(user_id):
return user_id in user_quiz

def is_selecting_level(user_id, text):
return text in LEVELS and user_id not in user_quiz

# ==================== 使い方サンプル ====================

if **name** == “**main**”:
user_id = “test_user”

```
print(start_quiz(user_id))
print()

print(select_level(user_id, "N3"))
print()

# 正解例
current = user_quiz[user_id]["answer"]
print(f"（テスト回答：{current}）")
print(answer_quiz(user_id, current))
print()

print(answer_quiz(user_id, "やめる"))
```