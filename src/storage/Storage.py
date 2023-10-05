import numpy as np
import os
import json
import time

from storage.FeatureExtractor import FEFactory
from specification.Query import *
from specification.Parser import Parser      
from storage.Database import Database          
    
class Storage():
    def __init__(self, data_path="data/") -> None:
        self.db = {} #dictionary name -> Database
        self.fe = FEFactory()
        self.current_db = None
        self.data_path=data_path
        self.structure = {"databases" : {}}
        if not os.path.exists(self.data_path):
            os.makedirs(self.data_path)
        if os.path.exists(os.path.join(self.data_path, "structure.json")):
            self.loadState()

    def loadState(self):
        # print("loading state")
        with open(os.path.join(self.data_path, 'structure.json'), 'r') as f:
            temp_structure = json.load(f)

        for db_k, db_v in temp_structure['databases'].items():
            self.createDB(CreateDBQuery(db_k))
            for tab_k, tab_v in db_v['tables'].items():
                self.createTable(CreateTableQuery(tab_k, tab_v['fe_id']))
                for index in tab_v['indexes']:
                    self.createIndex(CreateIndexQuery(tab_k, index))


    def saveState(self):
        with open(os.path.join(self.data_path, 'structure.json'), 'w') as f:
            json.dump(self.structure, f)

    def createDB(self, q : CreateDBQuery):
        if (q.dbName not in self.db.keys()):
            self.db[q.dbName] = Database(q.dbName, self.data_path)
            self.current_db = q.dbName
            path = os.path.join(self.data_path, q.dbName)
            if not os.path.exists(path):
                os.makedirs(path)
            self.structure['databases'][q.dbName] = {
                # "img_path" : q.path,
                "tables" : {}
            }
            self.saveState()
            return f"Database {q.dbName} Created"
        else:
            raise AssertionError('Database already exist')

    def changeDB(self, q : ChangeDBQuery):
        # print(q.dbName in self.db.keys(), q.dbName, self.db.keys())
        if (q.dbName in self.db.keys()):
            self.current_db = q.dbName
            return f"Using Database {q.dbName}"
        else:
            raise AssertionError('Database does not exist')
        
    def getCurrentDB(self) -> Database:
        return self.db[self.current_db]
    
    def insertImage(self, q:InsertImageQuery):
        n = self.getCurrentDB().insertImages(self.fe, q.values)
        return f"{n} images succesfully inserted"

    def insertFolder(self, q:InsertFolderQuery):
        n = self.getCurrentDB().insertFolder(self.fe, q.folder)
        return f"{n} images succesfully inserted"

    def deleteImage(self, q:DeleteImageQuery):
        self.getCurrentDB().deleteImage(q.id)
        return f"{len(q.id)} images succesfully deleted"

    def createTable(self, q: CreateTableQuery):
        if (self.current_db is not None):
            self.getCurrentDB().addTable(q.tableName, q.FEId)
            path = f"{self.data_path}{self.current_db}/{q.tableName}"
            if not os.path.exists(path):
                os.makedirs(path)
            self.structure['databases'][self.current_db]['tables'][q.tableName] = {
                "fe_id" : q.FEId,
                "indexes" : []
            }
            self.saveState()
            return f"Table {q.tableName} created"
        else:
            raise AssertionError('No database is chosen')
    
    def createIndex(self, q: CreateIndexQuery):
        if (self.current_db is not None):
            self.db[self.current_db].addIndex(q.tableName, q.indexType, self.fe)
            self.structure['databases'][self.current_db]['tables'][q.tableName]["indexes"].append(q.indexType)
            self.saveState()
            return f"Index {q.indexType} created on {q.tableName}"
        else:
            raise AssertionError('No database is chosen')
    
    def showDB(self, q=None):
        return list(self.db.keys())
    
    def showTable(self, q=None):
        return self.getCurrentDB().listTable()

    def showIndex(self, q:ShowIndexQuery):
        return self.getCurrentDB().listIndex(q.tableName)

    def showFeature(self, q=None):
        return self.fe.listFE()
    
    def showImage(self, q=None):
        return self.getCurrentDB().getImages()

    def search(self, q:SelectQuery):
        if (self.current_db is not None):
            
            #metadata filter
            if q.statements_meta is not None:
                meta_ids = []
                for meta in q.statements_meta:
                    meta_ids.append(self.getCurrentDB().searchMeta(meta))
                filter = q.plan_meta.computeMeta(meta_ids, self.getCurrentDB().getImageCount())
                filter = list(filter)
            else:
                filter = None

            #similarity search
            if (filter is None or len(filter) > 0):
                if (q.type[0] == 'knn'):
                    if q.statements is None:
                        return (True, [{'id': i} for i in filter][:q.type[1]])
                    statement_result = []
                    for s in q.statements:
                        res = self.db[self.current_db].search(s, self.fe, self.db[self.current_db].getImageCount(), filter)
                        if s.not_flag:
                            tmp_res_0 = np.flip(res[0])
                            tmp_res_1 = np.flip(res[1])
                            res = (tmp_res_0, tmp_res_1)
                        statement_result.append({'sim':res[0], 'id':res[1]})
                    
                        # statement_result.append({'sim':np.ones(len(filter)), 'id':np.array(filter)})
                    return (False, statement_result)
            else:
                return (None, None)
        else:
            raise AssertionError('No database is chosen')

    