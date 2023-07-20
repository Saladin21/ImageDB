from evaluator import QueryEvaluator
from storage.Storage import Storage
from specification.Parser import Parser
import time

class ImageDB():
    def __init__(self, data_path="data/") -> None:
        self.parser = Parser()
        self.storage = Storage(data_path=data_path)
        self.evaluator = QueryEvaluator(storage=self.storage)
    def query(self, input):
        res = {}
        try:
            q = self.parser.parse(input)
        except Exception as e:
            res['type'] = 'ERROR'
            res['error'] =  e
            return res
        t0 = time.time()
        try:
            res = self.evaluator.execute(q)
            res['time'] = time.time() - t0
        except Exception as e:
            res['type'] = 'ERROR'
            res['error'] =  e
        return res