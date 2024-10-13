from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import MeCab
import unicodedata
import re
from collections import Counter
from itertools import islice

# ChromeDriverのパスを指定
chrome_driver_path = './chromedriver-win64/chromedriver.exe'

# ChromeDriverのサービスを開始
service = Service(executable_path=chrome_driver_path)
driver = webdriver.Chrome(service=service)

# 企業情報のURL
print("企業名を入れて下さい")
company_name = str(input())

if company_name == "NTTデータ":
    # urls =['https://nttdata-recruit.com/introduction/keyword.html', 'https://nttdata-recruit.com/introduction/introduction.html', 'https://nttdata-recruit.com/introduction/achieve.html'] #NTTデータ採用ページ（キーワードで知るNTTデータ，はじめに知るNTTデータ，実現する世界）
    urls =['https://nttdata-recruit.com/introduction/introduction.html'] #NTTデータ採用ページ（始めに知るNTT）
    texts = []
    for url in urls:

        # URLを開く
        driver.get(url)

        # ページ内容を取得（JavaScriptで動的に生成されるコンテンツを考慮）
        page_source = driver.page_source

        # BeautifulSoupでパース
        soup = BeautifulSoup(page_source, 'html.parser')

        # ページ全体からテキストを抽出（すべてのタグ内のテキストを含む）
        # text = soup.get_text()
        paragraphs_p = soup.find_all('p')
        paragraphs_h2 = soup.find_all('h2')

        # すべてのタグのテキストを結合して1つの文字列にする
        text = ' '.join([p.get_text(strip=True) for p in paragraphs_p])
        texts.append(text)
    
    text = ' '.join([text for text in texts])

elif company_name == "TIS":
    # url = 'https://www.tis.co.jp/recruit/abouttis/feature/' #TIS採用ページ（特徴・強み
    url = 'https://www.tis.co.jp/recruit/strategy/01/' #TIS採用ページ（戦略1）

    # URLを開く
    driver.get(url)

    # ページ内容を取得（JavaScriptで動的に生成されるコンテンツを考慮）
    page_source = driver.page_source

    # BeautifulSoupでパース
    soup = BeautifulSoup(page_source, 'html.parser')

    # ページ全体からテキストを抽出（すべてのタグ内のテキストを含む）
    # text = soup.get_text()
    paragraphs = soup.find_all('p')

    paragraphs_h3 = soup.find_all('h3')

    # すべての <p> タグのテキストを結合して1つの文字列にする
    text = ' '.join([p.get_text(strip=True) for p in paragraphs])

elif company_name == "NEC":
    # url = "https://jpn.nec.com/recruit/newgraduate/index.html" #NEC採用ページ
    url = 'https://jpn.nec.com/recruit/about.html' #NEC採用ページ（NECについて)

    # URLを開く
    driver.get(url)

    # ページ内容を取得（JavaScriptで動的に生成されるコンテンツを考慮）
    page_source = driver.page_source

    # BeautifulSoupでパース
    soup = BeautifulSoup(page_source, 'html.parser')

    # ページ全体からテキストを抽出（すべてのタグ内のテキストを含む）
    # text = soup.get_text()
    paragraphs = soup.find_all('p')

    # すべての <p> タグのテキストを結合して1つの文字列にする
    text = ' '.join([p.get_text(strip=True) for p in paragraphs])

# WebDriverを終了
driver.quit()

# MeCabの初期化
mecab = MeCab.Tagger("C:/Program Files/MeCab/dic")

# N-gramを生成する関数
def generate_n_grams(token_list, n=2):
    # zipを使って連続するn個の単語のペアやトリプルを生成
    n_grams = zip(*[token_list[i:] for i in range(n)])
    return [' '.join(ngram) for ngram in n_grams]

# MeCab解析後のN-gramを適用する処理
def mecab_tokenizer_with_ngram(text, n=1):
    replaced_text = unicodedata.normalize("NFKC", text)
    replaced_text = re.sub(r'[【】 () （） 『』　「」]', '', replaced_text)

    parsed_lines = mecab.parse(replaced_text).split("\n")[:-2]

    # 表層形を取得
    surfaces = [l.split("\t")[0] for l in parsed_lines if l]
    # 品詞を取得
    pos = [l.split("\t")[1].split(",")[0] for l in parsed_lines if l]
    # 名詞と形容詞に絞り込み
    target_pos = ["名詞", "形容詞"]
    token_list = [t for t, p in zip(surfaces, pos) if p in target_pos]

    # ひらがなのみの単語を除く
    kana_re = re.compile("^[あ-ん]+$")
    token_list = [t for t in token_list if not kana_re.match(t)]

    # 文字列が2文字以上のもののみを抽出
    token_list = [t for t in token_list if len(t) > 1]

    # N-gramを生成
    n_gram_tokens = generate_n_grams(token_list, n)

    # トークンの頻度を計算（頻度が高い順に表示）
    token_counter = Counter(n_gram_tokens)
    most_common_tokens = token_counter.most_common()

    # デバッグ：最も多く出現するN-gramを確認
    print(f"Most common {n}-grams: {most_common_tokens[:10]}")

    # 各トークンをスペースを空けて結合
    return ' '.join(n_gram_tokens)

# 2-gramを使って形態素解析とN-gramを適用
words_with_ngram = mecab_tokenizer_with_ngram(text, n=1)

# 日本語対応のフォントを指定してワードクラウドを生成
if words_with_ngram.strip():
    wordcloud = WordCloud(
        font_path='C:/Windows/Fonts/HGRSGU.TTC',  # 日本語対応フォントを指定
        width=800, height=400, background_color='white'
    ).generate(words_with_ngram)

    # ワードクラウドを表示
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.show()
else:
    print("No words found for word cloud generation.")

"""

# 関数の設定
def mecab_tokenizer(text):
    replaced_text = unicodedata.normalize("NFKC", text)
    # replaced_text = replaced_text.upper()
    replaced_text = re.sub(r'[【】 () （） 『』　「」]', '', replaced_text) #【】 () 「」　『』の除去
    # replaced_text = re.sub(r'[\[\［］\]]', ' ', replaced_text)   # ［］の除去
    # replaced_text = re.sub(r'[@＠]\w+', '', replaced_text)  # メンションの除去
    # replaced_text = re.sub(r'\d+\.*\d*', '', replaced_text) #数字を0にする
    # replaced_text = re.sub(r'[予約 リスト 追加 企業 エントリー 行い 以下 ボタン 予約 リスト 確認 予約 リスト エントリー 受付 開始 トップ ページ エントリー 受付 開始 会員 人 ログ イン 最終 更新 日 現在 応募 停止 削除 株式 社 本部 部 年度 卒 採用 皆 OPENWORK クチコミ 情報 検索 クア メセ 担当 登録 無料 すべて ため 回答 強み 弱み]', '', replaced_text)
    replaced_text = re.sub(r'[ <p> </p> <br/> -]', '', replaced_text) #数字を0にする

    parsed_lines = mecab.parse(replaced_text).split("\n")[:-2]

    # 表層系を取得
    surfaces = [l.split("\t")[0] for l in parsed_lines if l]
    # 品詞を取得
    pos = [l.split("\t")[1].split(",")[0] for l in parsed_lines if l]
    # 名詞と形容詞に絞り込み
    target_pos = ["名詞", "形容詞"]
    token_list = [t for t, p in zip(surfaces, pos) if p in target_pos]

    # # ひらがなのみの単語を除く
    kana_re = re.compile("^[あ-ん]+$")
    token_list = [t for t in token_list if not kana_re.match(t)]

    # 文字列が2文字以上のもののみを抽出
    token_list = [t for t in token_list if len(t) > 1]

    # 各トークンを少しスペースを空けて（' '）結合
    return ' '.join(token_list)

# 関数の実行
words = mecab_tokenizer(text)

# デバッグ：トークンが空でないか確認
print(f"Extracted words: {words[:100]}...")  # 最初の100文字を表示して確認

# 日本語対応のフォントを指定してワードクラウドを生成
if words.strip():  # wordsが空でないことを確認
    wordcloud = WordCloud(
        font_path='C:/Windows/Fonts/HGRSGU.TTC',  # 日本語対応フォントを指定
        width=800, height=400, background_color='white'
    ).generate(words)

    # ワードクラウドを表示
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.show()
else:
    print("No words found for word cloud generation.")

"""