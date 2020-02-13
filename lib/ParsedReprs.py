from collections import namedtuple
from dataclasses import dataclass
METHOD_WITH_RETURN_TEMPLATE = """
    fun {}({}): {}{{}}
"""

METHOD_WITHOUT_RETURN_TEMPLATE = """
    fun {}({}){{}}
"""

TYPED_ARG_TEMPLATE = "{} : {}"


@dataclass
class ParsedArgument:
    name : str
    type : str

    def toString(self):
        return TYPED_ARG_TEMPLATE.format(self.name,self.type)

@dataclass
class ParsedMethod:
    name : str
    args : list
    hasReturn : bool
    returnType : str = None

    def argListToString(self):
        return ", ".join(map(lambda x: x.toString(),self.args))

    def argListToStringTypeless(self):
        return ", ".join(map(lambda x: x.name, self.args))

    def argListToStringVals(self):
        return ", ".join(map(lambda x: "val {}: {}".format(x.name,x.type),self.args))

    def toString(self):
        argsFormatted = self.argListToString()
        if self.hasReturn:
            return METHOD_WITH_RETURN_TEMPLATE.format(self.name,argsFormatted,self.returnType)
        else:
            return METHOD_WITHOUT_RETURN_TEMPLATE.format(self.name,argsFormatted)

def parseRawMethod(raw):
    punctuationControlled = raw.replace("(", " ").replace(")", " ").replace(":", " : ").replace(",", " ")
    words = punctuationControlled.split()
    if words[0] != "fun":
        raise Exception("Each method line must begin with fun: " + raw)
    name = words[1]
    ind = 2
    hasReturn = False
    args = []
    while ind < len(words):
        if words[ind] == ":":
            ind += 1
            hasReturn = True
            break
        if ind + 1 > len(words) or words[ind + 1] == ":":
            raise Exception("Invalid function argument format:" + raw)
        args.append(ParsedArgument(words[ind + 1], words[ind]))
        ind += 2
    returnType = None
    if hasReturn:
        if ind > len(words):
            raise Exception("Colon with no return" + raw)
        returnType = words[ind]
    return ParsedMethod(name,args,hasReturn,returnType)


@dataclass
class ParsedCu:
    className : str
    methods : list
    package : str
    args : list

    def classArgList(self):
        return ",".join(map(lambda x: "val {}: {}".format(x.name, x.type), self.args))


def parseRawCu(raw):
    lines = list(filter(lambda x: x != '', raw.splitlines()))
    package = lines[0]
    className = lines[1]
    constructorArgs = lines[2].split()
    ind = 0
    args = []
    while ind < len(constructorArgs):
        args.append(ParsedArgument(constructorArgs[ind + 1], constructorArgs[ind]))
        ind += 2
    methods = list(map(lambda x: parseRawMethod(x), lines[3:]))
    return ParsedCu(className,methods,package,args)