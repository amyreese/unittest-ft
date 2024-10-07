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
$ unittest-ft <module>
...

----------------------------------------------------------------------
Ran 7 tests in 497.55ms (saved 0.41ms)
```

If you can spare the time/cores, run a randomized stress test:

```py
$ unittest-ft --randomize --stress-test <module>
...

----------------------------------------------------------------------
Ran 70 tests in 1.306s (saved 10.679s)
```


License
-------

unittest-ft is copyright Amethyst Reese, and licensed under the MIT license.
