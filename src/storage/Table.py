import numpy as np
import os


# storage.FeatureExtractor
from specification.Query import SelectStatement

class Table():
    def __init__(self, name, FE_id, data_path) -> None:
        self.name = name
        self.FE_id = FE_id
        self.index = {}
        self.data_path = os.path.join(data_path, self.name)
    def create_index(self,index_type, index_class, FEFactory, img_path):
        index_path = os.path.join(self.data_path, f"{index_type}.bin")
        if os.path.exists(index_path):
            self.index[index_type] = index_class(path = index_path)
        else:    
            cache_path = os.path.join(self.data_path, 'features.npy')
            if os.path.exists(cache_path):
                features = np.load(cache_path)
            else:
                fe = FEFactory.getFE(self.FE_id)
                features = np.array([fe.extractImage(i) for i in img_path])
                np.save(cache_path, features)
            self.index[index_type] = index_class(features)
            self.index[index_type].save(index_path)
    def getIndex(self, index_type):
        if index_type is None:
            i = self.index.get("FlatL2")
        else:
            i = self.index.get(index_type)
        if i is None:
            raise AssertionError("Index does not exisst")
        else:
            return i
    def getDetails(self):
        return {
            "name" : self.name,
            'feature' : self.FE_id
        }
    def getIndexes(self):
        return list(self.index.keys())
    def search(self, selecStatement: SelectStatement, FEFactory, count, filter=None):
        fe = FEFactory.getFE(self.FE_id)
        q_vec = np.array([fe(selecStatement.variable, pred=selecStatement.predicate)])
        return self.index[selecStatement.index].search(q_vec, count, filter)
    def insert(self, FEFactory, img_path):
        if len(self.index) > 0:
            cache_path = os.path.join(self.data_path, 'features.npy')
            fe = FEFactory.getFE(self.FE_id)
            features = np.array([fe.extractImage(i) for i in img_path])

            if os.path.exists(cache_path):
                    temp = np.load(cache_path)
                    all_features = np.concatenate((temp, features))
                    np.save(cache_path, all_features)
            else:
                all_features = features
            for k, v in self.index.items():
                index_path = os.path.join(self.data_path, f"{k}.bin")
                v.add(new_features = features, all_features=all_features)
                v.save(index_path)
    def delete(self, ids):
        cache_path = os.path.join(self.data_path, 'features.npy')
        if os.path.exists(cache_path):
                temp = np.load(cache_path)
                np.delete(temp, ids, axis=0)
                np.save(cache_path, temp)
        for k, v in self.index.items():
            index_path = os.path.join(self.data_path, f"{k}.bin")
            v.delete(ids)
            v.save(index_path)