from specification.Query import *
from specification.ParseObject import *
import pyparsing as pp

class Parser():
    def __init__(self) -> None:
        self.typeMap = {
            'SELECT' : self.parseSelect,
            'INSERTIMAGEVALUES' : self.parseInsertImage,
            'INSERTIMAGEFOLDER' : self.parseInsertFolder,
            'DELETEIMAGE' : self.parseDeleteImage,
            'CREATEDATABASE' : self.parseCreateDB,
            'CREATETABLE' : self.parseCreateTable,
            'CREATEINDEX' : self.parseCreateIndex,
            'USE' : self.parseChangeDB,
            'SHOWTABLE' : self.parseShowTable,
            'SHOWINDEX' : self.parseShowIndex,
            'SHOWDATABASE' : self.parseShowDB,
            'SHOWFEATURE' : self.parseShowFeature,
        }
    def parse(self, input) -> Query:
        type = self.parseType(input)
        return self.typeMap[type](input)
    
    def parseType(self, input):
        type = (select_) ^ (use_)
        type = type ^ (create_ + (table_  ^ database_ ^ index_))
        type = type ^ (insert_ + image_ + values_) ^ (insert_ + image_ + folder_) ^ (delete_ + image_)
        type = type ^ (show_ + (database_ ^ table_ ^ index_ ^ feature_))

        parsed = type.parse_string(input)
        res = ""
        for a in parsed:
            res += a
        return res

    def parseSelect(self, input) -> SelectQuery:
        operator_sim = ((contains_ | visual_ | semantic_ | above_ | left_) + lparen + string + pp.Optional(comma + string) +rparen).setParseAction(OperatorSim)

        number = (
        pp.Word(pp.nums) + pp.Optional("." + pp.OneOrMore(pp.Word(pp.nums)))
        ).setParseAction(Number)

        identifier = alphaword.setParseAction(
        Identifier
        )

        expr = pp.Forward()
        expr_meta = pp.Forward()

        condition = pp.Group(pp.Optional(not_) + meta_ + dot + identifier + (operator + (string | number))
        ).setParseAction(Condition)

        condition = condition | (lparen + expr_meta + rparen)

        condition_sim = pp.Group(pp.Optional(not_) +  (identifier + (dot + operator_sim))).setParseAction(ConditionSim)
        condition_sim = condition_sim | (lparen + expr + rparen)

        and_condition = (condition_sim + pp.ZeroOrMore(and_ + condition_sim)).setParseAction(
        AndCondition
        )

        and_condition_meta = (condition + pp.ZeroOrMore(and_ + condition)).setParseAction(
        AndCondition
        )

        expr_meta << (and_condition_meta+ pp.ZeroOrMore(or_ + and_condition_meta))
        expr << (and_condition + pp.ZeroOrMore(or_ + and_condition))
        expr = expr.setParseAction(Expression)
        expr_meta = expr_meta.setParseAction(Expression)

        select = (select_ + image_ + from_ + identifier + pp.Optional(use_ + index_ + identifier) + pp.ZeroOrMore(comma + identifier + pp.Optional(use_ + index_ + identifier)) + where_ + ((expr_meta + and_ + expr) | expr_meta | expr) + limit_ + number).setParseAction(Select)

        try:
            parsed = select.parse_string(input)[0]
        except Exception as e:
            raise e
        # print(parsed.tables)
        if parsed.expr_meta is not None:
            statements, plan = parsed.expr.makeNode()
            statements_meta, plan_meta = parsed.expr_meta.makeNode()
        else:
            st, p = parsed.expr.makeNode()
            if st[0].table == "META":
                statements_meta, plan_meta = st, p
                statements, plan = None, None
            else:
                statements, plan = st, p
                statements_meta, plan_meta = None, None

        if statements is not None:
            for s in statements:
                index = parsed.tables.get(s.table)
                if index is not None:
                    s.index = index
                else:
                    s.index = None

        return SelectQuery(statements=statements, plan=plan, statements_meta=statements_meta, plan_meta=plan_meta, semantic='average', type=('knn', int(parsed.n)))
    
    def parseCreateDB(self, input) -> CreateDBQuery:
        parse = create_ + database_ + alphaword
        parsed = parse.parse_string(input)
        return CreateDBQuery(parsed[2])

    def parseChangeDB(self, input) -> ChangeDBQuery:
        parse = use_ + alphaword
        parsed = parse.parse_string(input)
        return ChangeDBQuery(parsed[1])

    def parseCreateTable(self, input) -> CreateTableQuery:
        parse = create_ + table_ + alphaword + feature_ + alphaword
        parsed = parse.parse_string(input)
        return CreateTableQuery(parsed[2], parsed[4])

    def parseCreateIndex(self, input) -> CreateIndexQuery:
        parse = create_ + index_ + alphaword + on_ + alphaword
        parsed = parse.parse_string(input)
        return CreateIndexQuery(parsed[4], parsed[2])
    
    def parseShowDB(self, input) -> Query:
        return Query('SHOWDB')
    
    def parseShowTable(self, input) -> Query:
        return Query('SHOWTABLE')
    
    def parseShowFeature(self, input) -> Query:
        return Query('SHOWFEATURE')
    
    def parseShowIndex(self, input) -> ShowIndexQuery:
        parse = show_ + index_ + on_ + alphaword
        parsed = parse.parse_string(input)
        return ShowIndexQuery(parsed[3])
    
    def parseInsertImage(self, input) -> InsertImageQuery:
        parse = insert_ + image_ + values_ + lparen + string + pp.ZeroOrMore(comma + string) + rparen
        parsed = parse.parse_string(input)
        images = [s.value for s in parsed[3:]]
        return InsertImageQuery(images)


    def parseInsertFolder(self, input) -> InsertFolderQuery:
        parse = insert_ + image_ + folder_ + lparen + string + rparen
        parsed = parse.parse_string(input)
        return InsertFolderQuery(parsed[-1].value)

    def parseDeleteImage(self, input) -> DeleteImageQuery:
        parse = delete_ + image_ + id_ + lparen + number + pp.ZeroOrMore(comma + number) + rparen
        parsed = parse.parse_string(input)
        ids = list(parsed[3:])
        return DeleteImageQuery(ids)
    


