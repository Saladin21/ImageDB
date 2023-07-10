
class Query():
    def __init__(self, queryType) -> None:
        self.queryType = queryType

class SelectStatement():
    def __init__(self, predicate, variable, table, index='FlatL2', not_flag=False, meta_label = None) -> None:
        self.predicate = predicate
        self.variable = variable #feature not extracted
        self.table = table
        self.index = index
        self.not_flag = not_flag
        self.meta_label = meta_label

class SelectPlanNode():
     def __init__(self, value=None) -> None:
          self.left : SelectPlanNode = None
          self.right : SelectPlanNode = None
          self.value = value # and, or, not, id of selectstatement
     def compute(self, sim:list, semantic):
          if isinstance(self.value, int):
               return sim[self.value]
          elif semantic == "min":
               if self.value == 'and':
                    return min(self.left.compute(sim, semantic), self.right.compute(sim, semantic))
               elif self.value =='or':
                    return max(self.left.compute(sim, semantic), self.right.compute(sim, semantic))
               else:
                    return 1-(self.left.compute())
          elif semantic == 'average':
               if self.value == 'and':
                    return (self.left.compute(sim, semantic) + self.right.compute(sim, semantic)) / 2
               elif self.value =='or':
                    return 1 - ((1 - self.left.compute(sim, semantic)+ 1 -  self.right.compute(sim, semantic))/2)
               else:
                    return 1-(self.left.compute(sim, semantic))
     def updateValue(self, value):
          if isinstance(self.value, int):
               self.value += value
          else:
               if self.left is not None:
                    self.left.updateValue(value)
               if self.right is not None:
                    self.right.updateValue(value)

class SelectQuery(Query):
    def __init__(self, statements, plan : SelectPlanNode, semantic, type) -> None:
        super().__init__(queryType = 'SELECT')
        self.plan = plan #binary tree
        self.semantic = semantic #fuzzy logic semantic
        self.type = type #('knn', k) atau ('thr', thr)
        self.statements = statements # list of SelectStatement

class CreateTableQuery(Query):
    def __init__(self, tableName, FEId) -> None:
        super().__init__('CREATETABLE')
        self.tableName = tableName
        self.FEId = FEId

class CreateIndexQuery(Query):
    def __init__(self, tableName, indexType) -> None:
        super().__init__('CREATEINDEX')
        self.tableName = tableName
        self.indexType = indexType

class CreateDBQuery(Query):
    def __init__(self, dbName) -> None:
        super().__init__('CREATEDB')
        self.dbName = dbName

class ChangeDBQuery(Query):
    def __init__(self, dbName) -> None:
        super().__init__('CHANGEDB')
        self.dbName = dbName

class ShowIndexQuery(Query):
     def __init__(self, table_name) -> None:
          super().__init__('SHOWINDEX')
          self.tableName = table_name

class InsertImageQuery(Query):
     def __init__(self, values) -> None:
          super().__init__('INSERTIMAGE')
          self.values = values

class InsertFolderQuery(Query):
     def __init__(self, folder) -> None:
          super().__init__('INSERTFOLDER')
          self.folder = folder

class DeleteImageQuery(Query):
     def __init__(self, id) -> None:
          super().__init__('DELETEIMAGE')
          self.id = id