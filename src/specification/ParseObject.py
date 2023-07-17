from specification.Query import SelectPlanNode, SelectStatement
import pyparsing as pp

class Expression(object):
    def __init__(self, tokens):
        self.and_conditions = tokens[::2]

    def generate(self):
        return (
            "("
            + " OR ".join(
                (and_condition.generate() for and_condition in self.and_conditions)
            )
            + ")"
        )
    
    def makeNode(self):
        statements = []
        if len(self.and_conditions) > 1:
            root = SelectPlanNode(value='or')
            # cNode = root
            length = len(self.and_conditions)
            for i in range(0, length):
                s, n = self.and_conditions[i].makeNode()
                n.updateValue(len(statements))
                statements += s
                root.child.append(n)
                # if i == 0:
                #     cNode.left = n
                # elif i < length -1:
                #     cNode.right = SelectPlanNode(value='or')
                #     cNode = cNode.right
                #     cNode.left = n
                # else:
                #     cNode.right = n
            plan = root
        else:
            c = self.and_conditions[0].makeNode()
            statements = c[0]
            plan = c[1]
        return (statements, plan)

class AndCondition(object):
    def __init__(self, tokens):
        self.conditions = tokens[::2] #list of conditions

    def generate(self):
        result = " AND ".join((condition.generate() for condition in self.conditions))
        if len(self.conditions) > 1:
            result = "(" + result + ")"
        return result
    
    def makeNode(self):
        statements = []
        if len(self.conditions) > 1:
            root = SelectPlanNode(value='and')
            # cNode = root
            length = len(self.conditions)
            for i in range(0, length):
                s, n = self.conditions[i].makeNode()
                n.updateValue(len(statements))
                statements.append(s)
                root.child.append(n)
                # if i == 0:
                #     cNode.left = n
                # elif i < length -1:
                #     cNode.right = SelectPlanNode(value='and')
                #     cNode = cNode.right
                #     cNode.left = n
                # else:
                #     cNode.right = n
            plan = root
        else:
            c = self.conditions[0].makeNode()
            statements = [c[0]]
            plan = c[1]
        return (statements, plan)

class Condition(object):
    def __init__(self, tokens):
        if (len(tokens[0]) > 4):
            i = 1
            self.not_flag = True
        else:
            i = 0
            self.not_flag = False
        self.col = tokens[0][1+i]
        self.op = tokens[0][2+i]
        self.var = tokens[0][3+i]

    def generate(self):
        return " ".join((self.identifier.generate(), self.op, self.rval.generate()))
    
    def makeNode(self):
        # print(self.op.rval[0])
        statement = SelectStatement(predicate=self.op, variable=self.var.value, table='META', not_flag=self.not_flag, meta_label=self.col.name)
        plan = SelectPlanNode(value = 0)
        if self.not_flag:
            left = plan
            plan = SelectPlanNode(value = 'not')
            plan.child.append(left)
        return (statement, plan)

class String(object):
    def __init__(self, result):
        self.value = result[0]

    def generate(self):
        return "'{}'".format(self.value)

class Number(object):
    def __init__(self, result):
        self.value = result[0]

    def generate(self):
        return self.value

class Identifier(object):
    def __init__(self, result):
        self.name = result[0]

    def generate(self):
        return self.name
    
class OperatorSim(object):
    def __init__ (self, result):
        self.op = result[0]
        self.rval = [result[1:]]
    def generate(self):
        vals = ''
        for i in self.rval[1:]:
            vals += f', {i.generate()}'
        return f"{self.op}({self.rval[0].generate()}{vals})"

class ConditionSim(object):
    def __init__(self, tokens):
        if (len(tokens[0]) > 2):
            i = 1
            self.not_flag = True
        else:
            i = 0
            self.not_flag = False
        self.identifier = tokens[0][0+i]
        self.op = tokens[0][1+i]

    def generate(self):
        return " ".join(('NOT' if self.not_flag else '', self.identifier.generate(), self.op.generate()))
    
    def makeNode(self):
        # print(self.op.rval[0])
        statement = SelectStatement(self.op.op, [s.value for s in self.op.rval[0]], self.identifier.name, None, not_flag=self.not_flag)
        plan = SelectPlanNode(value = 0)
        if self.not_flag:
            left = plan
            plan = SelectPlanNode(value = 'not')
            plan.child.append(left)
        return (statement, plan)
        
    
class Select(object):
    def __init__(self, tokens):
        where_id = tokens.as_list().index('WHERE')
        temp_tables = []
        i = 3
        while (i < where_id):
            if tokens[i] == "USE":
                i += 2
                temp_tables[-1][1] = tokens[i].name
            else:
                temp_tables.append([tokens[i].name, None])
            i+=1
        self.tables = {}
        for t in temp_tables:
            self.tables[t[0]] = t[1]
        print(tokens)
        if tokens[-4] == 'AND':
            self.expr = tokens[-3]
            self.expr_meta = tokens[-5]
        else:
            self.expr_meta = None
            self.expr = tokens[-3]
        self.n = tokens[-1].value

lparen = pp.Suppress("(")
rparen = pp.Suppress(")")
dot = pp.Suppress(".")
comma = pp.Suppress(",")

and_ = pp.CaselessKeyword("AND")
or_ = pp.CaselessKeyword("OR")
not_ = pp.CaselessKeyword("NOT")
contains_ = pp.CaselessKeyword("CONTAINS")
above_ = pp.CaselessKeyword("ABOVE")
left_ = pp.CaselessKeyword("LEFT")
visual_ = pp.CaselessKeyword("VISUALLY_SIMILAR")
semantic_ = pp.CaselessKeyword("SEMANTICALLY_SIMILAR")

select_ = pp.CaselessKeyword("SELECT")
from_ = pp.CaselessKeyword("FROM")
where_ = pp.CaselessKeyword("WHERE")
image_ = pp.CaselessKeyword("IMAGE")
create_ = pp.CaselessKeyword("CREATE")
use_ = pp.CaselessKeyword("USE")
index_ = pp.CaselessKeyword("INDEX")
feature_ = pp.CaselessKeyword("FEATURE")
table_ = pp.CaselessKeyword("TABLE")
database_ = pp.CaselessKeyword("DATABASE")
limit_ = pp.CaselessKeyword("LIMIT")
feature_ = pp.CaselessKeyword("FEATURE")
show_ = pp.CaselessKeyword("SHOW")
insert_ = pp.CaselessKeyword("INSERT")
delete_ = pp.CaselessKeyword("DELETE")
values_ = pp.CaselessKeyword("VALUES")
folder_ = pp.CaselessKeyword("FOLDER")
on_ = pp.CaselessKeyword("ON")
id_ = pp.CaselessKeyword("ID")
meta_ = pp.CaselessLiteral("META")
alphaword = pp.Word(pp.alphanums + "_")
number = pp.Word(pp.nums)
string = pp.QuotedString(quoteChar="'").setParseAction(String) ^ pp.QuotedString(quoteChar='"').setParseAction(String)

operator = pp.oneOf(("=", "<>", ">", ">=", "<", "<="))