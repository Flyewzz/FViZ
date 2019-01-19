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
        main.cpp \
        mainwindow.cpp \
    fizitem.cpp \
    graphview.cpp \
    addelement.cpp \
    about.cpp \
    addsysgroup.cpp \
    listoflows.cpp \
    lowssettings.cpp \
    mainlist.cpp \
    commands.cpp \
    general_settings.cpp

HEADERS += \
        mainwindow.h \
    fizitem.h \
    graphview.h \
    addelement.h \
    about.h \
    addsysgroup.h \
    listoflows.h \
    lowssettings.h \
    mainlist.h \
    commands.h \
    general_settings.h

FORMS += \
        mainwindow.ui \
    addelement.ui \
    about.ui \
    addsysgroup.ui \
    listoflows.ui \
    lowssettings.ui \
    mainlist.ui \
    general_settings.ui


DISTFILES += \
    MathJax/MathJax.js \
    Main.qml

RESOURCES += \
    res.qrc
