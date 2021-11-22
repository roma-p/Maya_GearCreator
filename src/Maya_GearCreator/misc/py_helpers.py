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
