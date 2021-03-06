"""@package PySideWidgetCollection.utility
@brief Useful qt utility functions
@date 2014/11/20
@version 1.0
@author Paul Schweizer
@email paulschweizer@gmx.net
"""
import os
import xml.etree.ElementTree as xml
from cStringIO import StringIO

import shiboken
import pysideuic
from PySide import QtCore, QtGui


def load_ui_type(ui_file):
    """Load a ui file for PySide.

    PySide lacks the "load_ui_type" command, so we have to convert
    the UI file to python code in-memory first and then execute it in a
    special frame to retrieve the form_class.
    """
    parsed = xml.parse(ui_file)
    widget_class = parsed.find('widget').get('class')
    form_class = parsed.find('class').text
    with open(ui_file, 'r') as f:
        o = StringIO()
        frame = {}

        pysideuic.compileUi(f, o, indent=0)
        pyc = compile(o.getvalue(), '<string>', 'exec')
        exec pyc in frame

        # Fetch the base_class and form_class based on their type
        # in the xml from designer
        base_class = eval('QtGui.%s' % widget_class)
        form_class = frame['Ui_%s' % form_class]
        return base_class, form_class
    # end reading the ui file
# end def load_ui_type


def wrapinstance(ptr, base=None):
    """Utility to convert a pointer to a Qt class instance.

    @param ptr long or Swig instance, Pointer to QObject in memory
    @param base QtGui.QWidget, (Optional) Base class to wrap with
                 (Defaults to QObject, which should handle anything)
    @return QWidget or subclass instance
    """
    if ptr is None:
        return None
    # end if
    ptr = long(ptr)
    if base is None:
        qObj = shiboken.wrapInstance(long(ptr), QtCore.QObject)
        metaObj = qObj.metaObject()
        cls = metaObj.className()
        superCls = metaObj.superClass().className()
        if hasattr(QtGui, cls):
            base = getattr(QtGui, cls)
        elif hasattr(QtGui, superCls):
            base = getattr(QtGui, superCls)
        else:
            base = QtGui.QWidget
        # end if
    # end if
    return shiboken.wrapInstance(long(ptr), base)
# end def wrapinstance


def get_cpp_pointer(widget):
    """Convert the cpp pointer of the given widget.

    @param widget the widget
    @return the cpp pointer
    """
    import shiboken
    return long(shiboken.getCppPointer(widget)[0])
# end def get_cpp_pointer


def get_ui_file_path(widget_file, widget_name):
    """Retrieve the ui file for the given widget.

    It is assumed that it is set up inside the standardized
    resource folder.
    @param widget_file the file of the widget
    @param widget_name the name of the widget
    @return the file path for the ui file
    """
    return os.path.join(os.path.dirname(widget_file),
                        'resource', '%s.ui' % widget_name)
# end def get_ui_file_path


def load_ui_bases(widget_file, widget_name):
    """Load the ui base classes.

    @param widget_file the file of the widget
    @param widget_name the name of the widget
    @return the base classes for the ui
    """
    return load_ui_type(get_ui_file_path(widget_file, widget_name))
# end def load_ui_bases


def get_css_file_path(widget_file, widget_name):
    """Retrieve the ui file for the given widget.

    It is assumed that it is set up inside the standardized
    resource folder.
    @param widget_file the file of the widget
    @param widget_name the name of the widget
    @return the file path for the ui file
    """
    return os.path.join(os.path.dirname(widget_file),
                        'resource', '%s.css' % widget_name)
# end def get_css_file_path


def set_stylesheet(widget, widget_file=None):
    """Set the style sheet to the given widget.

    general stylesheet and an additional stylesheet for
    the given widget if it exists.
    For this to work, the widget has to come with a resource folder on
    the same folder level and a .css file named like the class name.
    @param widget the widget
    @param widget_file the file location of the widget file, used to
                       retrieve the stylesheet file for the widget
    """
    general_css_file = os.path.join(os.path.dirname(__file__), 'general.css')
    with open(general_css_file, 'r') as f:
        general_css = f.read()
    # end reading the general css file

    if widget_file is not None:
        widget_css_file = get_css_file_path(widget_file,
                                            widget.__class__.__name__)
        if os.path.exists(widget_css_file):
            with open(widget_css_file, 'r') as f:
                widget_css = f.read()
            # end reading the widget's css file
            general_css += widget_css
        # end if
    # end if
    widget.setStyleSheet(general_css)
# end def set_stylesheet
