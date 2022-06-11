TEMPLATE = lib

a.depends = install_c
a.path = /dst
a.files = /src/a
INSTALLS += a

b.depends = install_a
b.path = /dst
b.files = /src/b/
INSTALLS += b

c.path = /dst
c.files = /src/c.txt
INSTALLS += c

distinfo.depends = install_lib install_a install_b install_c
distinfo.extra = sip-distinfo --inventory /dst/inventory.txt --project-root /src
distinfo.path = /dst
INSTALLS += distinfo
