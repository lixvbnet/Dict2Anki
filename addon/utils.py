import os
import re
from pathlib import Path

from bs4 import BeautifulSoup


def set_sub_ignore_case(a, b: set) -> set:
    b_lower = {v.lower() for v in b}
    return {v for v in a if v.lower() not in b_lower}


def get_image(fieldValue: str) -> str:
    if not fieldValue: return ""
    soup = BeautifulSoup(fieldValue, features="html.parser")
    result = []
    for img in soup.find_all('img', src=True):
        result.append(img['src'])
    return result[0] if result else ""


def get_audio(fieldValue: str) -> str:
    if not fieldValue: return ""
    matches = re.findall(r'\[sound:(.+)]', fieldValue)
    return matches[0] if matches else ""


def is_image_file_missing(fieldValue: str, media_dir: str) -> bool:
    return is_media_file_missing(fieldValue, media_dir, get_image)


def is_audio_file_missing(fieldValue: str, media_dir: str) -> bool:
    return is_media_file_missing(fieldValue, media_dir, get_audio)


def is_media_file_missing(fieldValue: str, media_dir: str, f_get) -> bool:
    filename = f_get(fieldValue)
    if not fieldValue or not filename:
        return False
    filepath = os.path.join(media_dir, filename)
    return not os.path.exists(filepath)


def read_words_from_file(filename: str) -> [[str]]:
    lines = []
    with open(filename, 'r', encoding='utf8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            lines.append(line)
    word_list = []
    for line in lines:
        fields = [re.sub(r'\s+', ' ', f.strip()) for f in re.split(r'\t+', line)]
        word_list.append(fields)
    return word_list


if __name__ == '__main__':
    words_file = 'words.txt'
    # homedir = str(Path.home())
    # words_file = homedir+'/words2中文文件名.txt'
    wordlist = read_words_from_file(words_file)
    print(wordlist)

    # images = [
    #     '<div><img src="MG-chloride.jpg"></div>',
    #     '<img src="OPD_10percent.jpg">',
    #     '<img>',
    #     '',
    #     None,
    # ]
    # for image in images:
    #     print(get_image(image))
    #
    # print("---------------------------------")
    #
    # audios = [
    #     '[sound:MG-chloride.mp3]',
    #     '[sound:OPD_10percent.mp3]',
    #     '[sound:]',
    #     '',
    #     None
    # ]
    # for audio in audios:
    #     print(get_audio(audio))

    # s1 = {'aa', 'bb', 'Cc'}
    # s2 = {'AA', 'Bb', 'dd', 'eE'}
    #
    # print("s1=", s1)
    # print("s2=", s2)
    # print("----------------")
    # print("s1-s2", s1-s2)
    # print("s2-s1", s2-s1)
    # print("----------------")
    #
    # s = set_sub_ignore_case(s1, s2)
    # print("s1-s2 ignore case:", s)
    # s = set_sub_ignore_case(s2, s1)
    # print("s2-s1 ignore case:", s)
