VERSION = 'v6.3.2'
RELEASE_URL = 'https://github.com/lixvbnet/Dict2Anki'
VERSION_CHECK_API = 'https://api.github.com/repos/lixvbnet/Dict2Anki/releases/latest'
WINDOW_TITLE = f'Dict2Anki {VERSION}'
MODEL_NAME = f'Dict2Anki-dev'

USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36'
HEADERS = {
    'User-Agent': USER_AGENT
}

LOG_BUFFER_CAPACITY = 20    # number of log items
LOG_FLUSH_INTERVAL = 3      # seconds

# BASIC_OPTION = ['definition', 'sentence', 'phrase', 'image', 'BrEPhonetic', 'AmEPhonetic']  # 顺序和名称不可修改
# EXTRA_OPTION = ['BrEPron', 'AmEPron', 'noPron']  # 顺序和名称不可修改

# MODEL_FIELDS = [
#     'term', 'definition', 'sentenceFront', 'sentenceBack', 'phraseFront', 'phraseBack',
#     'image', 'BrEPhonetic', 'AmEPhonetic', 'BrEPron', 'AmEPron'
# ]  # 名称不可修改

# continue to use Dict2Anki 4.x model
ASSET_FILENAME_PREFIX = "MG"
MODEL_FIELDS = [
    'term', 'definition',
    'definition_en',
    'uk', 'us',
    'phrase0', 'phrase1', 'phrase2', 'phrase_explain0', 'phrase_explain1', 'phrase_explain2',
    'sentence0', 'sentence1', 'sentence2', 'sentence_explain0', 'sentence_explain1', 'sentence_explain2',
    'pplaceHolder0', 'pplaceHolder1', 'pplaceHolder2',
    'splaceHolder0', 'splaceHolder1', 'splaceHolder2',
    'image', 'pronunciation',
    'group', 'modifiedTime', 'exam_type',
]

# Normal card template
NORMAL_CARD_TEMPLATE_NAME = "Normal"
NORMAL_CARD_TEMPLATE_QFMT = """\
<table>
    <tr>
        <td>
            <h1 class="term">{{term}}</h1>
            <span>{{pronunciation}}</span>
            <div class="pronounce">
                <span class="phonetic">UK[{{uk}}]</span>
                <span class="phonetic">US[{{us}}]</span>
            </div>
            <div class="definition">Tap To View</div>
            <div class="definition_en"></div>
        </td>
        <td style="width: 33%;">
            {{image}}
        </td>
    </tr>
</table>
<div class="divider"></div>
<table>
    <tr><td class="phrase">{{phrase0}}</td><td>{{pplaceHolder0}}</td></tr>
    <tr><td class="phrase">{{phrase1}}</td><td>{{pplaceHolder1}}</td></tr>
    <tr><td class="phrase">{{phrase2}}</td><td>{{pplaceHolder2}}</td></tr>
</table>
<table>
    <tr><td class="sentence">{{sentence0}}</td><td>{{splaceHolder0}}</td></tr>
    <tr><td class="sentence">{{sentence1}}</td><td>{{splaceHolder1}}</td></tr>
    <tr><td class="sentence">{{sentence2}}</td><td>{{splaceHolder2}}</td></tr>
</table>
"""
NORMAL_CARD_TEMPLATE_AFMT = """\
<table>
    <tr>
        <td>
        <h1 class="term">{{term}}</h1>
            <span>{{pronunciation}}</span>
            <div class="pronounce">
                <span class="phonetic">UK[{{uk}}]</span>
                <span class="phonetic">US[{{us}}]</span>
            </div>
            <div class="definition">{{definition}}</div>
            <div class="definition_en">{{definition_en}}</div>
        </td>
        <td style="width: 33%;">
            {{image}}
        </td>
    </tr>
</table>
<div class="divider"></div>
<table>
    <tr><td class="phrase">{{phrase0}}</td><td>{{phrase_explain0}}</td></tr>
    <tr><td class="phrase">{{phrase1}}</td><td>{{phrase_explain1}}</td></tr>
    <tr><td class="phrase">{{phrase2}}</td><td>{{phrase_explain2}}</td></tr>
</table>
<table>
    <tr><td class="sentence">{{sentence0}}</td><td>{{sentence_explain0}}</td></tr>
    <tr><td class="sentence">{{sentence1}}</td><td>{{sentence_explain1}}</td></tr>
    <tr><td class="sentence">{{sentence2}}</td><td>{{sentence_explain2}}</td></tr>
</table>
"""

CARD_TEMPLATE_CSS = """\
.card {
  font-family: arial;
  font-size: 16px;
  text-align: left;
  color: #212121;
  background-color: white;
}
.pronounce {
  line-height: 30px;
  font-size: 26px;
  margin-bottom: 0;
}
.phonetic {
  font-size: 16px;
  font-family: "lucida sans unicode", arial, sans-serif;
  color: #01848f;
}
.term {
  margin-bottom: -5px;
}
.divider {
  margin: 1em 0 1em 0;
  border-bottom: 2px solid #4caf50;
}
.phrase,
.sentence {
  color: #01848f;
  padding-right: 1em;
}
img {
  max-height: 300px;
}
tr {
  vertical-align: top;
}
"""

# Backwards card template (using same AFMT and CSS with Normal card template)
BACKWARDS_CARD_TEMPLATE_NAME = "Backwards"
BACKWARDS_CARD_TEMPLATE_QFMT = """\
<table>
    <tr>
        <td>
        <h1 class="term"></h1>
            <div class="pronounce">
                <span class="phonetic">UK[Tap To View]</span>
                <span class="phonetic">US[Tap To View]</span>
            </div>
            <div class="definition">{{definition}}</div>
            <div class="definition_en">{{definition_en}}</div>
        </td>
        <td style="width: 33%;">
            {{image}}
        </td>
    </tr>
</table>
<div class="divider"></div>
<table>
    <tr><td class="phrase">{{pplaceHolder0}}</td><td>{{phrase_explain0}}</td></tr>
    <tr><td class="phrase">{{pplaceHolder1}}</td><td>{{phrase_explain1}}</td></tr>
    <tr><td class="phrase">{{pplaceHolder2}}</td><td>{{phrase_explain2}}</td></tr>
</table>
<table>
    <tr><td class="sentence">{{splaceHolder0}}</td><td>{{sentence_explain0}}</td></tr>
    <tr><td class="sentence">{{splaceHolder1}}</td><td>{{sentence_explain1}}</td></tr>
    <tr><td class="sentence">{{splaceHolder2}}</td><td>{{sentence_explain2}}</td></tr>
</table>
"""
BACKWARDS_CARD_TEMPLATE_AFMT = NORMAL_CARD_TEMPLATE_AFMT


PRON_TYPES = ['noPron', 'BrEPron', 'AmEPron']


def get_pronunciation(word: dict, preferred_pron: int) -> (int, bool):
    """:return: pron_type: int, is_fallback: bool"""
    if preferred_pron == 0:
        return 0, False
    if word[PRON_TYPES[preferred_pron]]:
        return preferred_pron, False
    fallback_pron = 2 if preferred_pron == 1 else 1
    if word[PRON_TYPES[fallback_pron]]:
        return fallback_pron, True
    return 0, True


def default_image_filename(term: str) -> str:
    return f"{ASSET_FILENAME_PREFIX}-{term}.jpg"


def default_audio_filename(term: str) -> str:
    return f"{ASSET_FILENAME_PREFIX}-{term}.mp3"
