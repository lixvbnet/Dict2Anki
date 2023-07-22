import os
import re
from bs4 import BeautifulSoup


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
    with open(filename, 'r') as f:
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
