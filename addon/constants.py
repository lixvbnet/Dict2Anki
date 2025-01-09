VERSION = 'v6.3.6k'
RELEASE_URL = 'https://github.com/lixvbnet/Dict2Anki'
VERSION_CHECK_API = 'https://api.github.com/repos/lixvbnet/Dict2Anki/releases/latest'
WINDOW_TITLE = f'Dict2Anki {VERSION}'
MODEL_NAME = f'Dict2Anki'

USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36'
HEADERS = {
    'User-Agent': USER_AGENT
}

LOG_BUFFER_CAPACITY = 20    # number of log items
LOG_FLUSH_INTERVAL = 3      # seconds

# continue to use Dict2Anki 4.x model
ASSET_FILENAME_PREFIX = "MG"
MODEL_FIELDS = [
    'term', 'definition',
    'definition_en',
    'uk', 'us',
    'phrase0', 'phrase1', 'phrase2', 'phrase_explain0', 'phrase_explain1', 'phrase_explain2',
    'sentence0', 'sentence1', 'sentence2', 'sentence_explain0', 'sentence_explain1', 'sentence_explain2', 'sentence_speech0', 'sentence_speech1', 'sentence_speech2',
    'pplaceHolder0', 'pplaceHolder1', 'pplaceHolder2',
    'splaceHolder0', 'splaceHolder1', 'splaceHolder2',
    'image', 'pronunciation',
    'group', 'exam_type', 'modifiedTime',
]
CARD_SETTINGS = ['definition_en', 'image', 'pronunciation', 'phrase', 'sentence', 'exam_type']


class FieldGroup:
    def __init__(self):
        self.definition_en = "{{definition_en}}"
        self.image = "{{image}}"
        self.pronunciation = "{{pronunciation}}"
        self.phrase = [
            ("{{phrase0}}", "{{phrase_explain0}}", "{{pplaceHolder0}}"),
            ("{{phrase1}}", "{{phrase_explain1}}", "{{pplaceHolder1}}"),
            ("{{phrase2}}", "{{phrase_explain2}}", "{{pplaceHolder2}}"),
        ]
        self.sentence = [
            ("{{sentence0}}", "{{sentence_explain0}}", "{{splaceHolder0}}", '<a onclick="this.firstChild.play()"><audio src="{{sentence_speech0}}"></audio>▶︎</a>'),
            ("{{sentence1}}", "{{sentence_explain1}}", "{{splaceHolder1}}", '<a onclick="this.firstChild.play()"><audio src="{{sentence_speech1}}"></audio>▶︎</a>'),
            ("{{sentence2}}", "{{sentence_explain2}}", "{{splaceHolder2}}", '<a onclick="this.firstChild.play()"><audio src="{{sentence_speech2}}"></audio>▶︎</a>'),
        ]
        self.exam_type = "{{exam_type}}"

    def toggleOff(self, field):
        if field not in CARD_SETTINGS:
            raise RuntimeError(f"Unexpected field: {field}. Must be in {CARD_SETTINGS}!")
        if field == 'phrase':
            setattr(self, field, [
                ("", "", ""),
                ("", "", ""),
                ("", "", "")
            ])
        elif field == 'sentence':
            setattr(self, field, [
                ("", "", "", ""),
                ("", "", "", ""),
                ("", "", "", "")
            ])
        else:
            setattr(self, field, "")

    def toString(self) -> str:
        return f"definition_en={self.definition_en}, image={self.image}, pronunciation={self.pronunciation}, phrase={self.phrase}, sentence={self.sentence}"

    def __str__(self) -> str:
        return self.toString()

    def __repr__(self) -> str:
        return self.toString()


def normal_card_template_qfmt(fg: FieldGroup):
    return f"""\
<table>
    <tr>
        <td>
            <h1 class="term">{{{{term}}}}</h1>
            <span>{fg.pronunciation}</span>
            <div class="pronounce">
                <span class="phonetic">UK[{{{{uk}}}}]</span>
                <span class="phonetic">US[{{{{us}}}}]</span>
            </div>
            <div class="definition">Tap To View</div>
            <div class="definition_en"></div>
        </td>
        <td style="width: 33%;">
        </td>
    </tr>
</table>
<div class="divider"></div>
<table>
    <tr><td class="phrase">{fg.phrase[0][0]}</td><td>{fg.phrase[0][2]}</td></tr>
    <tr><td class="phrase">{fg.phrase[1][0]}</td><td>{fg.phrase[1][2]}</td></tr>
    <tr><td class="phrase">{fg.phrase[2][0]}</td><td>{fg.phrase[2][2]}</td></tr>
</table>
<table>
    <tr>
        <td class="sentence">
            {fg.sentence[0][0]}
            {fg.sentence[0][3]}
        </td>
        <td>{fg.sentence[0][2]}</td>
    </tr>
    <tr>
        <td class="sentence">
            {fg.sentence[1][0]}
            {fg.sentence[1][3]}
        </td>
        <td>{fg.sentence[1][2]}</td>
    </tr>
    <tr>
        <td class="sentence">
            {fg.sentence[2][0]}
            {fg.sentence[2][3]}
        </td>
        <td>{fg.sentence[2][2]}</td>
    </tr>
</table>
"""


def normal_card_template_afmt(fg: FieldGroup):
    return f"""\
<table>
    <tr>
        <td>
        <h1 class="term">{{{{term}}}}</h1>
            <span>{fg.pronunciation}</span>
            <div class="pronounce">
                <span class="phonetic">UK[{{{{uk}}}}]</span>
                <span class="phonetic">US[{{{{us}}}}]</span>
            </div>
            <div class="definition">{{{{definition}}}}</div>
            <div class="definition_en">{fg.definition_en}</div>
            <div class="exam_type">{fg.exam_type}</div>
        </td>
        <td style="width: 33%;">
            {fg.image}
        </td>
    </tr>
</table>
<div class="divider"></div>
<table>
    <tr><td class="phrase">{fg.phrase[0][0]}</td><td>{fg.phrase[0][1]}</td></tr>
    <tr><td class="phrase">{fg.phrase[1][0]}</td><td>{fg.phrase[1][1]}</td></tr>
    <tr><td class="phrase">{fg.phrase[2][0]}</td><td>{fg.phrase[2][1]}</td></tr>
</table>
<table>
    <tr>
        <td class="sentence">
            {fg.sentence[0][0]}
            {fg.sentence[0][3]}
        </td>
        <td>{fg.sentence[0][1]}</td>
    </tr>
    <tr>
        <td class="sentence">
            {fg.sentence[1][0]}
            {fg.sentence[1][3]}
        </td>
        <td>{fg.sentence[1][1]}</td>
    </tr>
    <tr>
        <td class="sentence">
            {fg.sentence[2][0]}
            {fg.sentence[2][3]}
        </td>
        <td>{fg.sentence[2][1]}</td>
    </tr>
</table>
"""


def backwards_card_template_qfmt(fg: FieldGroup):
    return f"""\
<table>
    <tr>
        <td>
        <h1 class="term"></h1>
            <div class="pronounce">
                <span class="phonetic">UK[Tap To View]</span>
                <span class="phonetic">US[Tap To View]</span>
            </div>
            <div class="definition">{{{{definition}}}}</div>
            <div class="definition_en">{fg.definition_en}</div>
        </td>
        <td style="width: 33%;">
            {fg.image}
        </td>
    </tr>
</table>
<div class="divider"></div>
<table>
    <tr><td class="phrase">{fg.phrase[0][2]}</td><td>{fg.phrase[0][1]}</td></tr>
    <tr><td class="phrase">{fg.phrase[1][2]}</td><td>{fg.phrase[1][1]}</td></tr>
    <tr><td class="phrase">{fg.phrase[2][2]}</td><td>{fg.phrase[2][1]}</td></tr>
</table>
<table>
    <tr><td class="sentence">{fg.sentence[0][2]}</td><td>{fg.sentence[0][1]}</td></tr>
    <tr><td class="sentence">{fg.sentence[1][2]}</td><td>{fg.sentence[1][1]}</td></tr>
    <tr><td class="sentence">{fg.sentence[2][2]}</td><td>{fg.sentence[2][1]}</td></tr>
</table>
"""


def backwards_card_template_afmt(fg: FieldGroup):
    return normal_card_template_afmt(fg)


# Normal card template
NORMAL_CARD_TEMPLATE_NAME = "Normal"
# Backwards card template (using same AFMT and CSS with Normal card template)
BACKWARDS_CARD_TEMPLATE_NAME = "Backwards"
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
.exam_type {
  margin: 1em 0 0em 0;
  color: gray;
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
