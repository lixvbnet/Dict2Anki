from Dict2Anki.addon.constants import *
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
    logger.info(f'添加卡片类型: {cardTemplateName}')
    existingCardTemplate = modelObject['tmpls']
    if cardTemplateName in [t.get('name') for t in existingCardTemplate]:
        logger.info(f"[Skip] {cardTemplateName} already exists.")
        return
    cardTemplate = mw.col.models.newTemplate(cardTemplateName)
    cardTemplate['qfmt'] = NORMAL_CARD_TEMPLATE_QFMT
    cardTemplate['afmt'] = NORMAL_CARD_TEMPLATE_AFMT
    modelObject['css'] = NORMAL_CARD_TEMPLATE_CSS
    mw.col.models.addTemplate(modelObject, cardTemplate)
    mw.col.models.add(modelObject)


def getOrCreateBackwardsCardTemplate(modelObject, backwardsTemplateName):
    """Create Backwards Card Template (Card Type) to existing Dict2Anki Note Type"""
    logger.info(f'Add Backwards Template: {backwardsTemplateName}')
    existingCardTemplate = modelObject['tmpls']
    if backwardsTemplateName in [t.get('name') for t in existingCardTemplate]:
        logger.info(f"[Skip] {backwardsTemplateName} already exists.")
        return
    cardTemplate = mw.col.models.newTemplate(backwardsTemplateName)
    cardTemplate['qfmt'] = BACKWARDS_CARD_TEMPLATE_QFMT
    cardTemplate['afmt'] = BACKWARDS_CARD_TEMPLATE_AFMT
    mw.col.models.addTemplate(modelObject, cardTemplate)
    mw.col.models.save(modelObject)


def deleteBackwardsCardTemplate(modelObject, backwardsTemplateObject):
    """Delete Backwards Card Template (Card Type) from existing Dict2Anki Note Type"""
    mw.col.models.remove_template(modelObject, backwardsTemplateObject)
    mw.col.models.save(modelObject)


def addNoteToDeck(deck, model, currentConfig: dict, word: dict, imageFilename: str, whichPron: str, pronFilename: str):
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
    # TODO: preferring short definition here. Need to make it configurable!
    include_definition_en = False   # TODO: make this configurable!
    definitions = []
    if word['definition_short']:    # str
        definitions.append(word['definition_short'])
    elif word['definition']:        # [str]
        definitions.extend(word['definition'])

    if include_definition_en:
        definitions.extend(word['definition_en'])

    if definitions:
        note['definition'] = '\n'.join(definitions)
    else:
        logger.warning(f"NO DEFINITION FOR WORD {word['term']}!!!")

    if word['BrEPhonetic']:
        note['uk'] = word['BrEPhonetic']
    if word['AmEPhonetic']:
        note['us'] = word['AmEPhonetic']

    if word['image']:
        note['image'] = f'<div><img src="{imageFilename}" /></div>'

    if word[whichPron]:
        note['pronunciation'] = f"[sound:{pronFilename}]"

    if word['phrase']:
        for i, phrase_tuple in enumerate(word['phrase']):
            note[f'phrase{i}'], note[f'phrase_explain{i}'] = phrase_tuple
            note[f'pplaceHolder{i}'] = "Tap To View"

    if word['sentence']:
        for i, sentence_tuple in enumerate(word['sentence']):
            note[f'sentence{i}'], note[f'sentence_explain{i}'] = sentence_tuple
            note[f'splaceHolder{i}'] = "Tap To View"

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
