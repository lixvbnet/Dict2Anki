import logging
from queue import Queue
from threading import Thread
from abc import ABC, abstractmethod

logger = logging.getLogger('dict2Anki.misc')


class SimpleWord(ABC):
    @classmethod
    def from_values(cls, values: [str]):
        n = len(values)
        if n == 0:
            return None
        term = values[0]
        trans = ""
        modifiedTime = 0
        bookId = 0
        bookName = ""
        if n > 1:
            trans = values[1]
        if n > 2:
            modifiedTime = int(values[2])
        if n > 3:
            bookId = int(values[3])
        if n > 4:
            bookName = values[4]
        return SimpleWord(term=term, trans=trans, modifiedTime=modifiedTime, bookId=bookId, bookName=bookName)

    """A SimpleWord includes the term and a brief translation, as well as other metadata."""
    def __init__(self, term: str, trans="", modifiedTime=0, bookId=0, bookName=""):
        self.term = term
        self.trans = trans
        self.modifiedTime = modifiedTime
        self.bookId = bookId
        self.bookName = bookName

    def toString(self) -> str:
        return f'{self.term} {self.trans} modifiedTime={self.modifiedTime}, bookId={self.bookId}, bookName={self.bookName}'

    def __str__(self) -> str:
        # return self.toString()
        return self.term

    def __repr__(self) -> str:
        # return f'SimpleWord({self.__str__()})'
        return self.term


class AbstractDictionary(ABC):

    @staticmethod
    @abstractmethod
    def loginCheckCallbackFn(cookie: dict, content: str):
        pass

    @abstractmethod
    def checkCookie(self, cookie: dict):
        pass

    @abstractmethod
    def getGroups(self) -> [(str, int)]:
        pass

    @abstractmethod
    def getTotalPage(self, groupName: str, groupId: int) -> int:
        pass

    @abstractmethod
    def getWordsByPage(self, pageNo: int, groupName: str, groupId: str) -> [SimpleWord]:
        pass

    @classmethod
    @abstractmethod
    def close(cls):
        pass


class AbstractQueryAPI(ABC):
    @classmethod
    @abstractmethod
    def query(cls, word: SimpleWord) -> dict:
        """
        查询
        :param word: 单词
        :return: 查询结果 dict(term, definition, phrase, image, sentence, BrEPhonetic, AmEPhonetic, BrEPron, AmEPron)
        """
        pass

    @classmethod
    @abstractmethod
    def close(cls):
        pass


class Mask:
    def __init__(self, info):
        self.info = info

    def __repr__(self):
        return '*******'

    def __str__(self):
        return self.info


class Worker(Thread):
    def __init__(self, queue, result_queue):
        super(Worker, self).__init__()
        self._q = queue
        self.result_queue = result_queue
        self.daemon = True
        self.start()

    def run(self):
        while True:
            try:
                f, args, kwargs = self._q.get()
                if f:
                    result = f(*args, **kwargs)
                    if result:
                        self.result_queue.put(result)
            except Exception as e:
                logger.exception(e)
            finally:
                self._q.task_done()


class ThreadPool:
    def __init__(self, max_workers):
        self._q = Queue(max_workers)
        self.results_q = Queue()
        self.result = []
        # Create Worker Thread
        for _ in range(max_workers):
            Worker(self._q, self.results_q)

    def submit(self, f, *args, **kwargs):
        self._q.put((f, args, kwargs))

    def wait_complete(self):
        self._q.join()
        while not self.results_q.empty():
            self.result.append(self.results_q.get())
        return self.result

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.wait_complete()
