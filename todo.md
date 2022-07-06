# todo

## performance

60 seconds for tests with cold cache

8 seconds for tests with warm cache

&rarr; something is slow

cache is in /run/user/$UID/qmake2cmake_cache/cache.json or similar

this is the cache for src/qmake2cmake/condition_simplifier.py

how often is it committed to disk?

use something better?

* sqlite
  * too complex. we only need a key-value store
* https://docs.python.org/3/library/dbm.html
  * faster than sqlite
  * in python stdlib
