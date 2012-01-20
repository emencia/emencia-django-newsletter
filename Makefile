# Makefile for emencia.django.newsletter
#
# Aim to simplify development and release process
# Be sure you have run the buildout, before using this Makefile

NO_COLOR	= \033[0m
COLOR	 	= \033[32;01m
SUCCESS_COLOR	= \033[35;01m

all: kwalitee test clean package

package:
	@echo "$(COLOR)* Creating source package for EDN$(NO_COLOR)"
	@python setup.py sdist

test:
	@echo "$(COLOR)* Launching the tests suite$(NO_COLOR)"
	@./bin/test


kwalitee:
	@echo "$(COLOR)* Running pyflakes$(NO_COLOR)"
	-@./bin/pyflakes emencia
	@echo "$(COLOR)* Running pep8$(NO_COLOR)"
	@./bin/pep8 --count -r --exclude=migrations emencia
	@echo "$(SUCCESS_COLOR)* No kwalitee errors, congratulations $(USER) ! :)$(NO_COLOR)"

translations:
	@echo "$(COLOR)* Generating english translation$(NO_COLOR)"
	@cd emencia/django/newsletter && ../../../bin/django makemessages --extension=.html,.txt -l en
	@echo "$(COLOR)* Pushing translation to Transifex$(NO_COLOR)"
	@rm -rf .tox
	@tx push -s

clean:
	@echo "$(COLOR)* Removing useless files$(NO_COLOR)"
	@find demo emencia docs -type f \( -name "*.pyc" -o -name "\#*" -o -name "*~" \) -exec rm -f {} \;
	@rm -f \#* *~
	@rm -rf .tox


