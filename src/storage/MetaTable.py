import numpy as np
import os
import pandas as pd

from specification.Query import SelectStatement

class MetaTable():
    def __init__(self, data_path) -> None:
        self.name = "META"
        self.FE_id = "META"
        self.columns = ['name', 'date', 'height', 'width', 'extension']
        self.data_path = os.path.join(data_path, self.name)
        cache_path = os.path.join(self.data_path, 'metadata.csv')
        if os.path.exists(cache_path):
            self.metadata = pd.read_csv(cache_path)
        else:
            self.metadata = {}
            for c in self.columns:
                self.metadata[c] = []
            self.metadata = pd.DataFrame(self.metadata)
        
        self.ops = {
            '=' : lambda col, var : self.metadata[self.metadata[col] == var],
            '>' : lambda col, var : self.metadata[self.metadata[col] > var],
            '<' : lambda col, var : self.metadata[self.metadata[col] < var],
            '>=' : lambda col, var : self.metadata[self.metadata[col] >= var],
            '<=' : lambda col, var : self.metadata[self.metadata[col] <= var],
            '<>' : lambda col, var : self.metadata[self.metadata[col] != var],
        }
    # def getDetails(self):
    #     return {
    #         "name" : self.name,
    #         'feature' : self.FE_id
    #     }
    def search(self, selecStatement: SelectStatement):
        if (selecStatement.meta_label == 'height' or selecStatement.meta_label=='width'):
            var = int(selecStatement.variable)
        else:
            var = selecStatement.variable
        found = self.ops[selecStatement.predicate](selecStatement.meta_label, var)
        found = set(found.index)
        return found
    
    def insert(self, FEFactory, img_path):
        cache_path = os.path.join(self.data_path, 'metadata.csv')
        fe = FEFactory.getFE(self.FE_id)
        features = [fe.extractImage(i) for i in img_path]

        self.metadata = pd.concat([self.metadata, pd.DataFrame(features)])
        self.metadata.to_csv(cache_path, index=False)

    def delete(self, ids):
        cache_path = os.path.join(self.data_path, 'metadata.csv')
        self.metadata.drop(ids)
        self.metadata.reset_index(drop=True)
        self.metadata.to_csv(cache_path, index=False)
    
    def getMetadata(self, id):
        return self.metadata.filter(items=id, axis=0).to_dict()