## 单词查询 API 模块

## Development Guide
可在该模块下添加自定义查询API，继承 `misc.AbstractQueryAPI`确保API能和插件兼容
之后将你的API 添加到当前目录`__init.py` 中的 `apis` 列表中以便插件读取，并且查询返回结果满足
```python
{
    'term': str,
    'bookId': str,
    'bookName': str,
    'modifiedTime': int,
    'definition_brief': str,
    'definition': [str],
    'definition_en': [str],
    'phrase': [(str,str)],
    'sentence': [(str,str)],
    'image': str,
    'BrEPhonetic': str,
    'AmEPhonetic': str,
    'BrEPron': str,
    'AmEPron': str,
    'exam_type': [str],
}

```
