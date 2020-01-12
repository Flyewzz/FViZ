#-------------------------------------------------
#
# Project created by QtCreator 2018-09-21T12:22:02
#
#-------------------------------------------------

QT       += core gui webenginewidgets

greaterThan(QT_MAJOR_VERSION, 4): QT += widgets

VERSION = 1.0.1
QMAKE_TARGET_COMPANY = Ustinov I.
QMAKE_TARGET_PRODUCT = FViZ
QMAKE_TARGET_DESCRIPTION = System of FViZ
QMAKE_TARGET_COPYRIGHT = Igor Ustinov
TARGET = FViZ
TEMPLATE = app

CONFIG+=sdk_no_version_check

# The following define makes your compiler emit warnings if you use
# any feature of Qt which has been marked as deprecated (the exact warnings
# depend on your compiler). Please consult the documentation of the
# deprecated API in order to know how to port your code away from it.
DEFINES += QT_DEPRECATED_WARNINGS

QMAKE_CXXFLAGS_DEBUG += -pg
QMAKE_LFLAGS_DEBUG += -pg
# You can also make your code fail to compile if you use deprecated APIs.
# In order to do so, uncomment the following line.
# You can also select to disable deprecated APIs only up to a certain version of Qt.
#DEFINES += QT_DISABLE_DEPRECATED_BEFORE=0x060000    # disables all the APIs deprecated before Qt 6.0.0


 SOURCES += \
    source/color.cpp  \
    source/cell.cpp  \
    source/sysgroup.cpp

HEADERS += \
    include/color.h  \
    include/cell.h  \
    include/sysgroup.h

INCLUDEPATH += $PWD/include



FORMS += \
        mainwindow.ui \
    addelement.ui \
    about.ui \
    addsysgroup.ui \
    listoflaws.ui \
    lawssettings.ui \
    mainlist.ui

RESOURCES += \
    res.qrc \
    katex/katex.qrc
