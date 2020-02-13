from lib.CommonExternals import genAsyncMethod, genSyncMethod

CONTROL_CLASS_TEMPLATE = """

package {}

import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.channels.Channel
import kotlinx.coroutines.launch
import kotlin.coroutines.CoroutineContext
import nl.komponents.kovenant.Kovenant.deferred
import nl.komponents.kovenant.Deferred
import {}.{}Ext
import {}.{}Impl
import kotlinx.coroutines.Dispatchers
import com.htuy.actors.ControlSchedulable

// Generated code, not to be manually modified.
class {}Controller({}context : CoroutineContext) : {}Ext{{
    val callChannel : Channel<Call> = Channel<Call>()
    val schedulable = ControlSchedulable()
    val inner = {}Impl({}schedulable)
    val scope = CoroutineScope(context)
    var isAlive = true
    init{{
        inner.initialize()
        scope.launch{{
            while(isAlive){{
                schedulable.resolveQueue()
                val call = callChannel.receive()
                if(false){{
                    // Nonsense branch, ignore
                }} {} else {{
                    throw IllegalStateException("Unrecognized call type $call")
                }}
            }}
        }}
    }}
    sealed class Call{{
        {}
    }}
    fun shutdown(){{
        isAlive = false
    }}
    
    {}
}}
"""

ASYNC_METHOD_BODY_TEMPLATE = """{{
        callChannel.offer(Call.{}CallA({},context,cb))
}}"""

SYNC_METHOD_BODY_TEMPLATE = """{{
        val def = deferred<{},Exception>()
        callChannel.offer(Call.{}CallS({},def))
        {} def.promise.get()
}}"""


def genAsyncs(methods):
    return "\n".join(
        map(lambda x: "override " + genAsyncMethod(x, ASYNC_METHOD_BODY_TEMPLATE.format(x.name, x.argListToStringTypeless())),
            methods))


def genSyncs(methods):
    res = []
    for method in methods:
        if method.hasReturn:
            retType = method.returnType
            ret = "return "
        else:
            retType = "Boolean"
            ret = ""
        res.append("override " + genSyncMethod(method, SYNC_METHOD_BODY_TEMPLATE.format(retType, method.name,
                                                                          method.argListToStringTypeless(), ret)))
    return "\n".join(res)


CALL_CLASS_A_TEMPLATE = "data class {}CallA({}, val context: CoroutineContext, val cb : ({})->Unit) : Call()"
CALL_CLASS_S_TEMPLATE = "data class {}CallS({}, val def : Deferred<{},Exception>) : Call()"


def genClasses(cu):
    res = []
    for method in cu.methods:
        if method.hasReturn:
            retTypeA = method.returnType
            retTypeS = method.returnType
        else:
            retTypeA = ""
            retTypeS = "Boolean"
        res.append(CALL_CLASS_S_TEMPLATE.format(method.name, method.argListToStringVals(), retTypeS))
        res.append(CALL_CLASS_A_TEMPLATE.format(method.name, method.argListToStringVals(), retTypeA))
    return "\n".join(res)


BRANCH_TEMPLATE = """else if(call is Call.{}Call{}){{
    {}
}}"""

BRANCH_CONTENTS_A_RET = """val res = inner.{}({})
launch(call.context){{call.cb(res)}}"""

BRANCH_CONTENTS_A_NO_RET = """inner.{}({})
launch(call.context){{call.cb()}}"""

BRANCH_CONTENTS_S_RET = "call.def.resolve(inner.{}({}))"

BRANCH_CONTENTS_S_NO_RET = """inner.{}({})
call.def.resolve(true)"""


def genBranches(cu):
    res = []
    rets = [BRANCH_CONTENTS_A_RET, BRANCH_CONTENTS_S_RET]
    nrets = [BRANCH_CONTENTS_A_NO_RET, BRANCH_CONTENTS_S_NO_RET]
    for method in cu.methods:
        callContents = ", ".join(map(lambda x: "call.{}".format(x.name), method.args))
        if method.hasReturn:
            use = rets
        else:
            use = nrets
        for i, elt in enumerate(use):
            compiled = elt.format(method.name, callContents)
            letter = "A"
            if i == 1:
                letter = "S"
            res.append(BRANCH_TEMPLATE.format(method.name, letter, compiled))
    return "".join(res)


def genControlClass(cu):
    if len(cu.args) != 0:
        args = cu.classArgList() + ", "
        argPass = ",".join(map(lambda x: x.name, cu.args)) + ", "
    else:
        args = ""
        argPass = ""
    methods = "\n".join([genAsyncs(cu.methods), genSyncs(cu.methods)])
    classes = genClasses(cu)
    branches = genBranches(cu)
    return CONTROL_CLASS_TEMPLATE.format(cu.package, cu.package, cu.className, cu.package, cu.className, cu.className,
                                         args, cu.className, cu.className, argPass, branches, classes, methods)
