import os
import pickle
import shutil
import glob

from storage.Table import Table
from storage.MetaTable import MetaTable
from storage.Index import *
from specification.Query import SelectStatement

class Database():
    def __init__(self,name, data_path) -> None:
        # self.available_index = {
        #     "FlatIP" : FlatIPIndex,
        #     "PQIP" : PQIPIndex,
        #     "FlatCosine" : FlatCosineIndex,
        #     "PQCosine" : PQCosineIndex
        # }
        self.name = name
        self.tables = {}
        self.data_path = os.path.join(data_path, self.name)
        self.meta_table = MetaTable(self.data_path)
        meta_path = os.path.join(self.data_path, 'META')
        if not os.path.exists(meta_path):
                os.makedirs(meta_path)
        self.img_dir = os.path.join(self.data_path, '_images_/')
        if not os.path.exists(self.img_dir):
                os.makedirs(self.img_dir)
        # self.imagesPath = glob.glob(path+"/*")
        savedImages = os.path.join(self.data_path, 'images.pk')
        if os.path.exists(savedImages):
            with open(savedImages, 'rb') as f:
                self.imagesPath = pickle.load(f)
        else:
            self.imagesPath = []
    def getImageCount(self):
        return len(self.imagesPath)
    def addTable(self, name, FE_id):
        self.tables[name] = Table(name, FE_id, self.data_path)
    def getTable(self, tableName) -> Table:
        t = self.tables.get(tableName)
        if t is None:
            raise AssertionError(f"Table {tableName} does not exist")
        else:
            return t
    def addIndex(self, tableName, index_type, FEFactory):
        index_type = index_type.upper()
        self.getTable(tableName).create_index(index_type, FEFactory, self.imagesPath)
    def getIndex(self, tablename, indexType):
        return self.getTable(tablename).getIndex(indexType)
    def listTable(self):
        res = []
        for t in self.tables.values():
            res.append(t.getDetails())
        return res
    def listIndex(self, tableName):
        return self.getTable(tableName).getIndexes()
    def searchMeta(self, selectStatement):
        return self.meta_table.search(selectStatement)
    def search(self, selectStatement: SelectStatement, FEFactory, count, filter=None):
        return self.getTable(selectStatement.table).search(selectStatement, FEFactory, count, filter)
    def insertImages(self, FEFactory, img_path):
        new_path = self.copyImages(img_path)
        self.imagesPath += new_path
        for table in self.tables.values():
            table.insert(FEFactory, new_path)
        self.meta_table.insert(FEFactory, img_path)
        self.saveImagesPath()
        return len(img_path)
    def insertFolder(self, FEFactory, folder_path):
        img_path = glob.glob(os.path.join(folder_path, "*"))
        return self.insertImages(FEFactory, img_path)
    def deleteImage(self, ids):
        for id in ids:
            self.imagesPath.pop(id)
        for table in self.tables.values():
            table.delete(ids)
        self.meta_table.delete(ids)
        self.saveImagesPath()
    def saveImagesPath(self):
        savedImages = os.path.join(self.data_path, 'images.pk')
        with open(savedImages, 'wb') as f:
            pickle.dump(self.imagesPath, f)
    def copyImages(self, img_path):
        new_path = []
        for im in img_path:
            shutil.copy2(im, self.img_dir)
            base = os.path.basename(im)
            new_path.append(self.img_dir+base)
        return new_path
    def getImagebyId(self, id):
        return self.imagesPath[int(id)]
    def getMetadata(self, id):
        return self.meta_table.getMetadata(id)
    def getImages(self):
        return self.imagesPath