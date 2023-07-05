from .constants import *
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


def getNoteIDsOfWords(wordList, deckName) -> list:
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


def getOrCreateModel(modelName, recreate=False) -> (object, bool, bool):
    """Create Note Model (Note Type). return: (model, newCreated, fieldsUpdated)"""
    model = mw.col.models.byName(modelName)
    if model:
        if not recreate:
            updated = mergeModelFields(model)
            return model, False, updated
        else:       # Dangerous action!!!  It would delete model, AND all its cards/notes!
            logger.warning(f"Force deleting and recreating model {modelName}")
            mw.col.models.rem(model)

    logger.info(f'Creating model {modelName}')
    newModel = mw.col.models.new(modelName)
    for field in MODEL_FIELDS:
        mw.col.models.addField(newModel, mw.col.models.newField(field))
    return newModel, True, True


def getOrCreateCardTemplate(modelObject, cardTemplateName, qfmt, afmt, css, add=True):
    """Create Card Template (Card Type)"""
    logger.info(f"Add card template {cardTemplateName}")
    existingCardTemplate = modelObject['tmpls']
    if cardTemplateName in [t.get('name') for t in existingCardTemplate]:
        logger.info(f"[Skip] Card Type '{cardTemplateName}' already exists.")
        return
    cardTemplate = mw.col.models.newTemplate(cardTemplateName)
    cardTemplate['qfmt'] = qfmt
    cardTemplate['afmt'] = afmt
    modelObject['css'] = css
    mw.col.models.addTemplate(modelObject, cardTemplate)
    if add:
        mw.col.models.add(modelObject)
    else:
        mw.col.models.save(modelObject)


def getOrCreateNormalCardTemplate(modelObject):
    """Create Normal Card Template (Card Type)"""
    getOrCreateCardTemplate(modelObject, NORMAL_CARD_TEMPLATE_NAME,
                            NORMAL_CARD_TEMPLATE_QFMT, NORMAL_CARD_TEMPLATE_AFMT, CARD_TEMPLATE_CSS, add=True)


def getOrCreateBackwardsCardTemplate(modelObject):
    """Create Backwards Card Template (Card Type) to existing Dict2Anki Note Type"""
    getOrCreateCardTemplate(modelObject, BACKWARDS_CARD_TEMPLATE_NAME,
                            BACKWARDS_CARD_TEMPLATE_QFMT, BACKWARDS_CARD_TEMPLATE_AFMT, CARD_TEMPLATE_CSS, add=False)


def deleteBackwardsCardTemplate(modelObject, backwardsTemplateObject):
    """Delete Backwards Card Template (Card Type) from existing Dict2Anki Note Type"""
    mw.col.models.remove_template(modelObject, backwardsTemplateObject)
    mw.col.models.save(modelObject)


def checkModelFields(modelObject) -> (bool, set, set):
    """Check if model fields are as expected. :return: (ok, unknown_fields, missing_fields)"""
    current_fields = [f['name'] for f in modelObject['flds']]
    expected_fields = MODEL_FIELDS

    set_current = set(current_fields)
    set_expected = set(expected_fields)
    if set_current == set_expected:
        return True, set(), set()
    else:
        unknown_fields = set_current - set_expected
        missing_fields = set_expected - set_current
        return False, unknown_fields, missing_fields


def mergeModelFields(modelObject) -> bool:
    """Merge model fields. Only need to do updates when there are missing fields. return: updated"""
    ok, unknown_fields, missing_fields = checkModelFields(modelObject)
    if ok or (not missing_fields):
        return False
    logger.warning(f"unknown fields: {unknown_fields}")
    logger.warning(f"missing fields: {missing_fields}")
    logger.info(f"Merge model fields...")
    fields = modelObject['flds']
    # field_map = {f["name"]: (f["ord"], f) for f in fields}
    field_map = mw.col.models.field_map(modelObject)

    fields.clear()
    logger.info(f"step 1. add MODEL_FIELDS: {MODEL_FIELDS}")
    for f_name in MODEL_FIELDS:
        if f_name in field_map:
            index, field = field_map[f_name]
        else:
            field = mw.col.models.newField(f_name)
        fields.append(field)
    logger.info(f"step 2. add unknown_fields: {unknown_fields}")
    for f_name in unknown_fields:
        index, field = field_map[f_name]
        fields.append(field)
    mw.col.models.save(modelObject)
    return True


def checkModelCardTemplates(modelObject) -> bool:
    """Check if model card templates are as expected"""
    for tmpl in modelObject['tmpls']:
        tmpl_name = tmpl['name']
        logger.info(f"Found card template '{tmpl_name}'")
        if tmpl_name == NORMAL_CARD_TEMPLATE_NAME:
            if tmpl['qfmt'] != NORMAL_CARD_TEMPLATE_QFMT or tmpl['afmt'] != NORMAL_CARD_TEMPLATE_AFMT:
                logger.info(f"Changes detected in template '{tmpl_name}'")
                return False
        elif tmpl_name == BACKWARDS_CARD_TEMPLATE_NAME:
            if tmpl['qfmt'] != BACKWARDS_CARD_TEMPLATE_QFMT or tmpl['afmt'] != BACKWARDS_CARD_TEMPLATE_AFMT:
                logger.warning(f"Changes detected in template '{tmpl_name}'")
                return False
    return True


def checkModelCardCSS(modelObject) -> bool:
    """Check if model CSS are as expected"""
    current_css = modelObject['css']
    expected_css = CARD_TEMPLATE_CSS
    if current_css == expected_css:
        return True
    else:
        logger.warning(f"Changes detected in card CSS")
        return False


def resetModelCardTemplates(modelObject):
    """Reset Card Templates to default"""
    for tmpl in modelObject['tmpls']:
        tmpl_name = tmpl['name']
        if tmpl_name == NORMAL_CARD_TEMPLATE_NAME:
            logger.info(f"Reset card template '{NORMAL_CARD_TEMPLATE_NAME}'")
            tmpl['qfmt'] = NORMAL_CARD_TEMPLATE_QFMT
            tmpl['afmt'] = NORMAL_CARD_TEMPLATE_AFMT
        elif tmpl_name == BACKWARDS_CARD_TEMPLATE_NAME:
            logger.info(f"Reset card template '{BACKWARDS_CARD_TEMPLATE_NAME}'")
            tmpl['qfmt'] = BACKWARDS_CARD_TEMPLATE_QFMT
            tmpl['afmt'] = BACKWARDS_CARD_TEMPLATE_AFMT
    logger.info(f"Reset CSS")
    modelObject['css'] = CARD_TEMPLATE_CSS
    logger.info(f"Save changes")
    mw.col.models.save(modelObject)


def addNoteToDeck(deck, model, config: dict, word: dict, whichPron: str):
    """
    Add note
    :param deck: deck
    :param model: model
    :param config: currentConfig
    :param word: (dict) query result of a word
    :return: None
    """
    if not word:
        logger.warning(f'查询结果{word} 异常，忽略')
        return
    model['did'] = deck['id']

    # create new note
    note = anki.notes.Note(mw.col, model)
    term = word['term']
    note['term'] = term

    # ================================== Required fields ==================================
    # 1. Required fields are always included in Anki cards and cannot be toggled off
    # 2. Always add to note if it has a value

    # group (bookName)
    if word['bookName']:
        note['group'] = word['bookName']

    # modifiedTime
    if word['modifiedTime']:    # int
        note['modifiedTime'] = str(word['modifiedTime'])

    # exam_type
    if word['exam_type']:       # [str]
        note['exam_type'] = str(word['exam_type'])

    # phonetic
    if word['BrEPhonetic']:
        note['uk'] = word['BrEPhonetic']
    if word['AmEPhonetic']:
        note['us'] = word['AmEPhonetic']

    # definition
    definitions = []
    if config['briefDefinition'] and word['definition_brief']:   # prefer brief definition
        definitions.append(word['definition_brief'])    # str

    if (not definitions) and word['definition']:
        definitions.extend(word['definition'])          # [str]

    if definitions:
        note['definition'] = '<br>\n'.join(definitions)
    else:
        logger.warning(f"NO DEFINITION FOR WORD {word['term']}!!!")

    # ================================== Optional fields ==================================
    # 1. Ignore "query settings"
    # 2. Always add to note if it has a value
    # 3. Toggle visibility by dynamically updating card template

    # definition_en
    if config['definition_en'] and word['definition_en']:
        note['definition_en'] = '<br>\n'.join(word['definition_en'])

    # image
    if word['image']:
        imageFilename = default_image_filename(term)
        note['image'] = f'<div><img src="{imageFilename}" /></div>'

    # pronunciation
    if whichPron and word[whichPron]:
        pronFilename = default_audio_filename(term)
        note['pronunciation'] = f"[sound:{pronFilename}]"

    # phrase
    if word['phrase']:
        for i, phrase_tuple in enumerate(word['phrase'][:3]):       # at most 3 phrases
            note[f'phrase{i}'], note[f'phrase_explain{i}'] = phrase_tuple
            note[f'pplaceHolder{i}'] = "Tap To View"

    # sentence
    if word['sentence']:
        for i, sentence_tuple in enumerate(word['sentence'][:3]):   # at most 3 sentences
            note[f'sentence{i}'], note[f'sentence_explain{i}'] = sentence_tuple
            note[f'splaceHolder{i}'] = "Tap To View"

    mw.col.addNote(note)
    mw.col.reset()
    logger.info(f"添加笔记{note['term']}")
