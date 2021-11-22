import types


def hashable(v):
    """Determine whether `v` can be hashed."""
    try:
        hash(v)
    except TypeError:
        return False
    return True


def isFuncOrMethod(obj):
    return isinstance(
        obj,
        (
            types.FunctionType,
            types.BuiltinFunctionType,
            types.MethodType,
            types.BuiltinMethodType))


def disconnectSignals(*signals):
    for sig in signals:
        try : sig.disconnect()
        except Exception: pass
