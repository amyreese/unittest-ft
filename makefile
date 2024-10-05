PKG:=unittest_ft
EXTRAS:=dev

UV:=$(shell uv --version)
ifdef UV
	VENV:=uv venv
	PIP:=uv pip
else
	VENV:=python -m venv
	PIP:=python -m pip
endif

install:
	$(PIP) install -Ue .[$(EXTRAS)]

.venv:
	$(VENV) .venv

venv: .venv
	source .venv/bin/activate && make install
	echo 'run `source .venv/bin/activate` to activate virtualenv'

test:
	python -m unittest_ft $(PKG).tests
	python -m mypy -p $(PKG)

lint:
	python -m flake8 $(PKG)
	python -m ufmt check $(PKG)

format:
	python -m ufmt format $(PKG)

clean:
	rm -rf .mypy_cache build dist html *.egg-info

distclean: clean
	rm -rf .venv
