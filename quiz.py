import random

# ====================

# クイズデータ

# 種類:

# reading = 漢字読み

# kanji   = 漢字書き

# grammar = 文法穴埋め

# keigo   = 敬語変換

# antonym = 反対語

# vocab   = 語彙

# ====================

QUIZ_DATA = {
“N5”: [
{“type”: “reading”, “question”: “「日本語」の読み方は？”, “answer”: “にほんご”},
{“type”: “reading”, “question”: “「学校」の読み方は？”, “answer”: “がっこう”},
{“type”: “reading”, “question”: “「食べ物」の読み方は？”, “answer”: “たべもの”},
{“type”: “reading”, “question”: “「電車」の読み方は？”, “answer”: “でんしゃ”},
{“type”: “reading”, “question”: “「友達」の読み方は？”, “answer”: “ともだち”},
{“type”: “reading”, “question”: “「水」の読み方は？”, “answer”: “みず”},
{“type”: “reading”, “question”: “「山」の読み方は？”, “answer”: “やま”},
{“type”: “reading”, “question”: “「川」の読み方は？”, “answer”: “かわ”},
{“type”: “reading”, “question”: “「先生」の読み方は？”, “answer”: “せんせい”},
{“type”: “reading”, “question”: “「毎日」の読み方は？”, “answer”: “まいにち”},
{“type”: “reading”, “question”: “「今日」の読み方は？”, “answer”: “きょう”},
{“type”: “reading”, “question”: “「右」の読み方は？”, “answer”: “みぎ”},
{“type”: “reading”, “question”: “「左」の読み方は？”, “answer”: “ひだり”},
{“type”: “reading”, “question”: “「入口」の読み方は？”, “answer”: “いりぐち”},
{“type”: “reading”, “question”: “「出口」の読み方は？”, “answer”: “でぐち”},
{“type”: “kanji”, “question”: “「おおきい」を漢字で書くと？”, “answer”: “大きい”},
{“type”: “kanji”, “question”: “「たかい」を漢字で書くと？”, “answer”: “高い”},
{“type”: “kanji”, “question”: “「やすい」を漢字で書くと？”, “answer”: “安い”},
{“type”: “kanji”, “question”: “「あたらしい」を漢字で書くと？”, “answer”: “新しい”},
{“type”: “kanji”, “question”: “「ちいさい」を漢字で書くと？”, “answer”: “小さい”},
{“type”: “kanji”, “question”: “「みず」を漢字で書くと？”, “answer”: “水”},
{“type”: “kanji”, “question”: “「やま」を漢字で書くと？”, “answer”: “山”},
{“type”: “kanji”, “question”: “「かわ」を漢字で書くと？”, “answer”: “川”},
{“type”: “kanji”, “question”: “「ひ」（太陽）を漢字で書くと？”, “answer”: “日”},
{“type”: “kanji”, “question”: “「つき」（月）を漢字で書くと？”, “answer”: “月”},
{“type”: “grammar”, “question”: “「これ___ 私の本です」”, “answer”: “は”},
{“type”: “grammar”, “question”: “「電車___ 乗ります」”, “answer”: “に”},
{“type”: “grammar”, “question”: “「学校___ 行きます」”, “answer”: “へ”},
{“type”: “grammar”, “question”: “「りんご___ 食べます」”, “answer”: “を”},
{“type”: “grammar”, “question”: “「本___ あります」”, “answer”: “が”},
{“type”: “grammar”, “question”: “「おはよう___！」（丁寧な朝の挨拶）”, “answer”: “ございます”},
{“type”: “grammar”, “question”: “「ありがとう___！」（丁寧な感謝）”, “answer”: “ございます”},
{“type”: “grammar”, “question”: “「日本語___ 勉強します」”, “answer”: “を”},
{“type”: “grammar”, “question”: “「私は学生___ 」（〜です）”, “answer”: “です”},
{“type”: “grammar”, “question”: “「明日___ 天気はどうですか」”, “answer”: “の”},
{“type”: “antonym”, “question”: “「大きい」の反対語は？”, “answer”: “小さい”},
{“type”: “antonym”, “question”: “「高い」の反対語は？”, “answer”: “低い”},
{“type”: “antonym”, “question”: “「新しい」の反対語は？”, “answer”: “古い”},
{“type”: “antonym”, “question”: “「長い」の反対語は？”, “answer”: “短い”},
{“type”: “antonym”, “question”: “「右」の反対語は？”, “answer”: “左”},
{“type”: “antonym”, “question”: “「上」の反対語は？”, “answer”: “下”},
{“type”: “antonym”, “question”: “「白い」の反対語は？”, “answer”: “黒い”},
{“type”: “antonym”, “question”: “「速い」の反対語は？”, “answer”: “遅い”},
{“type”: “vocab”, “question”: “「いただきます」は食事の___に言う”, “answer”: “前”},
{“type”: “vocab”, “question”: “「ごちそうさま」は食事の___に言う”, “answer”: “後”},
],
“N4”: [
{“type”: “reading”, “question”: “「仕事」の読み方は？”, “answer”: “しごと”},
{“type”: “reading”, “question”: “「時間」の読み方は？”, “answer”: “じかん”},
{“type”: “reading”, “question”: “「旅行」の読み方は？”, “answer”: “りょこう”},
{“type”: “reading”, “question”: “「練習」の読み方は？”, “answer”: “れんしゅう”},
{“type”: “reading”, “question”: “「説明」の読み方は？”, “answer”: “せつめい”},
{“type”: “reading”, “question”: “「運動」の読み方は？”, “answer”: “うんどう”},
{“type”: “reading”, “question”: “「予定」の読み方は？”, “answer”: “よてい”},
{“type”: “reading”, “question”: “「準備」の読み方は？”, “answer”: “じゅんび”},
{“type”: “reading”, “question”: “「連絡」の読み方は？”, “answer”: “れんらく”},
{“type”: “reading”, “question”: “「注意」の読み方は？”, “answer”: “ちゅうい”},
{“type”: “reading”, “question”: “「生活」の読み方は？”, “answer”: “せいかつ”},
{“type”: “reading”, “question”: “「地図」の読み方は？”, “answer”: “ちず”},
{“type”: “kanji”, “question”: “「かんたん」を漢字で書くと？”, “answer”: “簡単”},
{“type”: “kanji”, “question”: “「べんり」を漢字で書くと？”, “answer”: “便利”},
{“type”: “kanji”, “question”: “「しんぱい」を漢字で書くと？”, “answer”: “心配”},
{“type”: “kanji”, “question”: “「きけん」を漢字で書くと？”, “answer”: “危険”},
{“type”: “kanji”, “question”: “「れんしゅう」を漢字で書くと？”, “answer”: “練習”},
{“type”: “kanji”, “question”: “「りょこう」を漢字で書くと？”, “answer”: “旅行”},
{“type”: “kanji”, “question”: “「じかん」を漢字で書くと？”, “answer”: “時間”},
{“type”: “kanji”, “question”: “「よてい」を漢字で書くと？”, “answer”: “予定”},
{“type”: “grammar”, “question”: “「映画を見___ 行きませんか」（〜に）”, “answer”: “に”},
{“type”: “grammar”, “question”: “「この本は難し___ です」（〜すぎる）”, “answer”: “すぎる”},
{“type”: “grammar”, “question”: “「もっと早く来れ___ よかった」（〜ば）”, “answer”: “ば”},
{“type”: “grammar”, “question”: “「彼女は歌が上手___ なりました」（〜に）”, “answer”: “に”},
{“type”: “grammar”, “question”: “「宿題を___ から、遊びましょう」（して）”, “answer”: “して”},
{“type”: “grammar”, “question”: “「この映画は見___ ことがあります」（〜た）”, “answer”: “た”},
{“type”: “grammar”, “question”: “「電話し___ おきました」（〜て）”, “answer”: “て”},
{“type”: “grammar”, “question”: “「日本語を勉強___ います」（〜して）”, “answer”: “して”},
{“type”: “grammar”, “question”: “「雨___ 、試合は中止になった」（〜のため）”, “answer”: “のため”},
{“type”: “grammar”, “question”: “「もし時間___ あれば、来てください」（〜が）”, “answer”: “が”},
{“type”: “keigo”, “question”: “「食べる」の尊敬語は？”, “answer”: “召し上がる”},
{“type”: “keigo”, “question”: “「言う」の謙譲語は？”, “answer”: “申す”},
{“type”: “keigo”, “question”: “「いる」の尊敬語は？”, “answer”: “いらっしゃる”},
{“type”: “keigo”, “question”: “「行く」の謙譲語は？”, “answer”: “参る”},
{“type”: “keigo”, “question”: “「もらう」の謙譲語は？”, “answer”: “いただく”},
{“type”: “keigo”, “question”: “「する」の丁寧語は？”, “answer”: “いたします”},
{“type”: “keigo”, “question”: “「見る」の謙譲語は？”, “answer”: “拝見する”},
{“type”: “antonym”, “question”: “「安全」の反対語は？”, “answer”: “危険”},
{“type”: “antonym”, “question”: “「簡単」の反対語は？”, “answer”: “難しい”},
{“type”: “antonym”, “question”: “「便利」の反対語は？”, “answer”: “不便”},
{“type”: “antonym”, “question”: “「増える」の反対語は？”, “answer”: “減る”},
{“type”: “antonym”, “question”: “「始まる」の反対語は？”, “answer”: “終わる”},
],
“N3”: [
{“type”: “reading”, “question”: “「経験」の読み方は？”, “answer”: “けいけん”},
{“type”: “reading”, “question”: “「政治」の読み方は？”, “answer”: “せいじ”},
{“type”: “reading”, “question”: “「環境」の読み方は？”, “answer”: “かんきょう”},
{“type”: “reading”, “question”: “「機会」の読み方は？”, “answer”: “きかい”},
{“type”: “reading”, “question”: “「判断」の読み方は？”, “answer”: “はんだん”},
{“type”: “reading”, “question”: “「影響」の読み方は？”, “answer”: “えいきょう”},
{“type”: “reading”, “question”: “「可能性」の読み方は？”, “answer”: “かのうせい”},
{“type”: “reading”, “question”: “「責任」の読み方は？”, “answer”: “せきにん”},
{“type”: “reading”, “question”: “「関係」の読み方は？”, “answer”: “かんけい”},
{“type”: “reading”, “question”: “「解決」の読み方は？”, “answer”: “かいけつ”},
{“type”: “kanji”, “question”: “「あいまい」を漢字で書くと？”, “answer”: “曖昧”},
{“type”: “kanji”, “question”: “「かくじつ」を漢字で書くと？”, “answer”: “確実”},
{“type”: “kanji”, “question”: “「じょうきょう」を漢字で書くと？”, “answer”: “状況”},
{“type”: “kanji”, “question”: “「かんきょう」を漢字で書くと？”, “answer”: “環境”},
{“type”: “kanji”, “question”: “「せきにん」を漢字で書くと？”, “answer”: “責任”},
{“type”: “kanji”, “question”: “「かいけつ」を漢字で書くと？”, “answer”: “解決”},
{“type”: “kanji”, “question”: “「はんだん」を漢字で書くと？”, “answer”: “判断”},
{“type”: “kanji”, “question”: “「えいきょう」を漢字で書くと？”, “answer”: “影響”},
{“type”: “grammar”, “question”: “「試験に合格する___ 、毎日勉強している」（〜ために）”, “answer”: “ために”},
{“type”: “grammar”, “question”: “「彼は来る___ 来なかった」（〜はずなのに）”, “answer”: “はずなのに”},
{“type”: “grammar”, “question”: “「困った___ は相談してください」（〜とき）”, “answer”: “とき”},
{“type”: “grammar”, “question”: “「雨___ かかわらず、試合は続いた」（〜にも）”, “answer”: “にもかかわらず”},
{“type”: “grammar”, “question”: “「努力すれ___ 、夢は叶う」（〜ば）”, “answer”: “ば”},
{“type”: “grammar”, “question”: “「この問題は難し___ 、諦めた」（〜すぎて）”, “answer”: “すぎて”},
{“type”: “grammar”, “question”: “「食べ___ 、すぐ寝てしまった」（〜てから）”, “answer”: “てから”},
{“type”: “grammar”, “question”: “「先生___ おっしゃった通りです」（〜が）”, “answer”: “が”},
{“type”: “grammar”, “question”: “「彼___ よれば、明日は休みだ」（〜に）”, “answer”: “に”},
{“type”: “grammar”, “question”: “「どんな___ でも諦めない」（〜こと）”, “answer”: “こと”},
{“type”: “keigo”, “question”: “「もらう」の謙譲語は？”, “answer”: “いただく”},
{“type”: “keigo”, “question”: “「見る」の尊敬語は？”, “answer”: “ご覧になる”},
{“type”: “keigo”, “question”: “「する」の謙譲語は？”, “answer”: “いたす”},
{“type”: “keigo”, “question”: “「知っている」の尊敬語は？”, “answer”: “ご存知だ”},
{“type”: “keigo”, “question”: “「来る」の尊敬語は？”, “answer”: “いらっしゃる”},
{“type”: “keigo”, “question”: “「あげる」の謙譲語は？”, “answer”: “差し上げる”},
{“type”: “keigo”, “question”: “「聞く」の謙譲語は？”, “answer”: “伺う”},
{“type”: “antonym”, “question”: “「積極的」の反対語は？”, “answer”: “消極的”},
{“type”: “antonym”, “question”: “「具体的」の反対語は？”, “answer”: “抽象的”},
{“type”: “antonym”, “question”: “「楽観的」の反対語は？”, “answer”: “悲観的”},
{“type”: “antonym”, “question”: “「肯定」の反対語は？”, “answer”: “否定”},
{“type”: “antonym”, “question”: “「原因」の反対語は？”, “answer”: “結果”},
],
“N2”: [
{“type”: “reading”, “question”: “「懸念」の読み方は？”, “answer”: “けねん”},
{“type”: “reading”, “question”: “「概念」の読み方は？”, “answer”: “がいねん”},
{“type”: “reading”, “question”: “「恩恵」の読み方は？”, “answer”: “おんけい”},
{“type”: “reading”, “question”: “「矛盾」の読み方は？”, “answer”: “むじゅん”},
{“type”: “reading”, “question”: “「妥協」の読み方は？”, “answer”: “だきょう”},
{“type”: “reading”, “question”: “「貢献」の読み方は？”, “answer”: “こうけん”},
{“type”: “reading”, “question”: “「摩擦」の読み方は？”, “answer”: “まさつ”},
{“type”: “reading”, “question”: “「把握」の読み方は？”, “answer”: “はあく”},
{“type”: “reading”, “question”: “「促進」の読み方は？”, “answer”: “そくしん”},
{“type”: “reading”, “question”: “「抑制」の読み方は？”, “answer”: “よくせい”},
{“type”: “kanji”, “question”: “「ひっし」を漢字で書くと？”, “answer”: “必死”},
{“type”: “kanji”, “question”: “「ふくざつ」を漢字で書くと？”, “answer”: “複雑”},
{“type”: “kanji”, “question”: “「こうりつ」を漢字で書くと？”, “answer”: “効率”},
{“type”: “kanji”, “question”: “「ぎむ」を漢字で書くと？”, “answer”: “義務”},
{“type”: “kanji”, “question”: “「けねん」を漢字で書くと？”, “answer”: “懸念”},
{“type”: “kanji”, “question”: “「はあく」を漢字で書くと？”, “answer”: “把握”},
{“type”: “kanji”, “question”: “「そくしん」を漢字で書くと？”, “answer”: “促進”},
{“type”: “kanji”, “question”: “「むじゅん」を漢字で書くと？”, “answer”: “矛盾”},
{“type”: “grammar”, “question”: “「彼___ 失敗するとは思わなかった」（〜に限って）”, “answer”: “に限って”},
{“type”: “grammar”, “question”: “「努力した___ 、結果が出た」（〜かいがあって）”, “answer”: “かいがあって”},
{“type”: “grammar”, “question”: “「どう考え___ 理解できない」（〜ても）”, “answer”: “ても”},
{“type”: “grammar”, “question”: “「彼女は美しい___ 、頭もいい」（〜うえに）”, “answer”: “うえに”},
{“type”: “grammar”, “question”: “「問題が解決され___ 、次のステップへ進む」（〜次第）”, “answer”: “次第”},
{“type”: “grammar”, “question”: “「規則___ 、例外もある」（〜とはいえ）”, “answer”: “とはいえ”},
{“type”: “grammar”, “question”: “「失敗を恐れる___ 、挑戦することが大切だ」（〜より）”, “answer”: “より”},
{“type”: “grammar”, “question”: “「予算___ よって、計画が変わる」（〜に）”, “answer”: “に”},
{“type”: “grammar”, “question”: “「これ___ 限りで終わりにします」（〜を）”, “answer”: “を”},
{“type”: “grammar”, “question”: “「彼___ あってこそ、成功できた」（〜が）”, “answer”: “が”},
{“type”: “keigo”, “question”: “「知っている」の尊敬語は？”, “answer”: “ご存知である”},
{“type”: “keigo”, “question”: “「来る」の謙譲語は？”, “answer”: “参る”},
{“type”: “keigo”, “question”: “「あげる」の謙譲語は？”, “answer”: “差し上げる”},
{“type”: “keigo”, “question”: “「言う」の尊敬語は？”, “answer”: “おっしゃる”},
{“type”: “keigo”, “question”: “「もらう」の謙譲語は？”, “answer”: “頂戴する”},
{“type”: “keigo”, “question”: “「見せる」の謙譲語は？”, “answer”: “お見せする”},
{“type”: “keigo”, “question”: “「聞く」の尊敬語は？”, “answer”: “お聞きになる”},
{“type”: “antonym”, “question”: “「抽象的」の反対語は？”, “answer”: “具体的”},
{“type”: “antonym”, “question”: “「主観的」の反対語は？”, “answer”: “客観的”},
{“type”: “antonym”, “question”: “「促進」の反対語は？”, “answer”: “抑制”},
{“type”: “antonym”, “question”: “「拡大」の反対語は？”, “answer”: “縮小”},
{“type”: “antonym”, “question”: “「需要」の反対語は？”, “answer”: “供給”},
],
“N1”: [
{“type”: “reading”, “question”: “「忌避」の読み方は？”, “answer”: “きひ”},
{“type”: “reading”, “question”: “「逡巡」の読み方は？”, “answer”: “しゅんじゅん”},
{“type”: “reading”, “question”: “「蹉跌」の読み方は？”, “answer”: “さてつ”},
{“type”: “reading”, “question”: “「齟齬」の読み方は？”, “answer”: “そご”},
{“type”: “reading”, “question”: “「払拭」の読み方は？”, “answer”: “ふっしょく”},
{“type”: “reading”, “question”: “「示唆」の読み方は？”, “answer”: “しさ”},
{“type”: “reading”, “question”: “「鑑みる」の読み方は？”, “answer”: “かんがみる”},
{“type”: “reading”, “question”: “「恣意的」の読み方は？”, “answer”: “しいてき”},
{“type”: “reading”, “question”: “「瑕疵」の読み方は？”, “answer”: “かし”},
{“type”: “reading”, “question”: “「僭越」の読み方は？”, “answer”: “せんえつ”},
{“type”: “reading”, “question”: “「忖度」の読み方は？”, “answer”: “そんたく”},
{“type”: “reading”, “question”: “「看過」の読み方は？”, “answer”: “かんか”},
{“type”: “kanji”, “question”: “「ぜいじゃく」を漢字で書くと？”, “answer”: “脆弱”},
{“type”: “kanji”, “question”: “「きゅうきょく」を漢字で書くと？”, “answer”: “究極”},
{“type”: “kanji”, “question”: “「いっかん」を漢字で書くと？”, “answer”: “一貫”},
{“type”: “kanji”, “question”: “「ふへん」を漢字で書くと？”, “answer”: “普遍”},
{“type”: “kanji”, “question”: “「しさ」を漢字で書くと？”, “answer”: “示唆”},
{“type”: “kanji”, “question”: “「そんたく」を漢字で書くと？”, “answer”: “忖度”},
{“type”: “kanji”, “question”: “「かし」を漢字で書くと？”, “answer”: “瑕疵”},
{“type”: “kanji”, “question”: “「せんえつ」を漢字で書くと？”, “answer”: “僭越”},
{“type”: “grammar”, “question”: “「彼の言葉___ 、プロジェクトは中止になった」（〜をもって）”, “answer”: “をもって”},
{“type”: “grammar”, “question”: “「失敗を恐れる___ 、挑戦できない」（〜あまり）”, “answer”: “あまり”},
{“type”: “grammar”, “question”: “「規則___ 、例外もある」（〜とはいえ）”, “answer”: “とはいえ”},
{“type”: “grammar”, “question”: “「成功する___ 努力が必要だ」（〜いかんによって）”, “answer”: “いかんによって”},
{“type”: “grammar”, “question”: “「彼___ あるまじき行為だ」（〜に）”, “answer”: “に”},
{“type”: “grammar”, “question”: “「どんな困難___ 、諦めない」（〜にあっても）”, “answer”: “にあっても”},
{“type”: “grammar”, “question”: “「結果___ いかんでは、責任を取る」（〜の）”, “answer”: “の”},
{“type”: “grammar”, “question”: “「資料___ 基づいて報告します」（〜に）”, “answer”: “に”},
{“type”: “grammar”, “question”: “「事情___ よっては、対応できない場合もある」（〜に）”, “answer”: “に”},
{“type”: “grammar”, “question”: “「彼___ して初めて、その意味が分かった」（〜に）”, “answer”: “に”},
{“type”: “keigo”, “question”: “「食べる」の最上級尊敬語は？”, “answer”: “召し上がる”},
{“type”: “keigo”, “question”: “「もらう」の最上級謙譲語は？”, “answer”: “頂戴する”},
{“type”: “keigo”, “question”: “「言う」の最上級謙譲語は？”, “answer”: “申し上げる”},
{“type”: “keigo”, “question”: “「訪問する」の謙譲語は？”, “answer”: “伺う”},
{“type”: “keigo”, “question”: “「見せる」の尊敬語は？”, “answer”: “お目にかける”},
{“type”: “keigo”, “question”: “「知らせる」の謙譲語は？”, “answer”: “ご報告申し上げる”},
{“type”: “antonym”, “question”: “「普遍的」の反対語は？”, “answer”: “特殊的”},
{“type”: “antonym”, “question”: “「冗長」の反対語は？”, “answer”: “簡潔”},
{“type”: “antonym”, “question”: “「顕在」の反対語は？”, “answer”: “潜在”},
{“type”: “antonym”, “question”: “「帰納」の反対語は？”, “answer”: “演繹”},
{“type”: “antonym”, “question”: “「主観」の反対語は？”, “answer”: “客観”},
],
}

TYPE_LABELS = {
“reading”: “📖 漢字読み”,
“kanji”:   “✍️ 漢字書き”,
“grammar”: “📝 文法穴埋め”,
“keigo”:   “🎩 敬語変換”,
“antonym”: “🔄 反対語”,
“vocab”:   “💡 語彙”,
}

LEVELS = [“N5”, “N4”, “N3”, “N2”, “N1”]

# ==================== ユーザー状態管理 ====================

user_quiz  = {}
user_level = {}
user_score = {}

# ==================== ヘルパー関数 ====================

def get_random_quiz(level):
return random.choice(QUIZ_DATA[level])

def format_quiz(quiz):
label = TYPE_LABELS.get(quiz[“type”], “?”)
return (
f”{label}\n\n”
f”{quiz[‘question’]}\n\n”
f”ひらがな・漢字で答えてね！\n”
f”（やめる場合は「やめる」／レベル変更は「レベル変更」）”
)

def format_score(user_id):
s = user_score.get(user_id, {“correct”: 0, “total”: 0})
rate = int(s[“correct”] / s[“total”] * 100) if s[“total”] > 0 else 0
return f”📊 正解数：{s[‘correct’]}/{s[‘total’]}問（正答率 {rate}%）”

# ==================== メイン関数 ====================

def start_quiz(user_id):
return (
“🇯🇵 日本語クイズへようこそ！\n\n”
“レベルを選んでね！\n”
“N5 / N4 / N3 / N2 / N1\n\n”
“（難しい順：N1 > N2 > N3 > N4 > N5）”
)

def select_level(user_id, level):
if level not in LEVELS:
return “レベルは N5 / N4 / N3 / N2 / N1 から選んでね！”
user_level[user_id] = level
user_score[user_id] = {“correct”: 0, “total”: 0}
quiz = get_random_quiz(level)
user_quiz[user_id] = quiz
return f”🎌 {level}レベルでスタート！\n\n{format_quiz(quiz)}”

def answer_quiz(user_id, text):
if text == “やめる”:
score_text = format_score(user_id)
user_quiz.pop(user_id, None)
user_level.pop(user_id, None)
return f”クイズを終了したよ！お疲れ様！👋\n\n{score_text}”

```
if text == "レベル変更":
    user_quiz.pop(user_id, None)
    return start_quiz(user_id)

level       = user_level[user_id]
current     = user_quiz[user_id]
correct_ans = current["answer"]

user_score.setdefault(user_id, {"correct": 0, "total": 0})
user_score[user_id]["total"] += 1

if text == correct_ans:
    user_score[user_id]["correct"] += 1
    score_text = format_score(user_id)
    next_quiz  = get_random_quiz(level)
    user_quiz[user_id] = next_quiz
    return f"✅ 正解！すごい！\n{score_text}\n\n次の問題！\n{format_quiz(next_quiz)}"
else:
    return f"❌ 惜しい！もう一度考えてみて！\n\n{format_quiz(current)}"
```

def is_in_quiz(user_id):
return user_id in user_quiz

def is_selecting_level(user_id, text):
return text in LEVELS and user_id not in user_quiz

# ==================== 動作確認 ====================

if **name** == “**main**”:
uid = “test_user”
print(start_quiz(uid))
print()
print(select_level(uid, “N3”))
print()
ans = user_quiz[uid][“answer”]
print(f”（テスト回答：{ans}）”)
print(answer_quiz(uid, ans))
print()
print(answer_quiz(uid, “やめる”))