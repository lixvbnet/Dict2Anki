VERSION = 'v6.2.0'
RELEASE_URL = 'https://github.com/lixvbnet/Dict2Anki'
VERSION_CHECK_API = 'https://api.github.com/repos/lixvbnet/Dict2Anki/releases/latest'
WINDOW_TITLE = f'Dict2Anki {VERSION}'
MODEL_NAME = f'Dict2Anki-fork'      # change this only when there's some breaking change

BASIC_OPTION = ['definition', 'sentence', 'phrase', 'image', 'BrEPhonetic', 'AmEPhonetic']  # 顺序和名称不可修改
EXTRA_OPTION = ['BrEPron', 'AmEPron', 'noPron']  # 顺序和名称不可修改

# MODEL_FIELDS = ['term', 'definition', 'sentenceFront', 'sentenceBack', 'phraseFront', 'phraseBack', 'image', 'BrEPhonetic', 'AmEPhonetic', 'BrEPron', 'AmEPron']  # 名称不可修改
# continue to use old model (Dict2Anki 4.x)
MODEL_FIELDS = [
    'term', 'definition', 'uk', 'us',
    'phrase0', 'phrase1', 'phrase2', 'phrase_explain0', 'phrase_explain1', 'phrase_explain2',
    'sentence0', 'sentence1', 'sentence2', 'sentence_explain0', 'sentence_explain1', 'sentence_explain2',
    'pplaceHolder0', 'pplaceHolder1', 'pplaceHolder2',
    'splaceHolder0', 'splaceHolder1', 'splaceHolder2',
    'image', 'pronunciation',
]
