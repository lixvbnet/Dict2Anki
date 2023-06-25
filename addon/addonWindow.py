import os
import sys
import logging
import json
from copy import deepcopy
from tempfile import gettempdir

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QPlainTextEdit, QDialog, QListWidgetItem, QVBoxLayout, QPushButton
from PyQt5.QtCore import pyqtSlot, QThread, Qt

from .queryApi import apis
from .UIForm import wordGroup, mainUI, icons_rc
from .workers import LoginStateCheckWorker, VersionCheckWorker, RemoteWordFetchingWorker, QueryWorker, AssetDownloadWorker
from .dictionary import dictionaries
from .logger import Handler
from .loginDialog import LoginDialog
from .misc import Mask, SimpleWord
from .constants import *

try:
    from aqt import mw
    from aqt.utils import askUser, showCritical, showInfo, tooltip, openLink
    from .noteManager import getOrCreateDeck, getDeckList, getOrCreateModel, getOrCreateModelCardTemplate, \
    getOrCreateBackwardsCardTemplate, addNoteToDeck, getWordsByDeck, getNotes, deleteBackwardsCardTemplate
except ImportError:
    from test.dummy_aqt import mw, askUser, showCritical, showInfo, tooltip, openLink
    from test.dummy_noteManager import getOrCreateDeck, getDeckList, getOrCreateModel, getOrCreateModelCardTemplate, addNoteToDeck, getWordsByDeck, getNotes

logger = logging.getLogger('dict2Anki')


def fatal_error(exc_type, exc_value, exc_traceback):
    logger.exception(exc_value, exc_info=(exc_type, exc_value, exc_traceback))


# 未知异常日志
sys.excepthook = fatal_error


class Windows(QDialog, mainUI.Ui_Dialog):
    isRunning = False

    def __init__(self, parent=None):
        super(Windows, self).__init__(parent)
        self.selectedDict = None
        self.currentConfig = dict()
        self.localWords: [str] = []
        self.remoteWordsDict: {str: SimpleWord} = {}
        self.selectedGroups = [list()] * len(dictionaries)

        self.workerThread = QThread(self)
        self.workerThread.start()
        self.updateCheckThead = QThread(self)
        self.updateCheckThead.start()
        self.assetDownloadThread = QThread(self)

        self.updateCheckWork = None
        self.loginWorker = None
        self.queryWorker = None
        self.pullWorker = None
        self.assetDownloadWorker = None

        self.setupUi(self)
        self.setWindowTitle(WINDOW_TITLE)
        self.setupLogger()
        self.initCore()
        # self.checkUpdate()    # 会导致卡顿
        # self.__dev() # 以备调试时使用

    def __dev(self):
        def on_dev():
            logger.debug('whatever')

        self.devBtn = QPushButton('Magic Button', self.mainTab)
        self.devBtn.clicked.connect(on_dev)
        self.gridLayout_4.addWidget(self.devBtn, 4, 3, 1, 1)

    def closeEvent(self, event):
        # 插件关闭时退出所有线程
        if self.workerThread.isRunning():
            self.workerThread.requestInterruption()
            self.workerThread.quit()
            self.workerThread.wait()

        if self.updateCheckThead.isRunning():
            self.updateCheckThead.quit()
            self.updateCheckThead.wait()

        if self.assetDownloadThread.isRunning():
            self.assetDownloadThread.requestInterruption()
            self.workerThread.quit()
            self.workerThread.wait()

        event.accept()

    def on_NewLogRecord(self, text):
        # append to log box, and scroll to bottom
        self.logTextBox.appendPlainText(text)
        self.logTextBox.verticalScrollBar().setValue(self.logTextBox.verticalScrollBar().maximum())

    def setupLogger(self):
        """初始化 Logger """

        def onDestroyed():
            logger.removeHandler(QtHandler)

        # 防止 debug 信息写入stdout/stderr 导致 Anki 崩溃
        logFile = os.path.join(gettempdir(), 'dict2anki.log')
        logging.basicConfig(handlers=[logging.FileHandler(logFile, 'w', 'utf-8')], level=logging.DEBUG, format='[%(asctime)s][%(levelname)8s] -- %(message)s - (%(name)s)')

        QtHandler = Handler(self)
        logger.addHandler(QtHandler)
        # QtHandler.newRecord.connect(self.logTextBox.appendPlainText)
        QtHandler.newRecord.connect(self.on_NewLogRecord)

        # 日志Widget销毁时移除 Handlers
        self.logTextBox.destroyed.connect(onDestroyed)

    def setupGUIByConfig(self):
        config = mw.addonManager.getConfig(__name__)
        # logger.info(f"config name: {__name__}")
        # logger.info(f"config: {json.dumps(config)}")

        # basic settings
        self.deckComboBox.setCurrentText(config['deck'])
        self.dictionaryComboBox.setCurrentIndex(config['selectedDict'])
        self.apiComboBox.setCurrentIndex(config['selectedApi'])
        if config['selectedGroup']:
            self.selectedGroups = config['selectedGroup']
        else:
            self.selectedGroups = [list()] * len(dictionaries)

        # account settings
        selectedDictCredential = config['credential'][config['selectedDict']]
        self.usernameLineEdit.setText(selectedDictCredential['username'])
        self.passwordLineEdit.setText(selectedDictCredential['password'])
        self.cookieLineEdit.setText(selectedDictCredential['cookie'])

        # query settings
        self.briefDefinitionCheckBox.setChecked(config['briefDefinition'])
        self.enDefinitionCheckBox.setChecked(config['enDefinition'])
        self.noPronRadioButton.setChecked(config['noPron'])
        self.BrEPronRadioButton.setChecked(config['BrEPron'])
        self.AmEPronRadioButton.setChecked(config['AmEPron'])

        # card settings
        self.imageCheckBox.setChecked(config['image'])
        self.pronunciationCheckBox.setChecked(config['pronunciation'])
        self.phraseCheckBox.setChecked(config['phrase'])
        self.sentenceCheckBox.setChecked(config['sentence'])

    def initCore(self):
        self.usernameLineEdit.hide()
        self.usernameLabel.hide()
        self.passwordLabel.hide()
        self.passwordLineEdit.hide()
        self.dictionaryComboBox.addItems([d.name for d in dictionaries])
        self.apiComboBox.addItems([d.name for d in apis])
        self.deckComboBox.addItems(getDeckList())
        self.setupGUIByConfig()

    def getAndSaveCurrentConfig(self) -> dict:
        """获取当前设置"""
        currentConfig = dict(
            # basic settings
            deck=self.deckComboBox.currentText(),
            selectedDict=self.dictionaryComboBox.currentIndex(),
            selectedApi=self.apiComboBox.currentIndex(),
            selectedGroup=self.selectedGroups,

            # account settings
            username=self.usernameLineEdit.text(),
            password=Mask(self.passwordLineEdit.text()),
            cookie=Mask(self.cookieLineEdit.text()),

            # query settings
            briefDefinition=self.briefDefinitionCheckBox.isChecked(),
            enDefinition=self.enDefinitionCheckBox.isChecked(),
            noPron=self.noPronRadioButton.isChecked(),
            BrEPron=self.BrEPronRadioButton.isChecked(),
            AmEPron=self.AmEPronRadioButton.isChecked(),

            # note settings
            image=self.imageCheckBox.isChecked(),
            pronunciation=self.pronunciationCheckBox.isChecked(),
            phrase=self.phraseCheckBox.isChecked(),
            sentence=self.sentenceCheckBox.isChecked(),
        )
        logger.info(f'当前设置:{currentConfig}')
        self._saveConfig(currentConfig)
        self.currentConfig = currentConfig
        return currentConfig

    @staticmethod
    def _saveConfig(config):
        # get the config currently stored in Anki
        oldConfig = deepcopy(mw.addonManager.getConfig(__name__))

        _config = deepcopy(config)
        selectedDict = _config['selectedDict']

        # handle credential
        _config['credential'] = oldConfig['credential']
        _config['credential'][selectedDict] = dict(
            username=_config.pop('username'),
            password=str(_config.pop('password')),
            cookie=str(_config.pop('cookie'))
        )
        maskedConfig = deepcopy(_config)
        maskedCredential = [
            dict(
                username=c['username'],
                password=Mask(c['password']),
                cookie=Mask(c['cookie'])) for c in maskedConfig['credential']
        ]
        maskedConfig['credential'] = maskedCredential
        logger.info(f'保存配置项:{maskedConfig}')
        mw.addonManager.writeConfig(__name__, _config)

    def checkUpdate(self):
        @pyqtSlot(str, str)
        def on_haveNewVersion(version, changeLog):
            if askUser(f'有新版本:{version}是否更新？\n\n{changeLog.strip()}'):
                openLink(RELEASE_URL)

        self.updateCheckWork = VersionCheckWorker()
        self.updateCheckWork.moveToThread(self.updateCheckThead)
        self.updateCheckWork.haveNewVersion.connect(on_haveNewVersion)
        self.updateCheckWork.finished.connect(self.updateCheckThead.quit)
        self.updateCheckWork.start.connect(self.updateCheckWork.run)
        self.updateCheckWork.start.emit()

    @pyqtSlot(int)
    def on_dictionaryComboBox_currentIndexChanged(self, index):
        """词典候选框改变事件"""
        self.currentDictionaryLabel.setText(f'当前选择词典: {self.dictionaryComboBox.currentText()}')
        config = mw.addonManager.getConfig(__name__)
        self.cookieLineEdit.setText(config['credential'][index]['cookie'])

    @pyqtSlot()
    def on_pullRemoteWordsBtn_clicked(self):
        """获取单词按钮点击事件"""
        if not self.deckComboBox.currentText():
            showInfo('\n请选择或输入要同步的牌组')
            return

        self.mainTab.setEnabled(False)
        self.progressBar.setValue(0)
        self.progressBar.setMaximum(0)

        currentConfig = self.getAndSaveCurrentConfig()
        self.selectedDict = dictionaries[currentConfig['selectedDict']]()

        # 登陆线程
        self.loginWorker = LoginStateCheckWorker(self.selectedDict.checkCookie, json.loads(self.cookieLineEdit.text() or '{}'))
        self.loginWorker.moveToThread(self.workerThread)
        self.loginWorker.start.connect(self.loginWorker.run)
        self.loginWorker.logSuccess.connect(self.onLogSuccess)
        self.loginWorker.logFailed.connect(self.onLoginFailed)
        self.loginWorker.start.emit()

    @pyqtSlot()
    def onLoginFailed(self):
        showCritical('第一次登录或cookie失效!请重新登录')
        self.progressBar.setValue(0)
        self.progressBar.setMaximum(1)
        self.mainTab.setEnabled(True)
        self.cookieLineEdit.clear()
        self.loginDialog = LoginDialog(
            loginUrl=self.selectedDict.loginUrl,
            loginCheckCallbackFn=self.selectedDict.loginCheckCallbackFn,
            parent=self
        )
        self.loginDialog.loginSucceed.connect(self.onLogSuccess)
        self.loginDialog.show()

    @pyqtSlot(str)
    def onLogSuccess(self, cookie):
        self.cookieLineEdit.setText(cookie)
        self.getAndSaveCurrentConfig()
        self.selectedDict.checkCookie(json.loads(cookie))
        groups = self.selectedDict.getGroups()
        if groups:
            logger.info(f"{len(groups)} group(s): {groups}")
        else:
            logger.warning(f"group is None!")

        def onAccepted(is_popup=True):
            """选择单词本弹窗确定事件"""
            # 清空 listWidget
            self.newWordListWidget.clear()
            self.needDeleteWordListWidget.clear()
            self.mainTab.setEnabled(False)

            if not is_popup:
                selectedGroups = self.selectedGroups[self.currentConfig['selectedDict']]
            else:
                selectedGroups = [group.wordGroupListWidget.item(index).text() for index in range(group.wordGroupListWidget.count()) if
                              group.wordGroupListWidget.item(index).checkState() == Qt.Checked]
            # 保存分组记录
            self.selectedGroups[self.currentConfig['selectedDict']] = selectedGroups
            self.progressBar.setValue(0)
            self.progressBar.setMaximum(1)
            logger.info(f'选中单词本{selectedGroups}')
            self.getRemoteWordList(selectedGroups)

        def onRejected():
            """选择单词本弹窗取消事件"""
            self.progressBar.setValue(0)
            self.progressBar.setMaximum(1)
            self.mainTab.setEnabled(True)

        # Avoid popup when there's only 1 group
        if len(groups) == 1:
            logger.info(f"Only 1 group. Select automatically and avoid popup.")
            group_name, group_index = groups[0]
            selectedDict = self.currentConfig['selectedDict']
            if not self.selectedGroups[selectedDict]:
                self.selectedGroups[selectedDict] = list()
            self.selectedGroups[selectedDict] = [group_name]
            onAccepted(is_popup=False)
            return

        # Otherwise, popup a dialog
        container = QDialog(self)
        group = wordGroup.Ui_Dialog()
        group.setupUi(container)
        for groupName in [str(group_name) for group_name, _ in self.selectedDict.groups]:
            item = QListWidgetItem()
            item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
            item.setText(groupName)
            item.setCheckState(Qt.Unchecked)
            group.wordGroupListWidget.addItem(item)
        # 恢复上次选择的单词本分组
        selectedDict = self.currentConfig['selectedDict']
        if not self.selectedGroups[selectedDict]:
            self.selectedGroups[selectedDict] = list()
        for groupName in self.selectedGroups[selectedDict]:
            items = group.wordGroupListWidget.findItems(groupName, Qt.MatchExactly)
            for item in items:
                item.setCheckState(Qt.Checked)
        group.buttonBox.accepted.connect(onAccepted)
        group.buttonBox.rejected.connect(onRejected)
        container.exec()

    def getRemoteWordList(self, selected_groups: [str]):
        """根据选中到分组获取分组下到全部单词，并添加到 newWordListWidget"""
        group_map = dict(self.selectedDict.groups)
        self.localWords = getWordsByDeck(self.deckComboBox.currentText())

        # 启动单词获取线程
        self.pullWorker = RemoteWordFetchingWorker(self.selectedDict, [(group_name, group_map[group_name],) for group_name in selected_groups])
        self.pullWorker.moveToThread(self.workerThread)
        self.pullWorker.start.connect(self.pullWorker.run)
        self.pullWorker.tick.connect(lambda: self.progressBar.setValue(self.progressBar.value() + 1))
        self.pullWorker.setProgress.connect(self.progressBar.setMaximum)
        self.pullWorker.doneThisGroup.connect(self.insertWordToListWidget)
        self.pullWorker.done.connect(self.on_allPullWork_done)
        self.pullWorker.start.emit()

    @pyqtSlot(list)
    def insertWordToListWidget(self, words: [SimpleWord]):
        """一个分组获取完毕事件"""
        for word in words:
            self.remoteWordsDict[word.term] = word
            wordItem = QListWidgetItem(word.term, self.newWordListWidget)
            wordItem.setData(Qt.UserRole, None)
        self.newWordListWidget.clearSelection()

    @pyqtSlot()
    def on_allPullWork_done(self):
        """全部分组获取完毕事件"""
        # termList: [str]
        localTermList = set(getWordsByDeck(self.deckComboBox.currentText()))
        remoteTermList = set([self.newWordListWidget.item(row).text() for row in range(self.newWordListWidget.count())])

        newTerms = remoteTermList - localTermList  # 新单词
        needToDeleteTerms = localTermList - remoteTermList  # 需要删除的单词
        logger.info(f'本地({len(localTermList)}): {localTermList}')
        logger.info(f'远程({len(remoteTermList)}): {remoteTermList}')
        logger.info(f'待查({len(newTerms)}): {newTerms}')
        logger.info(f'待删({len(needToDeleteTerms)}): {needToDeleteTerms}')
        waitIcon = QIcon(':/icons/wait.png')
        delIcon = QIcon(':/icons/delete.png')
        self.newWordListWidget.clear()
        self.needDeleteWordListWidget.clear()

        for term in needToDeleteTerms:
            item = QListWidgetItem(term)
            # item.setCheckState(Qt.Checked)
            item.setCheckState(Qt.Unchecked)    # Defaults to Unchecked (Avoid unintentional data loss)
            item.setIcon(delIcon)
            self.needDeleteWordListWidget.addItem(item)

        for term in newTerms:
            item = QListWidgetItem(term)
            item.setIcon(waitIcon)
            self.newWordListWidget.addItem(item)
        self.newWordListWidget.clearSelection()

        self.dictionaryComboBox.setEnabled(True)
        self.apiComboBox.setEnabled(True)
        self.deckComboBox.setEnabled(True)
        self.pullRemoteWordsBtn.setEnabled(True)
        self.queryBtn.setEnabled(self.newWordListWidget.count() > 0)
        self.btnSync.setEnabled(self.newWordListWidget.count() == 0 and self.needDeleteWordListWidget.count() > 0)
        if self.needDeleteWordListWidget.count() == self.newWordListWidget.count() == 0:
            logger.info('无需同步')
            tooltip('无需同步')
        self.mainTab.setEnabled(True)

    @pyqtSlot()
    def on_queryBtn_clicked(self):
        logger.info('点击查询按钮')
        currentConfig = self.getAndSaveCurrentConfig()
        self.queryBtn.setEnabled(False)
        self.pullRemoteWordsBtn.setEnabled(False)
        self.btnSync.setEnabled(False)

        wordList: [(SimpleWord, int)] = []      # [(SimpleWord, row)]
        selectedTerms = self.newWordListWidget.selectedItems()
        if selectedTerms:
            # 如果选中单词则只查询选中的单词
            for termItem in selectedTerms:
                row = self.newWordListWidget.row(termItem)
                word = self.remoteWordsDict[termItem.text()]
                wordList.append((word, row))
        else:  # 没有选择则查询全部
            for row in range(self.newWordListWidget.count()):
                termItem = self.newWordListWidget.item(row)
                word = self.remoteWordsDict[termItem.text()]
                wordList.append((word, row))

        logger.info(f'待查询单词{wordList}')
        # 查询线程
        self.progressBar.setMaximum(len(wordList))
        self.queryWorker = QueryWorker(wordList, apis[currentConfig['selectedApi']])
        self.queryWorker.moveToThread(self.workerThread)
        self.queryWorker.thisRowDone.connect(self.on_thisRowDone)
        self.queryWorker.thisRowFailed.connect(self.on_thisRowFailed)
        self.queryWorker.tick.connect(lambda: self.progressBar.setValue(self.progressBar.value() + 1))
        self.queryWorker.allQueryDone.connect(self.on_allQueryDone)
        self.queryWorker.start.connect(self.queryWorker.run)
        self.queryWorker.start.emit()

    @pyqtSlot(int, dict)
    def on_thisRowDone(self, row, result):
        """该行单词查询完毕"""
        doneIcon = QIcon(':/icons/done.png')
        wordItem = self.newWordListWidget.item(row)
        wordItem.setIcon(doneIcon)
        wordItem.setData(Qt.UserRole, result)

    @pyqtSlot(int)
    def on_thisRowFailed(self, row):
        failedIcon = QIcon(':/icons/failed.png')
        failedWordItem = self.newWordListWidget.item(row)
        failedWordItem.setIcon(failedIcon)

    @pyqtSlot()
    def on_allQueryDone(self):
        failed = []

        for i in range(self.newWordListWidget.count()):
            wordItem = self.newWordListWidget.item(i)
            if not wordItem.data(Qt.UserRole):
                failed.append(wordItem.text())

        if failed:
            logger.warning(f'查询失败或未查询:{failed}')

        self.pullRemoteWordsBtn.setEnabled(True)
        self.queryBtn.setEnabled(True)
        self.btnSync.setEnabled(True)

    @pyqtSlot()
    def on_btnSync_clicked(self):

        failedGenerator = (self.newWordListWidget.item(row).data(Qt.UserRole) is None for row in range(self.newWordListWidget.count()))
        if any(failedGenerator):
            if not askUser('存在未查询或失败的单词，确定要加入单词本吗？\n 你可以选择失败的单词点击 "查询按钮" 来重试。'):
                return

        currentConfig = self.getAndSaveCurrentConfig()

        # create Note Type/Model
        try:
            model = getOrCreateModel(MODEL_NAME)
        except RuntimeError as err:
            logger.warning(err)
            if not askUser(f"{err}\nDeleting it would delete ALL its cards and notes!!! Continue?", defaultno=True):
                logger.info("Aborted")
                return
            if not askUser(f"[DANGEROUS ACTION!!!] Are you sure to delete model '{MODEL_NAME}' AND all its cards/notes???", defaultno=True):
                logger.info("Aborted upon second reminder")
                return
            # force delete the existing model
            model = getOrCreateModel(MODEL_NAME, force=True)

        # create 'Normal' card template (card type)
        getOrCreateModelCardTemplate(model, NORMAL_CARD_TEMPLATE_NAME)
        # create 'Backwards' card template (card type)
        # getOrCreateBackwardsCardTemplate(model, BACKWARDS_CARD_TEMPLATE_NAME)

        # create deck
        deck = getOrCreateDeck(self.deckComboBox.currentText(), model=model)

        logger.info('同步点击')
        imagesDownloadTasks = []
        audiosDownloadTasks = []
        newWordCount = self.newWordListWidget.count()

        # 判断是否需要下载发音
        if currentConfig['noPron']:
            logger.info('不下载发音')
            preferred_pron = None
        else:
            preferred_pron = 'AmEPron' if self.AmEPronRadioButton.isChecked() else 'BrEPron'
            logger.info(f'Preferred Pronunciation: {preferred_pron}')

        added = 0
        for row in range(newWordCount):
            wordItem = self.newWordListWidget.item(row)
            wordItemData = wordItem.data(Qt.UserRole)
            if wordItemData:
                word = wordItemData['term']
                logger.debug(f"wordItemData ({word}): {wordItemData}")

                # Add image download task
                imageFilename = None
                if wordItemData['image']:
                    imageFilename = f"{ASSET_FILENAME_PREFIX}-{word}.jpg"       # to be consistent with 4.x
                    imagesDownloadTasks.append((imageFilename, wordItemData['image'],))
                else:
                    logger.debug(f"No image for word {word}")

                # Add audio download task
                whichPron = preferred_pron
                pronFilename = None
                if whichPron:
                    has_pron = True
                    if not wordItemData.get(whichPron):     # whichPron is missing
                        newPron = 'AmEPron' if whichPron == 'BrEPron' else 'BrEPron'
                        if not wordItemData.get(newPron):   # newPron is also missing
                            has_pron = False
                            logger.warning(f"No audio for word {word}!")
                        else:                               # whichPron is missing, but newPron is present
                            has_pron = True
                            logger.warning(f"{whichPron} is missing for word {word}. Downloading {newPron} instead.")
                            whichPron = newPron
                    if has_pron:
                        # pronFilename = f"{whichPron}_{wordItemData['term']}.mp3"
                        pronFilename = f"{ASSET_FILENAME_PREFIX}-{word}.mp3"    # to be consistent with 4.x
                        audiosDownloadTasks.append((pronFilename, wordItemData[whichPron],))

                # add note
                addNoteToDeck(deck, model, currentConfig, wordItemData, imageFilename, whichPron, pronFilename)
                added += 1
        mw.reset()

        logger.info(f"Image download tasks: {imagesDownloadTasks}")
        logger.info(f"Audio download tasks: {audiosDownloadTasks}")

        if imagesDownloadTasks or audiosDownloadTasks:
            self.btnSync.setEnabled(False)
            self.progressBar.setValue(0)
            self.progressBar.setMaximum(len(imagesDownloadTasks) + len(audiosDownloadTasks))
            if self.assetDownloadThread is not None:
                self.assetDownloadThread.requestInterruption()
                self.assetDownloadThread.quit()
                self.assetDownloadThread.wait()

            self.assetDownloadThread = QThread(self)
            self.assetDownloadThread.start()
            self.assetDownloadWorker = AssetDownloadWorker(mw.col.media.dir(), imagesDownloadTasks, audiosDownloadTasks)
            self.assetDownloadWorker.moveToThread(self.assetDownloadThread)
            self.assetDownloadWorker.tick.connect(lambda: self.progressBar.setValue(self.progressBar.value() + 1))
            self.assetDownloadWorker.start.connect(self.assetDownloadWorker.run)
            self.assetDownloadWorker.done.connect(lambda: tooltip(f'图片音频下载完成'))
            self.assetDownloadWorker.done.connect(self.assetDownloadThread.quit)
            self.assetDownloadWorker.start.emit()

        self.newWordListWidget.clear()

        needToDeleteWordItems = [
            self.needDeleteWordListWidget.item(row)
            for row in range(self.needDeleteWordListWidget.count())
            if self.needDeleteWordListWidget.item(row).checkState() == Qt.Checked
        ]
        needToDeleteWords = [i.text() for i in needToDeleteWordItems]

        deleted = 0

        if needToDeleteWords and askUser(f'确定要删除这些单词吗:{needToDeleteWords[:3]}...({len(needToDeleteWords)}个)', title='Dict2Anki', parent=self):
            needToDeleteWordNoteIds = getNotes(needToDeleteWords, currentConfig['deck'])
            mw.col.remNotes(needToDeleteWordNoteIds)
            deleted += 1
            mw.col.reset()
            mw.reset()
            for item in needToDeleteWordItems:
                self.needDeleteWordListWidget.takeItem(self.needDeleteWordListWidget.row(item))
            logger.info('删除完成')
        logger.info('完成')

        if not audiosDownloadTasks:
            tooltip(f'添加{added}个笔记\n删除{deleted}个笔记')

    @pyqtSlot()
    def on_btnDownloadMissingAssets_clicked(self):
        tooltip("btnDownloadMissingAssets Clicked!")

    @pyqtSlot()
    def on_btnExportAudio_clicked(self):
        tooltip("btnExportAudio Clicked!")

    @pyqtSlot()
    def on_btnBackwardTemplate_clicked(self):
        """Add Or Delete Backwards Card Template (Card Type)"""
        modelObject = mw.col.models.byName(MODEL_NAME)
        if not modelObject:
            showInfo(f"Model (Note Type) '{MODEL_NAME}' does not exist! Please Sync first!")
            return

        backwardsTemplate = None
        for temp in modelObject['tmpls']:
            if temp['name'] == BACKWARDS_CARD_TEMPLATE_NAME:
                backwardsTemplate = temp
                break

        if backwardsTemplate:
            if askUser("Are you sure to delete Backwards template?", defaultno=True):
                try:
                    deleteBackwardsCardTemplate(modelObject, backwardsTemplate)
                    logger.info("Deleted Backwards template")
                    tooltip("Deleted")
                except AssertionError as err:
                    logger.error(f"Failed to delete Backwards template: {err}")
                    tooltip("Failed!")
        else:
            if askUser("Add Backwards template now?", defaultno=True):
                try:
                    getOrCreateBackwardsCardTemplate(modelObject, BACKWARDS_CARD_TEMPLATE_NAME)
                    logger.info("Added Backward template")
                    tooltip("Added")
                except Exception as e:
                    logger.error(e)
                    tooltip("Failed!")

    @pyqtSlot()
    def on_btnCheckTemplates_clicked(self):
        tooltip("btnCheckTemplates Clicked!")