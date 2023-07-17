import faiss
import numpy as np

class Index():
    def __init__(self, features) -> None:
        pass
    def search(self, query, count):
        pass
    def save(self) -> str:
        pass
    def add(self, features):
        pass
    def remove(self, ids):
        pass


class faissIndex(Index):
    def __init__(self, features = None, path = None) -> None:
        if path is not None:
            self.faiss = faiss.read_index(path)
        
    def add(self, new_features, all_features=None):
        self.faiss.add(new_features)

    def search(self, query, count, filter):
        if filter is not None:
            sel = faiss.IDSelectorArray(filter)
            return self.faiss.search(query, count, params=faiss.SearchParameters(sel=sel))
        else:
            return self.faiss.search(query, count)
    
    def save(self, path):
        faiss.write_index(self.faiss, path)

    def delete(self, ids):
        self.faiss.remove_ids(np.array(ids).astype('int64'))

    
class FlatCosineIndex(faissIndex):
    def __init__(self, features = None, path = None) -> None:
        super().__init__(features, path)
        if path is None:
            self.faiss = faiss.IndexFlatIP(len(features[0]))
            self.add(features)
    def add(self, new_features, all_features=None):
        norm_feature = np.copy(new_features)
        faiss.normalize_L2(norm_feature)
        self.faiss.add(norm_feature)
    def search(self, query, count, filter):
        norm_q = np.copy(query)
        faiss.normalize_L2(norm_q)
        return super().search(norm_q, count, filter)

class FlatL2Index(faissIndex):
    def __init__(self, features = None, path = None) -> None:
        super().__init__(features, path)
        if path is None:
            self.faiss = faiss.IndexFlatIP(len(features[0]))
            self.add(features)

class PQCosineIndex(faissIndex):
    def __init__(self, features=None, path=None) -> None:
        super().__init__(features, path)
        if path is None:
            self.add(all_features=features)
    def add(self,  all_features, new_features=None):
        self.faiss = faiss.index_factory(len(all_features[0]), "PQ16", faiss.METRIC_INNER_PRODUCT)
        norm = np.copy(all_features)
        faiss.normalize_L2(norm)
        self.faiss.train(norm)
        self.faiss.add(norm)
    def search(self, query, count, filter):
        norm_q = np.copy(query)
        faiss.normalize_L2(norm_q)
        return super().search(norm_q, count, filter)
