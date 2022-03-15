TEMPLATE = app
TARGET = myapp
QT += qml quick
CONFIG += qmltypes
QML_IMPORT_NAME = DonkeySimulator
QML_IMPORT_MAJOR_VERSION = 1
HEADERS += donkeyengine.h
SOURCES += donkeyengine.cpp \
           main.cpp
RESOURCES += donkeyassets.qrc
