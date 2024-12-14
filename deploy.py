import argparse
import os
import zipfile

from bs4 import BeautifulSoup
from requests.sessions import Session
from zipfile import ZipFile
from addon.constants import WINDOW_TITLE

TARGET_DIR = '.'
TARGET_FILENAME = f'{WINDOW_TITLE}.zip'


def create_zip(target_dir=TARGET_DIR, target_filename=TARGET_FILENAME):
    file_paths = []
    exclude_dirs = ['build', '_image', 'test', 'test_addon', 'testapi', '__pycache__', '.git', '.idea', '.pytest_cache', 'screenshots', 'venv']
    exclude_files = ['README.md', 'SUPPORT.md', 'Makefile', 'Makefile.bat', 'apitest.py', 'constants_tests.py', 'words.txt', 'NOTE.txt',
                     'test.py', 'testqt.py', 'apitest_eudict.py', 'apitest_youdao.py', 'FixQtEnums.py',
                     '.gitignore', '.travis.yml', 'deploy.py', 'requirements.txt', '.DS_Store', 'meta.json']
    exclude_ext = ['.png', '.ui', '.qrc', '.log', '.zip', '.tpl', '.sh']
    for dirname, sub_dirs, files in os.walk("."):
        for d in exclude_dirs:
            if d in sub_dirs:
                sub_dirs.remove(d)
        for f in exclude_files:
            if f in files:
                files.remove(f)
        for ext in exclude_ext:
            for f in files[:]:
                if f.endswith(ext):
                    files.remove(f)
        for filename in files:
            file_paths.append(os.path.join(dirname, filename))

    if not os.path.exists(target_dir):
        os.mkdir(target_dir)
    filepath = os.path.join(target_dir, target_filename)
    with ZipFile(filepath, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
        for file in file_paths:
            zf.write(file)
    print(f"File [{filepath}] saved.")


def publish(zip_dir, zip_filename, title, tags, desc):
    """TODO"""
    username = os.environ.get('ANKI_USERNAME')
    password = os.environ.get('ANKI_PASSWORD')
    addon_id = os.environ.get('ANKI_ADDON_ID')

    if not username:
        username = input("Anki username: ")
    if not addon_id:
        addon_id = input("Anki addon ID: ")

    print("username:", username)
    print("addon_id:", addon_id)

    if not password:
        password = input("Anki password: ")

    s = Session()
    URL = 'https://ankiweb.net/account/login'
    rsp = s.get(URL)
    soup = BeautifulSoup(rsp.text, features="html.parser")
    csrf_token = soup.find('input', {'name': 'csrf_token'}).get('value')
    s.post(URL, data={'submit': 1, 'csrf_token': csrf_token, 'username': username, 'password': password})

    URL = 'https://ankiweb.net/shared/upload'
    filepath = os.path.join(zip_dir, zip_filename)
    file = {'v21file': open(filepath, 'rb')}
    rsp = s.post(URL, files=file, data={
        'title': title,
        'tags': tags,
        'desc': desc,
        'id': addon_id,
        'submit': 'Update',
        'v21file': file,
        'v20file': '',
    })
    s.close()
    if rsp.url == f'https://ankiweb.net/shared/info/{addon_id}':
        return True
    else:
        return False


if __name__ == '__main__':
    OPERATIONS = ["build", "publish"]
    parser = argparse.ArgumentParser()
    parser.add_argument("operation", type=str, choices=OPERATIONS, help="cluster name")
    parser.add_argument("-d", "--dir", type=str, help="target directory")
    args = parser.parse_args()

    operation = args.operation
    directory = args.dir
    if not directory:
        directory = TARGET_DIR

    # print(operation, directory)
    print(f"operation: {operation}")
    print(f"directory: {directory}")

    if operation == "build":
        create_zip(target_dir=directory)
    elif operation == "publish":
        raise RuntimeError(f"Operation '{operation}' is not implemented yet")
    else:
        raise RuntimeError(f"Unsupported operation: {operation}")
