import types


# PURE PYTHON HELPERS *********************************************************

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


# ** Intervals helpers **

def sortIntervalBySize(*intervalSize):
    return sorted(
            intervalSize,
            key=lambda x: abs(x[1] - x[0]),
            reverse=True)

def canContainInterval(intervalToContain, *intervals):

    def getIntervalSize(interval):
        return abs(interval[1] - interval[0])
    size = getIntervalSize(intervalToContain)
    ret = []
    for interval in intervals:
        if getIntervalSize(interval) >= size:
            ret.append(interval)
    return ret


# QT HELPERS ******************************************************************

def disconnectSignals(*signals):
    for sig in signals:
        try:
            sig.disconnect()
        except Exception:
            pass


def deleteSubWidgetByType(parentWidget, *widgetTypes):
    for widgetType in widgetTypes:
        for widget in parentWidget.findChildren(widgetType):
            widget.setParent(None)
            widget.setVisible(False)
            widget.deleteLater()
