from Dict2Anki.addon.constants import MODEL_FIELDS, BASIC_OPTION, EXTRA_OPTION
import logging

logger = logging.getLogger('dict2Anki.noteManager')
try:
    from aqt import mw
    import anki
except ImportError:
    from test.dummy_aqt import mw
    from test import dummy_anki as anki


def getDeckList():
    return [deck['name'] for deck in mw.col.decks.all()]


def getWordsByDeck(deckName) -> [str]:
    notes = mw.col.findNotes(f'deck:"{deckName}"')
    words = []
    for nid in notes:
        note = mw.col.getNote(nid)
        if note.model().get('name', '').lower().startswith('dict2anki') and note['term']:
            words.append(note['term'])
    return words


def getNotes(wordList, deckName) -> list:
    notes = []
    for word in wordList:
        note = mw.col.findNotes(f'deck:"{deckName}" term:"{word}"')
        if note:
            notes.append(note[0])
    return notes


def getOrCreateDeck(deckName, model):
    deck_id = mw.col.decks.id(deckName)
    deck = mw.col.decks.get(deck_id)
    mw.col.decks.select(deck['id'])
    mw.col.decks.save(deck)
    mw.col.models.setCurrent(model)
    model['did'] = deck['id']
    mw.col.models.save(model)
    mw.col.reset()
    mw.reset()
    return deck


def getOrCreateModel(modelName, force=False):
    """Create Note Model (Note Type)"""
    model = mw.col.models.byName(modelName)
    if model:
        if set([f['name'] for f in model['flds']]) == set(MODEL_FIELDS):
            return model
        if force:   # Dangerous action!!!  It would delete model, AND all its cards/notes!
            logger.warning(f"Force deleting model {modelName}")
            mw.col.models.rem(model)
        else:
            raise RuntimeError(f"Model '{modelName}' already exists but has different fields!")

    logger.info(f'Creating model {modelName}')
    newModel = mw.col.models.new(modelName)
    for field in MODEL_FIELDS:
        mw.col.models.addField(newModel, mw.col.models.newField(field))
    return newModel


def getOrCreateModelCardTemplate(modelObject, cardTemplateName):
    """Create Card Template (Card Type)"""
    logger.info(f'添加卡片类型:{cardTemplateName}')
    existingCardTemplate = modelObject['tmpls']
    if cardTemplateName in [t.get('name') for t in existingCardTemplate]:
        return
    cardTemplate = mw.col.models.newTemplate(cardTemplateName)
    cardTemplate['qfmt'] = '''\
        <table>
            <tr>
            <td>
                <h1 class="term">{{term}}</h1>
                <span>{{pronunciation}}</span>
                <div class="pronounce">
                    <span class="phonetic">UK[{{uk}}]</span>
                    <span class="phonetic">US[{{us}}]</span>
                </div>
                <div class="definiton">Tap To View</div>
            </td>
            <td>
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
    '''
    cardTemplate['afmt'] = '''\
        <table>
            <tr>
            <td>
            <h1 class="term">{{term}}</h1>
                <span>{{pronunciation}}</span>
                <div class="pronounce">
                    <span class="phonetic">UK[{{uk}}]</span>
                    <span class="phonetic">US[{{us}}]</span>
                </div>
                <div class="definiton">{{definition}}</div>
            </td>
            <td>
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
    '''
    modelObject['css'] = '''
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
          max-height: 120px;
        }
        tr {
          vertical-align: top;
        }
    '''
    mw.col.models.addTemplate(modelObject, cardTemplate)
    mw.col.models.add(modelObject)


def addNoteToDeck(deck, model, currentConfig: dict, word: dict, whichPron: str):
    """
    Add note
    :param deck: deck
    :param model: model
    :param currentConfig: currentConfig
    :param word: (dict) query result of a word
    :return: None
    """
    if not word:
        logger.warning(f'查询结果{word} 异常，忽略')
        return
    model['did'] = deck['id']

    # create new note
    note = anki.notes.Note(mw.col, model)
    note['term'] = word['term']
    if word['definition_short']:    # TODO: using short definition here. Need to make it configurable!
        note['definition'] = word['definition_short']
    if word['BrEPhonetic']:
        note['uk'] = word['BrEPhonetic']
    if word['AmEPhonetic']:
        note['us'] = word['AmEPhonetic']
    if word[whichPron]:
        note['pronunciation'] = f"[sound:{whichPron}_{word['term']}.mp3]"
    if word['phrase']:
        for i, phrase_tuple in enumerate(word['phrase']):
            note[f'phrase{i}'], note[f'phrase_explain{i}'] = phrase_tuple
            note[f'pplaceHolder{i}'] = "Tap To View"

    if word['sentence']:
        for i, sentence_tuple in enumerate(word['sentence']):
            note[f'sentence{i}'], note[f'sentence_explain{i}'] = sentence_tuple
            note[f'splaceHolder{i}'] = "Tap To View"

    if word['image']:               # TODO: download the image and reference it locally instead
        note['image'] = "<img src='{}' />".format(word['image'])

    # for configName in BASIC_OPTION + EXTRA_OPTION:
    #     logger.debug(f'字段:{configName}--结果:{term.get(configName)}')
    #     if term.get(configName):
    #         # 短语例句
    #         if configName in ['sentence', 'phrase'] and currentConfig[configName]:
    #             note[f'{configName}Front'] = '\n'.join(
    #                 [f'<tr><td>{e.strip()}</td></tr>' for e, _ in term[configName]])
    #             note[f'{configName}Back'] = '\n'.join(
    #                 [f'<tr><td>{e.strip()}<br>{c.strip()}</td></tr>' for e, c in term[configName]])
    #         # 图片
    #         elif configName == 'image':
    #             note[configName] = f'src="{term[configName]}"'
    #         # 释义
    #         elif configName == 'definition' and currentConfig[configName]:
    #             note[configName] = ' '.join(term[configName])
    #         # 发音
    #         elif configName in EXTRA_OPTION[:2]:
    #             note[configName] = f"[sound:{configName}_{term['term']}.mp3]"
    #         # 其他
    #         elif currentConfig[configName]:
    #             note[configName] = term[configName]

    mw.col.addNote(note)
    mw.col.reset()
    logger.info(f"添加笔记{note['term']}")
