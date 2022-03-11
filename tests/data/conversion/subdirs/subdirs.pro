TEMPLATE = subdirs
SUBDIRS = \
    app.pro \
    lib1

SUBDIRS += narf
narf.subdir = lib2

SUBDIRS += zort
zort.file = lib3/lib3.pro
