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


def getOrCreateNormalCardTemplate(modelObject, fg: FieldGroup):
    """Create Normal Card Template (Card Type)"""
    qfmt = normal_card_template_qfmt(fg)
    afmt = normal_card_template_afmt(fg)
    getOrCreateCardTemplate(modelObject, NORMAL_CARD_TEMPLATE_NAME,
                            qfmt, afmt, CARD_TEMPLATE_CSS, add=True)


def getOrCreateBackwardsCardTemplate(modelObject, fg: FieldGroup):
    """Create Backwards Card Template (Card Type) to existing Dict2Anki Note Type"""
    qfmt = backwards_card_template_qfmt(fg)
    afmt = backwards_card_template_afmt(fg)
    getOrCreateCardTemplate(modelObject, BACKWARDS_CARD_TEMPLATE_NAME,
                            qfmt, afmt, CARD_TEMPLATE_CSS, add=False)


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


def checkModelCardTemplates(modelObject, fg) -> bool:
    """Check if model card templates are as expected"""
    for tmpl in modelObject['tmpls']:
        tmpl_name = tmpl['name']
        logger.info(f"Found card template '{tmpl_name}'")
        if tmpl_name == NORMAL_CARD_TEMPLATE_NAME:
            if tmpl['qfmt'] != normal_card_template_qfmt(fg) or tmpl['afmt'] != normal_card_template_afmt(fg):
                logger.info(f"Changes detected in template '{tmpl_name}'")
                return False
        elif tmpl_name == BACKWARDS_CARD_TEMPLATE_NAME:
            if tmpl['qfmt'] != backwards_card_template_qfmt(fg) or tmpl['afmt'] != backwards_card_template_afmt(fg):
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


def resetModelCardTemplates(modelObject, fg):
    """Reset Card Templates to default"""
    for tmpl in modelObject['tmpls']:
        tmpl_name = tmpl['name']
        if tmpl_name == NORMAL_CARD_TEMPLATE_NAME:
            logger.info(f"Reset card template '{NORMAL_CARD_TEMPLATE_NAME}'")
            tmpl['qfmt'] = normal_card_template_qfmt(fg)
            tmpl['afmt'] = normal_card_template_afmt(fg)
        elif tmpl_name == BACKWARDS_CARD_TEMPLATE_NAME:
            logger.info(f"Reset card template '{BACKWARDS_CARD_TEMPLATE_NAME}'")
            tmpl['qfmt'] = backwards_card_template_qfmt(fg)
            tmpl['afmt'] = backwards_card_template_afmt(fg)
    logger.info(f"Reset CSS")
    modelObject['css'] = CARD_TEMPLATE_CSS
    logger.info(f"Save changes")
    mw.col.models.save(modelObject)


def setNoteFieldValue(note, key: str, value: str, isNewNote: bool, overwrite: bool) -> bool:
    """set note field value. :return isWritten"""
    if not value:
        return False
    if isNewNote or overwrite:
        note[key] = value
        return True
    if not note[key]:   # field value of the Existing Note is missing
        note[key] = value
        return True
    return False


def addNoteToDeck(deck, model, config: dict, word: dict, whichPron: str, existing_note=None, overwrite=False):
    """
    Add note
    :param deck: deck
    :param model: model
    :param config: currentConfig
    :param word: (dict) query result of a word
    :param whichPron:
    :param existing_note: if not None, then do not create new note
    :param overwrite: True to overwrite existing note, and False to fill missing values only. (Only relevant when
                        'existing_note' is not None.
    :return: None
    """
    if not word:
        logger.warning(f'查询结果{word} 异常，忽略')
        return

    isNewNote = (existing_note is None)
    if isNewNote:
        model['did'] = deck['id']
        note = anki.notes.Note(mw.col, model)   # create new note
    else:
        note = existing_note                    # existing note

    term = word['term']
    setNoteFieldValue(note, 'term', term, isNewNote, overwrite)
    # note['term'] = term

    # ================================== Required fields ==================================
    # 1. Required fields are always included in Anki cards and cannot be toggled off
    # 2. Always add to note if it has a value

    # group (bookName)
    if word['bookName']:
        key, value = 'group', word['bookName']
        setNoteFieldValue(note, key, value, isNewNote, overwrite)
        # note['group'] = word['bookName']

    # exam_type
    if word['exam_type']:       # [str]
        key, value = 'exam_type', " / ".join(word['exam_type'])
        setNoteFieldValue(note, key, value, isNewNote, overwrite)
        # note['exam_type'] = " / ".join(word['exam_type'])

    # modifiedTime
    if word['modifiedTime']:    # int
        key, value = 'modifiedTime', str(word['modifiedTime'])
        setNoteFieldValue(note, key, value, isNewNote, overwrite)
        # note['modifiedTime'] = str(word['modifiedTime'])

    # phonetic
    if word['BrEPhonetic']:
        key, value = 'uk', word['BrEPhonetic']
        setNoteFieldValue(note, key, value, isNewNote, overwrite)
        # note['uk'] = word['BrEPhonetic']
    if word['AmEPhonetic']:
        key, value = 'us', word['AmEPhonetic']
        setNoteFieldValue(note, key, value, isNewNote, overwrite)
        # note['us'] = word['AmEPhonetic']

    # definition
    definitions = []
    if not word['definition_brief'] and not word['definition']:         # both empty
        logger.warning(f"NO DEFINITION FOR WORD {word['term']}!!!")
    elif word['definition_brief'] and word['definition']:               # both non-empty
        definitions = [word['definition_brief']] if config['briefDefinition'] else word['definition']
    else:                                                               # one is empty and the other is non-empty
        definitions = [word['definition_brief']] if word['definition_brief'] else word['definition']

    key, value = 'definition', '<br>\n'.join(definitions)
    setNoteFieldValue(note, key, value, isNewNote, overwrite)
    # note['definition'] = '<br>\n'.join(definitions)

    # ================================== Optional fields ==================================
    # 1. Ignore "query settings"
    # 2. Always add to note if it has a value
    # 3. Toggle visibility by dynamically updating card template

    # definition_en
    if word['definition_en']:
        key, value = 'definition_en', '<br>\n'.join(word['definition_en'])
        setNoteFieldValue(note, key, value, isNewNote, overwrite)
        # note['definition_en'] = '<br>\n'.join(word['definition_en'])

    # image
    if word['image']:
        imageFilename = default_image_filename(term)
        key, value = 'image', f'<div><img src="{imageFilename}" /></div>'
        setNoteFieldValue(note, key, value, isNewNote, overwrite)
        # note['image'] = f'<div><img src="{imageFilename}" /></div>'

    # pronunciation
    if whichPron and whichPron != 'noPron' and word[whichPron]:
        pronFilename = default_audio_filename(term)
        key, value = 'pronunciation', f"[sound:{pronFilename}]"
        setNoteFieldValue(note, key, value, isNewNote, overwrite)
        # note['pronunciation'] = f"[sound:{pronFilename}]"

    # phrase
    if word['phrase']:
        for i, phrase_tuple in enumerate(word['phrase'][:3]):       # at most 3 phrases
            key, value = f'phrase{i}', phrase_tuple[0]
            setNoteFieldValue(note, key, value, isNewNote, overwrite)
            key, value = f'phrase_explain{i}', phrase_tuple[1]
            setNoteFieldValue(note, key, value, isNewNote, overwrite)
            key, value = f'pplaceHolder{i}', "Tap To View"
            setNoteFieldValue(note, key, value, isNewNote, overwrite)
            # note[f'phrase{i}'], note[f'phrase_explain{i}'] = phrase_tuple
            # note[f'pplaceHolder{i}'] = "Tap To View"

    # sentence
    if word['sentence']:
        for i, sentence_tuple in enumerate(word['sentence'][:3]):   # at most 3 sentences
            s_overwrite = overwrite
            # Sentence may have changed over time.
            # To avoid sentence-speech mismatch, overwrite sentence info if sentence_speech is missing.
            # Also overwrite sentence info if term is not highlighted.
            if not note[f'sentence_speech{i}'] or f"<b>{term}</b>" not in note[f'sentence{i}']:
                s_overwrite = True

            key, value = f'sentence{i}', sentence_tuple[0]
            setNoteFieldValue(note, key, value, isNewNote, s_overwrite)
            key, value = f'sentence_explain{i}', sentence_tuple[1]
            setNoteFieldValue(note, key, value, isNewNote, s_overwrite)
            key, value = f'splaceHolder{i}', "Tap To View"
            setNoteFieldValue(note, key, value, isNewNote, s_overwrite)
            key, value = f'sentence_speech{i}', sentence_tuple[2]
            setNoteFieldValue(note, key, value, isNewNote, s_overwrite)
            # note[f'sentence{i}'], note[f'sentence_explain{i}'] = sentence_tuple
            # note[f'splaceHolder{i}'] = "Tap To View"

    if isNewNote:
        mw.col.addNote(note)
        logger.info(f"添加笔记{term}")
    else:
        mw.col.update_note(note)
        logger.info(f"更新笔记{term}")
    mw.col.reset()
