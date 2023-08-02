from storage.Storage import Storage
from specification.Query import *
import numpy as np

class QueryEvaluator():
    def __init__(self, storage) -> None:
        self.storage = storage
        self.queryMap = {
            "SELECT" : self.select,
            "CREATETABLE" : self.storage.createTable,
            "CREATEINDEX" : self.storage.createIndex,
            "CREATEDB" : self.storage.createDB,
            "CHANGEDB" : self.storage.changeDB,
            "SHOWDB" : self.storage.showDB,
            "SHOWTABLE" : self.storage.showTable,
            "SHOWINDEX" : self.storage.showIndex,
            "SHOWFEATURE" :self.storage.showFeature,
            "INSERTIMAGE" :self.storage.insertImage,
            "INSERTFOLDER" :self.storage.insertFolder,
            "DELETEIMAGE" :self.storage.deleteImage,
        }

    def execute(self, query:Query):
        res = self.queryMap[query.queryType](query)
        query_result = {
            "type" : query.queryType,
            "data" : res
        }
        return query_result
    
    def select(self, query):
        statement_result = self.storage.search(query)
        if statement_result is not None:
            result = self.topKFagin(statement_result, query)

            for r in result:
                r['path'] = self.storage.getCurrentDB().getImagebyId(r['id'])
                meta = self.storage.getCurrentDB().getMetadata([r['id']])
                # print(meta)
                for k,v in meta.items():
                    r[k] = v[r['id']]
        else:
            result = []
        return result

    def topKFagin(self, statement_result, q:SelectQuery):
        #Fagin Algorithm
        m = {}
        c = []
        i = 0
        max = len(statement_result[0]['id'][0])
        # print(max)
        while len(c) < q.type[1] and len(c) < max :
            for j in range(len(statement_result)):
                id = statement_result[j]['id'][0][i]
                sim = statement_result[j]['sim'][0][i]
                if (id not in m.keys()):
                    m[id] = [-1 for i in range(len(statement_result))]
                m[id][j] = sim
                if -1 not in m[id]:
                    c.append({"id":id, 'statement_score':m[id]})
                    del m[id]
            i+=1

        for id, sim in m.items():
            for i in range(len(statement_result)):
                if sim[i] == -1:
                    sim[i] = statement_result[i]['sim'][0][np.where(statement_result[i]['id'][0] == id)[0].item()]
            c.append({"id":id, 'statement_score':sim})

        for i in c:
            i['sim'] = q.plan.compute(i['statement_score'], q.semantic)
        c.sort(key=lambda x: x['sim'], reverse=True)
        result = c[:q.type[1]]
        for r in result:
            for i, s in enumerate(q.statements):
                r[str(s)] = r['statement_score'][i]
            del r['statement_score']
        return result

    def topKNRA(self, statement_result, q:SelectQuery):
        pass
                
                #No random access algorithm
                # res = {}
                # found = False
                # i = 0
                # max_table = [-999 for i in range (len(statement_result))]
                # while not found and i < self.db[self.current_db].imageCount:
                #     for j in range(len(statement_result)):
                #         id = statement_result[j]['id'][0][i]
                #         if (id not in res.keys()):
                #             res[id] = {'sim':[-1 for i in range(len(statement_result))], 'lb':-999, 'ub':999}
                #         res[id]['sim'][j] = statement_result[j]['sim'][0][i]
                #         max_table[j] = statement_result[j]['sim'][0][i]
                    
                #     for k, v in res.items():
                #         #compute lb
                #         res[k]['lb'] = q.plan.compute(list(map(lambda x : max(0, x), v['sim'])), q.semantic)
                #         #compute ub
                #         res[k]['ub'] = q.plan.compute([max(x, max_table[v['sim'].index(x)]) for x in v['sim']], q.semantic)
                #     #check maximum lb 
                #     if (i==20):
                #         found = True
                #     i+=1

                # return (res)