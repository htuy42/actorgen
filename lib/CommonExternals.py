ASYNC_METHOD_TEMPLATE = """
    fun {}A({}, context: CoroutineContext {}, cb : ({}) -> Unit){}"""



def genAsyncMethod(method,body=""):
    if method.hasReturn:
        returnType = method.returnType
    else:
        returnType = ""
    if body == "":
        ctx = "= Dispatchers.Unconfined"
    else:
        ctx = ""
    return ASYNC_METHOD_TEMPLATE.format(method.name, method.argListToString(), ctx, returnType, body)

SYNC_METHOD_TEMPLATE = """
    fun {}S({}){}{}"""



def genSyncMethod(method,body=""):
    if method.hasReturn:
        returnType = ": " + method.returnType
    else:
        returnType = ""
    return SYNC_METHOD_TEMPLATE.format(method.name, method.argListToString(), returnType, body)


OUTER_INTERFACE_TEMPLATE = """

package {}
import kotlin.coroutines.CoroutineContext
import kotlinx.coroutines.Dispatchers

// Generated code, not to be manually modified.
interface {}Ext{{
    {}
}}

"""


def genOuterClass(cu):
    syncs = "\n".join(map(lambda x: genSyncMethod(x), cu.methods))
    asyncs = "\n".join(map(lambda x: genAsyncMethod(x), cu.methods))
    return OUTER_INTERFACE_TEMPLATE.format(cu.package, cu.className, "\n".join([syncs, asyncs]))


IMPL_CLASS_TEMPLATE = """
package {}
import com.htuy.actors.ControlSchedulable

class {}Impl({}val scheduler : ControlSchedulable){{
    fun initialize(){{}}
    {}
}}
"""


def genImpl(cu):
    if len(cu.args) != 0:
        args = cu.classArgList() + ", "
    else:
        args = ""
    return IMPL_CLASS_TEMPLATE.format(cu.package, cu.className, args,"".join(map(lambda x: x.toString(),cu.methods)))
