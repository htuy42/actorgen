import sys

from lib.CommonExternals import genOuterClass, genImpl
from lib.LocalActors import genControlClass
from lib.ParsedReprs import parseRawCu

f = open(sys.argv[1],"r")

contents = f.read()

a = parseRawCu(contents)

name = a.className

impl = open("{}Impl.kt".format(name), "w+")
ext = open("{}Ext.kt".format(name), "w+")
control = open("{}Control.kt".format(name), "w+")

impl.write(genImpl(a))
ext.write(genOuterClass(a))
control.write(genControlClass(a))