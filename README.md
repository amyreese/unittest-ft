# unittest-ft

Run Python tests in parallel with free threading

[![version](https://img.shields.io/pypi/v/unittest-ft.svg)](https://pypi.org/project/unittest-ft)
[![license](https://img.shields.io/pypi/l/unittest-ft.svg)](https://github.com/amyreese/unittest-ft/blob/main/LICENSE)

Alternative to the standard unittest runner that spawns a thread pool, and
runs every test individually on separate threads, in parallel, to both run tests
faster and to assist with validating the thread safety of the tested system.

unittest-ft also includes options to run "stress tests" which queues every test
to be run ten times rather than just once, as well as randomizing the test order
every time to help catch unintended test order dependencies.

This is intended for use with Python 3.13 or newer with Free Threading enabled,
but is functionally compatible back to Python 3.8 for use in multi-version CI.


Install
-------

```shell-session
$ pip install unittest-ft
```


Usage
-----

Run your test suite:

```shell-session
$ unittest-ft [<module>]
s...xx.
----------------------------------------------------------------------
Ran 7 tests in 463.69ms

OK (skipped=1, expected failures=2)
```

If you can spare the time/cores, run a randomized stress test:

```shell-session
$ unittest-ft --randomize --stress-test [<module>]
.s...xs.xsxx.xx....xxx..xsxx.x.s.x...xs.xsxx....xx...s..ss............
----------------------------------------------------------------------
Ran 70 tests in 1.240s (saved 9.988s)

OK (skipped=10, expected failures=20)
```


License
-------

unittest-ft is copyright Amethyst Reese, and licensed under the MIT license.
