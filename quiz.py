import random

# ====================

# クイズデータ

# choices: 正解を含む選択肢リスト（4択）

# ====================

QUIZ_DATA = {
“N5”: [
{“type”: “reading”, “question”: “「学校」の読み方は？”, “answer”: “がっこう”, “choices”: [“がっこう”, “がくこう”, “がくしょう”, “かっこう”]},
{“type”: “reading”, “question”: “「電車」の読み方は？”, “answer”: “でんしゃ”, “choices”: [“でんしゃ”, “てんしゃ”, “でんさ”, “てんさ”]},
{“type”: “reading”, “question”: “「友達」の読み方は？”, “answer”: “ともだち”, “choices”: [“ともだち”, “ゆうたつ”, “ゆうだち”, “ともたち”]},
{“type”: “reading”, “question”: “「先生」の読み方は？”, “answer”: “せんせい”, “choices”: [“せんせい”, “さきせい”, “せんさい”, “さきさい”]},
{“type”: “reading”, “question”: “「毎日」の読み方は？”, “answer”: “まいにち”, “choices”: [“まいにち”, “まいじつ”, “ごとにち”, “ごとじつ”]},
{“type”: “reading”, “question”: “「今日」の読み方は？”, “answer”: “きょう”, “choices”: [“きょう”, “こんにち”, “いまひ”, “こんじつ”]},
{“type”: “reading”, “question”: “「入口」の読み方は？”, “answer”: “いりぐち”, “choices”: [“いりぐち”, “にゅうこう”, “いりこう”, “にゅうぐち”]},
{“type”: “reading”, “question”: “「出口」の読み方は？”, “answer”: “でぐち”, “choices”: [“でぐち”, “しゅつこう”, “でこう”, “しゅつぐち”]},
{“type”: “reading”, “question”: “「食べ物」の読み方は？”, “answer”: “たべもの”, “choices”: [“たべもの”, “しょくもの”, “たべぶつ”, “しょくぶつ”]},
{“type”: “reading”, “question”: “「水」の読み方は？”, “answer”: “みず”, “choices”: [“みず”, “すい”, “みす”, “すいき”]},
{“type”: “kanji”, “question”: “「おおきい」を漢字で書くと？”, “answer”: “大きい”, “choices”: [“大きい”, “太きい”, “多きい”, “犬きい”]},
{“type”: “kanji”, “question”: “「ちいさい」を漢字で書くと？”, “answer”: “小さい”, “choices”: [“小さい”, “少さい”, “細さい”, “小ちい”]},
{“type”: “kanji”, “question”: “「あたらしい」を漢字で書くと？”, “answer”: “新しい”, “choices”: [“新しい”, “若しい”, “初しい”, “鮮しい”]},
{“type”: “kanji”, “question”: “「やすい」を漢字で書くと？”, “answer”: “安い”, “choices”: [“安い”, “易い”, “休い”, “低い”]},
{“type”: “kanji”, “question”: “「たかい」を漢字で書くと？”, “answer”: “高い”, “choices”: [“高い”, “高い”, “貴い”, “高い”]},
{“type”: “grammar”, “question”: “「電車___ 乗ります」”, “answer”: “に”, “choices”: [“に”, “を”, “で”, “が”]},
{“type”: “grammar”, “question”: “「りんご___ 食べます」”, “answer”: “を”, “choices”: [“を”, “に”, “で”, “が”]},
{“type”: “grammar”, “question”: “「学校___ 行きます」”, “answer”: “へ”, “choices”: [“へ”, “を”, “に”, “で”]},
{“type”: “grammar”, “question”: “「本___ あります」”, “answer”: “が”, “choices”: [“が”, “は”, “を”, “に”]},
{“type”: “grammar”, “question”: “「おはよう___ 」（丁寧な朝の挨拶）”, “answer”: “ございます”, “choices”: [“ございます”, “です”, “ます”, “でした”]},
{“type”: “antonym”, “question”: “「大きい」の反対語は？”, “answer”: “小さい”, “choices”: [“小さい”, “低い”, “短い”, “細い”]},
{“type”: “antonym”, “question”: “「新しい」の反対語は？”, “answer”: “古い”, “choices”: [“古い”, “悪い”, “暗い”, “遠い”]},
{“type”: “antonym”, “question”: “「速い」の反対語は？”, “answer”: “遅い”, “choices”: [“遅い”, “重い”, “弱い”, “暗い”]},
{“type”: “antonym”, “question”: “「上」の反対語は？”, “answer”: “下”, “choices”: [“下”, “左”, “右”, “後”]},
{“type”: “antonym”, “question”: “「白い」の反対語は？”, “answer”: “黒い”, “choices”: [“黒い”, “青い”, “赤い”, “暗い”]},
],
“N4”: [
{“type”: “reading”, “question”: “「仕事」の読み方は？”, “answer”: “しごと”, “choices”: [“しごと”, “しごと”, “さぎょう”, “こうじ”]},
{“type”: “reading”, “question”: “「旅行」の読み方は？”, “answer”: “りょこう”, “choices”: [“りょこう”, “たびこう”, “りょかん”, “たびかん”]},
{“type”: “reading”, “question”: “「練習」の読み方は？”, “answer”: “れんしゅう”, “choices”: [“れんしゅう”, “れんしゅ”, “けんしゅう”, “けんしゅ”]},
{“type”: “reading”, “question”: “「準備」の読み方は？”, “answer”: “じゅんび”, “choices”: [“じゅんび”, “しゅんび”, “じゅんぴ”, “じゅんい”]},
{“type”: “reading”, “question”: “「連絡」の読み方は？”, “answer”: “れんらく”, “choices”: [“れんらく”, “れんろく”, “れんかく”, “れんがく”]},
{“type”: “reading”, “question”: “「注意」の読み方は？”, “answer”: “ちゅうい”, “choices”: [“ちゅうい”, “ちゅうに”, “じゅうい”, “じゅうに”]},
{“type”: “reading”, “question”: “「予定」の読み方は？”, “answer”: “よてい”, “choices”: [“よてい”, “よじょう”, “よつい”, “よじょ”]},
{“type”: “reading”, “question”: “「説明」の読み方は？”, “answer”: “せつめい”, “choices”: [“せつめい”, “せつあき”, “そつめい”, “そつあき”]},
{“type”: “kanji”, “question”: “「かんたん」を漢字で書くと？”, “answer”: “簡単”, “choices”: [“簡単”, “感単”, “間単”, “観単”]},
{“type”: “kanji”, “question”: “「べんり」を漢字で書くと？”, “answer”: “便利”, “choices”: [“便利”, “弁利”, “便里”, “変利”]},
{“type”: “kanji”, “question”: “「しんぱい」を漢字で書くと？”, “answer”: “心配”, “choices”: [“心配”, “新配”, “芯配”, “深配”]},
{“type”: “kanji”, “question”: “「きけん」を漢字で書くと？”, “answer”: “危険”, “choices”: [“危険”, “機険”, “危検”, “期険”]},
{“type”: “grammar”, “question”: “「この本は難し___ です」（〜すぎる）”, “answer”: “すぎる”, “choices”: [“すぎる”, “すぎた”, “すぎて”, “すぎず”]},
{“type”: “grammar”, “question”: “「映画を見___ 行きませんか」（〜に）”, “answer”: “に”, “choices”: [“に”, “を”, “へ”, “で”]},
{“type”: “grammar”, “question”: “「もっと早く来れ___ よかった」”, “answer”: “ば”, “choices”: [“ば”, “て”, “たら”, “なら”]},
{“type”: “grammar”, “question”: “「電話し___ おきました」”, “answer”: “て”, “choices”: [“て”, “に”, “を”, “が”]},
{“type”: “grammar”, “question”: “「この映画は見___ ことがあります」”, “answer”: “た”, “choices”: [“た”, “る”, “て”, “ない”]},
{“type”: “keigo”, “question”: “「食べる」の尊敬語は？”, “answer”: “召し上がる”, “choices”: [“召し上がる”, “いただく”, “食べられる”, “食べなさる”]},
{“type”: “keigo”, “question”: “「言う」の謙譲語は？”, “answer”: “申す”, “choices”: [“申す”, “おっしゃる”, “言われる”, “言いなさる”]},
{“type”: “keigo”, “question”: “「いる」の尊敬語は？”, “answer”: “いらっしゃる”, “choices”: [“いらっしゃる”, “おる”, “いられる”, “おいでなさる”]},
{“type”: “keigo”, “question”: “「見る」の謙譲語は？”, “answer”: “拝見する”, “choices”: [“拝見する”, “ご覧になる”, “見られる”, “お見えになる”]},
{“type”: “antonym”, “question”: “「安全」の反対語は？”, “answer”: “危険”, “choices”: [“危険”, “困難”, “不安”, “恐怖”]},
{“type”: “antonym”, “question”: “「便利」の反対語は？”, “answer”: “不便”, “choices”: [“不便”, “不利”, “不満”, “不快”]},
{“type”: “antonym”, “question”: “「増える」の反対語は？”, “answer”: “減る”, “choices”: [“減る”, “消える”, “なくなる”, “小さくなる”]},
{“type”: “antonym”, “question”: “「始まる」の反対語は？”, “answer”: “終わる”, “choices”: [“終わる”, “止まる”, “消える”, “消滅する”]},
],
“N3”: [
{“type”: “reading”, “question”: “「経験」の読み方は？”, “answer”: “けいけん”, “choices”: [“けいけん”, “きょうけん”, “けいかん”, “きょうかん”]},
{“type”: “reading”, “question”: “「環境」の読み方は？”, “answer”: “かんきょう”, “choices”: [“かんきょう”, “かんけい”, “えんきょう”, “えんけい”]},
{“type”: “reading”, “question”: “「判断」の読み方は？”, “answer”: “はんだん”, “choices”: [“はんだん”, “はんとう”, “ばんだん”, “ばんとう”]},
{“type”: “reading”, “question”: “「影響」の読み方は？”, “answer”: “えいきょう”, “choices”: [“えいきょう”, “えいかん”, “えいこう”, “かげきょう”]},
{“type”: “reading”, “question”: “「可能性」の読み方は？”, “answer”: “かのうせい”, “choices”: [“かのうせい”, “かのうしょう”, “かのうき”, “かのうし”]},
{“type”: “reading”, “question”: “「責任」の読み方は？”, “answer”: “せきにん”, “choices”: [“せきにん”, “せきりん”, “せきじん”, “せきひん”]},
{“type”: “reading”, “question”: “「解決」の読み方は？”, “answer”: “かいけつ”, “choices”: [“かいけつ”, “かいかつ”, “かいはつ”, “かいさつ”]},
{“type”: “reading”, “question”: “「関係」の読み方は？”, “answer”: “かんけい”, “choices”: [“かんけい”, “かんきょう”, “かんさい”, “かんじ”]},
{“type”: “kanji”, “question”: “「あいまい」を漢字で書くと？”, “answer”: “曖昧”, “choices”: [“曖昧”, “愛昧”, “哀昧”, “愛味”]},
{“type”: “kanji”, “question”: “「かくじつ」を漢字で書くと？”, “answer”: “確実”, “choices”: [“確実”, “各実”, “覚実”, “格実”]},
{“type”: “kanji”, “question”: “「せきにん」を漢字で書くと？”, “answer”: “責任”, “choices”: [“責任”, “席任”, “積任”, “責人”]},
{“type”: “kanji”, “question”: “「かいけつ」を漢字で書くと？”, “answer”: “解決”, “choices”: [“解決”, “回決”, “開決”, “改決”]},
{“type”: “grammar”, “question”: “「試験に合格する___ 、毎日勉強している」”, “answer”: “ために”, “choices”: [“ために”, “ように”, “から”, “ので”]},
{“type”: “grammar”, “question”: “「彼は来る___ 来なかった」”, “answer”: “はずなのに”, “choices”: [“はずなのに”, “つもりなのに”, “みたいなのに”, “らしいのに”]},
{“type”: “grammar”, “question”: “「雨___ かかわらず、試合は続いた」”, “answer”: “にもかかわらず”, “choices”: [“にもかかわらず”, “なのに”, “だから”, “でも”]},
{“type”: “grammar”, “question”: “「彼___ よれば、明日は休みだ」”, “answer”: “に”, “choices”: [“に”, “が”, “の”, “で”]},
{“type”: “grammar”, “question”: “「食べ___ 、すぐ寝てしまった」”, “answer”: “てから”, “choices”: [“てから”, “てので”, “たあとで”, “ながら”]},
{“type”: “keigo”, “question”: “「もらう」の謙譲語は？”, “answer”: “いただく”, “choices”: [“いただく”, “もらわれる”, “頂戴する”, “受け取る”]},
{“type”: “keigo”, “question”: “「見る」の尊敬語は？”, “answer”: “ご覧になる”, “choices”: [“ご覧になる”, “拝見する”, “見られる”, “お見せになる”]},
{“type”: “keigo”, “question”: “「聞く」の謙譲語は？”, “answer”: “伺う”, “choices”: [“伺う”, “お聞きになる”, “聞かれる”, “拝聴する”]},
{“type”: “keigo”, “question”: “「する」の謙譲語は？”, “answer”: “いたす”, “choices”: [“いたす”, “なさる”, “される”, “しられる”]},
{“type”: “antonym”, “question”: “「積極的」の反対語は？”, “answer”: “消極的”, “choices”: [“消極的”, “否定的”, “悲観的”, “受動的”]},
{“type”: “antonym”, “question”: “「肯定」の反対語は？”, “answer”: “否定”, “choices”: [“否定”, “拒否”, “反対”, “批判”]},
{“type”: “antonym”, “question”: “「楽観的」の反対語は？”, “answer”: “悲観的”, “choices”: [“悲観的”, “消極的”, “否定的”, “現実的”]},
{“type”: “antonym”, “question”: “「原因」の反対語は？”, “answer”: “結果”, “choices”: [“結果”, “過程”, “目的”, “影響”]},
],
“N2”: [
{“type”: “reading”, “question”: “「懸念」の読み方は？”, “answer”: “けねん”, “choices”: [“けねん”, “けんねん”, “かねん”, “かいねん”]},
{“type”: “reading”, “question”: “「矛盾」の読み方は？”, “answer”: “むじゅん”, “choices”: [“むじゅん”, “もじゅん”, “むじん”, “もじん”]},
{“type”: “reading”, “question”: “「妥協」の読み方は？”, “answer”: “だきょう”, “choices”: [“だきょう”, “たきょう”, “だけい”, “たけい”]},
{“type”: “reading”, “question”: “「貢献」の読み方は？”, “answer”: “こうけん”, “choices”: [“こうけん”, “こうきん”, “くうけん”, “くうきん”]},
{“type”: “reading”, “question”: “「把握」の読み方は？”, “answer”: “はあく”, “choices”: [“はあく”, “はにぎ”, “はかく”, “はりょく”]},
{“type”: “reading”, “question”: “「促進」の読み方は？”, “answer”: “そくしん”, “choices”: [“そくしん”, “そくすすむ”, “うながしん”, “そくし”]},
{“type”: “reading”, “question”: “「抑制」の読み方は？”, “answer”: “よくせい”, “choices”: [“よくせい”, “よくそく”, “おさえせい”, “よくそ”]},
{“type”: “reading”, “question”: “「概念」の読み方は？”, “answer”: “がいねん”, “choices”: [“がいねん”, “がいかん”, “かんねん”, “かいねん”]},
{“type”: “kanji”, “question”: “「ふくざつ」を漢字で書くと？”, “answer”: “複雑”, “choices”: [“複雑”, “復雑”, “腹雑”, “複乱”]},
{“type”: “kanji”, “question”: “「こうりつ」を漢字で書くと？”, “answer”: “効率”, “choices”: [“効率”, “公率”, “功率”, “高率”]},
{“type”: “kanji”, “question”: “「むじゅん」を漢字で書くと？”, “answer”: “矛盾”, “choices”: [“矛盾”, “武盾”, “矛順”, “務盾”]},
{“type”: “kanji”, “question”: “「はあく」を漢字で書くと？”, “answer”: “把握”, “choices”: [“把握”, “波握”, “把惑”, “把確”]},
{“type”: “grammar”, “question”: “「彼___ 失敗するとは思わなかった」（〜に限って）”, “answer”: “に限って”, “choices”: [“に限って”, “だけは”, “こそは”, “さえも”]},
{“type”: “grammar”, “question”: “「努力した___ 、結果が出た」（〜かいがあって）”, “answer”: “かいがあって”, “choices”: [“かいがあって”, “おかげで”, “ために”, “ので”]},
{“type”: “grammar”, “question”: “「彼女は美しい___ 、頭もいい」”, “answer”: “うえに”, “choices”: [“うえに”, “だけに”, “ために”, “ものの”]},
{“type”: “grammar”, “question”: “「問題が解決され___ 、次へ進む」”, “answer”: “次第”, “choices”: [“次第”, “たら”, “たあと”, “てから”]},
{“type”: “grammar”, “question”: “「これ___ 限りで終わりにします」”, “answer”: “を”, “choices”: [“を”, “が”, “で”, “に”]},
{“type”: “keigo”, “question”: “「知っている」の尊敬語は？”, “answer”: “ご存知である”, “choices”: [“ご存知である”, “知られる”, “知っておられる”, “お知りになる”]},
{“type”: “keigo”, “question”: “「言う」の尊敬語は？”, “answer”: “おっしゃる”, “choices”: [“おっしゃる”, “申す”, “言われる”, “申し上げる”]},
{“type”: “keigo”, “question”: “「聞く」の尊敬語は？”, “answer”: “お聞きになる”, “choices”: [“お聞きになる”, “伺う”, “拝聴する”, “聞かれる”]},
{“type”: “keigo”, “question”: “「見せる」の謙譲語は？”, “answer”: “お見せする”, “choices”: [“お見せする”, “ご覧になる”, “見せられる”, “お目にかける”]},
{“type”: “antonym”, “question”: “「促進」の反対語は？”, “answer”: “抑制”, “choices”: [“抑制”, “減少”, “阻止”, “後退”]},
{“type”: “antonym”, “question”: “「拡大」の反対語は？”, “answer”: “縮小”, “choices”: [“縮小”, “減少”, “消去”, “消滅”]},
{“type”: “antonym”, “question”: “「需要」の反対語は？”, “answer”: “供給”, “choices”: [“供給”, “生産”, “流通”, “販売”]},
{“type”: “antonym”, “question”: “「主観的」の反対語は？”, “answer”: “客観的”, “choices”: [“客観的”, “論理的”, “合理的”, “科学的”]},
],
“N1”: [
{“type”: “reading”, “question”: “「忌避」の読み方は？”, “answer”: “きひ”, “choices”: [“きひ”, “いひ”, “きかい”, “いかい”]},
{“type”: “reading”, “question”: “「逡巡」の読み方は？”, “answer”: “しゅんじゅん”, “choices”: [“しゅんじゅん”, “じゅんしゅん”, “しゅんじん”, “じゅんじん”]},
{“type”: “reading”, “question”: “「齟齬」の読み方は？”, “answer”: “そご”, “choices”: [“そご”, “しょご”, “そぐ”, “しょぐ”]},
{“type”: “reading”, “question”: “「払拭」の読み方は？”, “answer”: “ふっしょく”, “choices”: [“ふっしょく”, “はらいぬぐ”, “ふつしょく”, “はらいふく”]},
{“type”: “reading”, “question”: “「示唆」の読み方は？”, “answer”: “しさ”, “choices”: [“しさ”, “じさ”, “しそう”, “じそう”]},
{“type”: “reading”, “question”: “「忖度」の読み方は？”, “answer”: “そんたく”, “choices”: [“そんたく”, “すんたく”, “そんど”, “すんど”]},
{“type”: “reading”, “question”: “「瑕疵」の読み方は？”, “answer”: “かし”, “choices”: [“かし”, “きず”, “けつ”, “かくし”]},
{“type”: “reading”, “question”: “「僭越」の読み方は？”, “answer”: “せんえつ”, “choices”: [“せんえつ”, “せんこう”, “そうえつ”, “そうこう”]},
{“type”: “reading”, “question”: “「看過」の読み方は？”, “answer”: “かんか”, “choices”: [“かんか”, “みすごす”, “かんご”, “みか”]},
{“type”: “reading”, “question”: “「恣意的」の読み方は？”, “answer”: “しいてき”, “choices”: [“しいてき”, “じいてき”, “きまぐれてき”, “しいし”]},
{“type”: “kanji”, “question”: “「ぜいじゃく」を漢字で書くと？”, “answer”: “脆弱”, “choices”: [“脆弱”, “税弱”, “脆若”, “贅弱”]},
{“type”: “kanji”, “question”: “「いっかん」を漢字で書くと？”, “answer”: “一貫”, “choices”: [“一貫”, “一管”, “一観”, “一間”]},
{“type”: “kanji”, “question”: “「そんたく」を漢字で書くと？”, “answer”: “忖度”, “choices”: [“忖度”, “村度”, “寸度”, “存度”]},
{“type”: “kanji”, “question”: “「かし」（欠陥の意）を漢字で書くと？”, “answer”: “瑕疵”, “choices”: [“瑕疵”, “過失”, “欠疵”, “瑕地”]},
{“type”: “grammar”, “question”: “「彼の言葉___ 、プロジェクトは中止になった」”, “answer”: “をもって”, “choices”: [“をもって”, “によって”, “において”, “を通じて”]},
{“type”: “grammar”, “question”: “「失敗を恐れる___ 、挑戦できない」”, “answer”: “あまり”, “choices”: [“あまり”, “ために”, “から”, “ので”]},
{“type”: “grammar”, “question”: “「規則___ 、例外もある」”, “answer”: “とはいえ”, “choices”: [“とはいえ”, “だからといって”, “にもかかわらず”, “ながらも”]},
{“type”: “grammar”, “question”: “「彼___ あるまじき行為だ」”, “answer”: “に”, “choices”: [“に”, “が”, “として”, “にとって”]},
{“type”: “grammar”, “question”: “「どんな困難___ 、諦めない」”, “answer”: “にあっても”, “choices”: [“にあっても”, “でも”, “だとしても”, “といえども”]},
{“type”: “grammar”, “question”: “「結果___ いかんでは、責任を取る」”, “answer”: “の”, “choices”: [“の”, “が”, “を”, “に”]},
{“type”: “keigo”, “question”: “「言う」の最上級謙譲語は？”, “answer”: “申し上げる”, “choices”: [“申し上げる”, “申す”, “おっしゃる”, “言上する”]},
{“type”: “keigo”, “question”: “「訪問する」の謙譲語は？”, “answer”: “伺う”, “choices”: [“伺う”, “参る”, “おじゃまする”, “訪れる”]},
{“type”: “keigo”, “question”: “「もらう」の最上級謙譲語は？”, “answer”: “頂戴する”, “choices”: [“頂戴する”, “いただく”, “受け取る”, “もらわれる”]},
{“type”: “antonym”, “question”: “「顕在」の反対語は？”, “answer”: “潜在”, “choices”: [“潜在”, “不在”, “非在”, “内在”]},
{“type”: “antonym”, “question”: “「帰納」の反対語は？”, “answer”: “演繹”, “choices”: [“演繹”, “分析”, “推論”, “仮説”]},
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

user_quiz  = {}
user_level = {}
user_score = {}

def get_random_quiz(level):
return random.choice(QUIZ_DATA[level])

def make_quick_reply(choices):
“”“選択肢リストからクイックリプライオブジェクトを生成”””
items = []
for c in choices:
items.append({
“type”: “action”,
“action”: {
“type”: “message”,
“label”: c[:20],  # LINEのラベル上限20文字
“text”: c
}
})
return {“items”: items}

def format_score(user_id):
s = user_score.get(user_id, {“correct”: 0, “total”: 0})
rate = int(s[“correct”] / s[“total”] * 100) if s[“total”] > 0 else 0
return f”📊 正解数：{s[‘correct’]}/{s[‘total’]}問（正答率 {rate}%）”

def start_quiz(user_id):
“”“レベル選択メッセージ（クイックリプライ付き）を返す”””
return {
“text”: “🇯🇵 日本語クイズへようこそ！\nレベルを選んでね！\n（難しい順：N1 ＞ N5）”,
“quick_reply”: make_quick_reply(LEVELS)
}

def select_level(user_id, level):
“”“レベルを設定して最初の問題を返す”””
if level not in LEVELS:
return {“text”: “レベルは N5 / N4 / N3 / N2 / N1 から選んでね！”,
“quick_reply”: make_quick_reply(LEVELS)}
user_level[user_id] = level
user_score[user_id] = {“correct”: 0, “total”: 0}
quiz = get_random_quiz(level)
user_quiz[user_id] = quiz
return _format_question(quiz, f”🎌 {level}レベルでスタート！\n\n”)

def answer_quiz(user_id, text):
if text == “やめる”:
score_text = format_score(user_id)
user_quiz.pop(user_id, None)
user_level.pop(user_id, None)
return {“text”: f”クイズを終了したよ！お疲れ様！👋\n\n{score_text}”}

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
    return _format_question(next_quiz, f"✅ 正解！すごい！\n{score_text}\n\n次の問題！\n")
else:
    return _format_question(current, f"❌ 惜しい！もう一度考えてみて！\n\n")
```

def _format_question(quiz, prefix=””):
“”“問題文＋クイックリプライを生成”””
label = TYPE_LABELS.get(quiz[“type”], “❓”)
choices = quiz[“choices”][:]
random.shuffle(choices)
# 「やめる」「レベル変更」を最後に追加
extra = [“やめる”, “レベル変更”]
text = f”{prefix}{label}\n\n{quiz[‘question’]}”
return {
“text”: text,
“quick_reply”: make_quick_reply(choices + extra)
}

def is_in_quiz(user_id):
return user_id in user_quiz

def is_selecting_level(user_id, text):
return text in LEVELS and user_id not in user_quiz