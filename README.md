# Dict2Anki (Fork)

This is a fork of Dict2Anki.

注：当前为Fork版本，根据我的个人喜好做了一些修改。原插件地址: https://ankiweb.net/shared/info/1284759083



本fork所做的修改：

* 默认不删除Anki卡片
* 仍然使用旧版Note type，兼容以前同步的数据
* 添加重置按钮，用来重置插件（清空同步记录）
* 添加其他工具：
  * Download Missing Assets
  * Export Audio (macOS only)
  * Add/Delete Backward Template

- Other minor fixes or improvements



> Q：什么时候会用到重置按钮？
>
> A：比如你同步了单词之后，在Anki上背词的过程中删除了一些已经背会的单词，正常情况下再次进行同步时是不会重新添加这些单词的，因为同步时会把上次同步过的词都过滤掉。但如果这些词是误删的，想在下次同步时重新同步过来，就可以重置插件，然后同步即可。



当前fork源码：https://github.com/lixvbnet/Dict2Anki 