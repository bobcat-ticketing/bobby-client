SOURCE=		bob_test

PYTHON=		python3
VENV=		venv

BAD_CERT=	badcert.pem

all:

lint: $(VENV)
	$(VENV)/bin/pylint $(SOURCE)

$(VENV): requirements.txt
	$(PYTHON) -m venv $(VENV)
	$(VENV)/bin/pip install -r requirements.txt

upgrade-venv:: $(VENV)
	$(VENV)/bin/pip install -r requirements.txt --upgrade

$(BAD_CERT):
	openssl req -new -x509 -sha256 -days 1000 \
		-newkey rsa:2048 -nodes -keyout $@ \
		-subj "/CN=badcert" -out $@

test: $(BAD_CERT)
	$(VENV)/bin/green -vv

typecheck: $(VENV)
	$(VENV)/bin/mypy -s $(SOURCE)

clean:
	rm -f $(BAD_CERT)

realclean:
	rm -fr $(VENV)
