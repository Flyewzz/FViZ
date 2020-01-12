include(gtest_dependency.pri)

TEMPLATE = app
CONFIG += console
CONFIG -= app_bundle
CONFIG += thread
CONFIG -= qt

INCLUDEPATH += ../include


HEADERS += \
        ../include/sysgroup.h \
        sysgroup_test.h

SOURCES += \
        main.cpp  \
        ../source/sysgroup.cpp
