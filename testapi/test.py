# A simple manual test
import json
import os
from Dict2Anki.addon.dictionary.youdao import Youdao
from Dict2Anki.addon.misc import SimpleWord
from Dict2Anki.addon.queryApi.youdao import API


BASE_DIR = "../Dict2Anki"


def youdao_get_words() -> [SimpleWord]:
    # 1. run `make install`
    # 2. open Anki, Dict2Anki, and login Youdao
    # 3. Anki will generate the `meta.json` file, which contains the user config, including cookie
    with open(BASE_DIR+'/meta.json', 'r') as f:
        meta = json.load(f)

    cookie = json.loads(meta['config']['credential'][0]['cookie'])  # 0: Youdao
    print(cookie)

    yd = Youdao()
    print("=================== check cookie ===================")
    valid = yd.checkCookie(cookie)
    if valid:
        print("Cookie is valid")
    else:
        print("Cookie is NOT valid")
        exit(1)

    print("==================== get groups ====================")
    groups = yd.getGroups()
    print(f"{groups} \t size={len(groups)}")

    words = []
    group = groups[0]   # here just try first group
    group_name, group_id = group
    print(f"====== get all words in group [{group_name}] ======")
    page_count = yd.getTotalPage(group_name, group_id)
    print(f"page_count={page_count}")
    for pageNo in range(page_count):
        # print(f"--- page {pageNo} ---")
        words_in_page = yd.getWordsByPage(pageNo, group_name, group_id)
        # print(f"{len(words_in_page)} words: {words_in_page}")
        words.extend(words_in_page)
    print(f"Total: {len(words)} words: {words}")
    return words


def youdao_test():
    words = youdao_get_words()
    # word = words[len(words)-1]   # here just query last word
    word = None
    for w in words:
        if w.term == 'hype':
            word = w

    if word is None:
        print(f"Error: word not found!")
        return

    print(f"================ Query word {word} ================")
    print(word.toString())
    print('------------------------')
    result = API.query(word)
    print(json.dumps(result, ensure_ascii=False))

    print(f"definition_short: \t {result['definition_short']}")
    print(f"definition: \t\t {result['definition']} (size={len(result['definition'])})")
    print(f"definition_en: \t\t {result['definition_en']} (size={len(result['definition_en'])})")
    print(f"phrase: \t\t\t {result['phrase']} (size={len(result['phrase'])})")
    print(f"sentence: \t\t\t {result['sentence']} (size={len(result['sentence'])})")


print(os.getcwd())
youdao_test()
