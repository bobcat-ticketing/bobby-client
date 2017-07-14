SOURCE=		bobby_client

PYTHON=		python3
VENV=		venv
GREEN=		$(VENV)/bin/green -vv

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
	$(GREEN)

test-authentication: $(BAD_CERT)
	$(GREEN) $(SOURCE)/test_authentication*.py

test-device:
	$(GREEN) $(SOURCE)/test_device*.py

test-product:
	$(GREEN) $(SOURCE)/test_product*.py

test-ticket:
	$(GREEN) $(SOURCE)/test_ticket*.py

test-validation:
	$(GREEN) $(SOURCE)/test_validation*.py

test-inspection:
	$(GREEN) $(SOURCE)/test_inspection*.py

test-lifecycle:
	$(GREEN) $(SOURCE)/test_lifecycle*.py

typecheck: $(VENV)
	$(VENV)/bin/mypy --ignore-missing-imports $(SOURCE)

clean:
	rm -f $(BAD_CERT)

realclean:
	rm -fr $(VENV)
