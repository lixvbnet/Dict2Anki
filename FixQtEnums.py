# This script comes from https://stackoverflow.com/a/72658216
# -*- coding: utf-8 -*-
# ================================================================================================ #
#                                       ENUM CONVERTER TOOL                                        #
# ================================================================================================ #

from typing import *
import os, argparse, inspect, re
q = "'"

help_text = '''
Copyright (c) 2022 Kristof Mulier
MIT licensed, see bottom

ENUM CONVERTER TOOL
===================
The script starts from the toplevel directory (assuming that you put this file in that directory)
and crawls through all the files and folders. In each file, it searches for old-style enums to
convert them into fully qualified names.

HOW TO USE
==========
Fill in the path to your PyQt6 installation folder. See line 57:

    pyqt6_folderpath = 'C:/Python39/Lib/site-packages/PyQt6'

Place this script in the toplevel directory of your project. Open a terminal, navigate to the
directory and invoke this script:

    $ python enum_converter_tool.py
    
WARNING
=======
This script modifies the files in your project! Make sure to backup your project before you put this
file inside. Also, you might first want to do a dry run:

    $ python enum_converter_tool.py --dry_run
    
FEATURES
========
You can invoke this script in the following ways:

    $ python enum_converter_tool.py                   No parameters. The script simply goes through
                                                      all the files and makes the replacements.
                                                      
    $ python enum_converter_tool.py --dry_run         Dry run mode. The script won't do any replace-
                                                      ments, but prints out what it could replace.
                                                      
    $ python enum_converter_tool.py --show            Print the dictionary this script creates to
                                                      convert the old-style enums into new-style.
                                                      
    $ python enum_converter_tool.py --help            Show this help info

'''

# IMPORTANT: Point at the folder where PyQt6 stub files are located. This folder will be examined to
# fill the 'enum_dict'.
# pyqt6_folderpath = 'C:/Python39/Lib/site-packages/PyQt6'
# EDIT: @Myridium suggested another way to fill this 'pyqt6_folderpath'
# variable:
try:
    import PyQt6
except Exception:
    print("[ERROR] Unable to import PyQt6. [SKIP]")
    exit(0)

pyqt6_folderpath = PyQt6.__path__[0]

# Figure out where the toplevel directory is located. We assume that this converter tool is located
# in that directory. An os.walk() operation starts from this toplevel directory to find and process
# all files.
toplevel_directory = os.path.realpath(
    os.path.dirname(
        os.path.realpath(
            inspect.getfile(
                inspect.currentframe()
            )
        )
    )
).replace('\\', '/')

# Figure out the name of this script. It will be used later on to exclude oneself from the replace-
# ments.
script_name = os.path.realpath(
    inspect.getfile(inspect.currentframe())
).replace('\\', '/').split('/')[-1]

# Create the dictionary that will be filled with enums
enum_dict:Dict[str, str] = {}

def fill_enum_dict(filepath:str) -> None:
    '''
    Parse the given stub file to extract the enums and flags. Each one is inside a class, possibly a
    nested one. For example:

               ---------------------------------------------------------------------
               | class Qt(PyQt6.sip.simplewrapper):                                |
               |     class HighDpiScaleFactorRoundingPolicy(enum.Enum):            |
               |         Round = ... # type: Qt.HighDpiScaleFactorRoundingPolicy   |
               ---------------------------------------------------------------------

    The enum 'Round' is from class 'HighDpiScaleFactorRoundingPolicy' which is in turn from class
    'Qt'. The old reference style would then be:
        > Qt.Round

    The new style (fully qualified name) would be:
        > Qt.HighDpiScaleFactorRoundingPolicy.Round

    The aim of this function is to fill the 'enum_dict' with an entry like:
    enum_dict = {
        'Qt.Round' : 'Qt.HighDpiScaleFactorRoundingPolicy.Round'
    }
    '''
    content:str = ''
    with open(filepath, 'r', encoding='utf-8', newline='\n', errors='replace') as f:
        content = f.read()

    p = re.compile(r'(\w+)\s+=\s+\.\.\.\s+#\s*type:\s*([\w.]+)')
    for m in p.finditer(content):
        # Observe the enum's name, eg. 'Round'
        enum_name = m.group(1)

        # Figure out in which classes it is
        class_list = m.group(2).split('.')

        # If it belongs to just one class (no nesting), there is no point in continuing
        if len(class_list) == 1:
            continue

        # Extract the old and new enum's name
        old_enum = f'{class_list[0]}.{enum_name}'
        new_enum = ''
        for class_name in class_list:
            new_enum += f'{class_name}.'
            continue
        new_enum += enum_name

        # Add them to the 'enum_dict'
        enum_dict[old_enum] = new_enum
        continue
    return

def show_help() -> None:
    '''
    Print help info and quit.
    '''
    print(help_text)
    return

def convert_enums_in_file(filepath:str, dry_run:bool) -> None:
    '''
    Convert the enums in the given file.
    '''
    filename:str = filepath.split('/')[-1]

    # Ignore the file in some cases
    if any(filename == fname for fname in (script_name, )):
        return

    # Read the content
    content:str = ''
    with open(filepath, 'r', encoding='utf-8', newline='\n', errors='replace') as f:
        content = f.read()

    # Loop over all the keys in the 'enum_dict'. Perform a replacement in the 'content' for each of
    # them.
    for k, v in enum_dict.items():
        if k not in content:
            continue
        # Compile a regex pattern that only looks for the old enum (represented by the key of the
        # 'enum_dict') if it is surrounded by bounds. What we want to avoid is a situation like
        # this:
        #     k = 'Qt.Window'
        #     k found in 'qt.Qt.WindowType.Window'
        # In the situation above, k is found in 'qt.Qt.WindowType.Window' such that a replacement
        # will take place there, messing up the code! By surrounding k with bounds in the regex pat-
        # tern, this won't happen.
        p = re.compile(fr'\b{k}\b')

        # Substitute all occurences of k (key) in 'content' with v (value). The 'subn()' method re-
        # turns a tuple (new_string, number_of_subs_made).
        new_content, n = p.subn(v, content)
        if n == 0:
            assert new_content == content
            continue
        assert new_content != content
        print(f'{q}{filename}{q}: Replace {q}{k}{q} => {q}{v}{q} ({n})')
        content = new_content
        continue

    if dry_run:
        return

    with open(filepath, 'w', encoding='utf-8', newline='\n', errors='replace') as f:
        f.write(content)
    return

def convert_all(dry_run:bool) -> None:
    '''
    Search and replace all enums.
    '''
    for root, dirs, files in os.walk(toplevel_directory):
        for f in files:
            if not f.endswith('.py'):
                continue
            filepath = os.path.join(root, f).replace('\\', '/')
            convert_enums_in_file(filepath, dry_run)
            continue
        continue
    return

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description = 'Convert enums to fully-qualified names',
        add_help    = False,
    )
    parser.add_argument('-h', '--help'    , action='store_true')
    parser.add_argument('-d', '--dry_run' , action='store_true')
    parser.add_argument('-s', '--show'    , action='store_true')
    args = parser.parse_args()
    if args.help:
        show_help()
    else:
        #& Check if 'pyqt6_folderpath' exists
        if not os.path.exists(pyqt6_folderpath):
            print(
                f'\nERROR:\n'
                f'Folder {q}{pyqt6_folderpath}{q} could not be found. Make sure that variable '
                f'{q}pyqt6_folderpath{q} from line 57 points to the PyQt6 installation folder.\n'
            )
        else:
            #& Fill the 'enum_dict'
            type_hint_files = [
                os.path.join(pyqt6_folderpath, _filename)
                for _filename in os.listdir(pyqt6_folderpath)
                if _filename.endswith('.pyi')
            ]
            for _filepath in type_hint_files:
                fill_enum_dict(_filepath)
                continue

            #& Perform requested action
            if args.show:
                import pprint
                pprint.pprint(enum_dict)
            elif args.dry_run:
                print('\nDRY RUN\n')
                convert_all(dry_run=True)
            else:
                convert_all(dry_run=False)
    # print('\nQuit enum converter tool\n')


# MIT LICENSE
# ===========
# Copyright (c) 2022 Kristof Mulier
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and
# associated documentation files (the "Software"), to deal in the Software without restriction, in-
# cluding without limitation the rights to use, copy, modify, merge, publish, distribute, sublicen-
# se, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to
# do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substan-
# tial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT
# NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRIN-
# GEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR
# OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
