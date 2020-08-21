all:

clean:
	find -name "*.pyc" -delete

pyflakes:
	@echo Running pyflakes...
	@pyflakes3 *.py

docstyle:
	@echo Running pydocstyle...
	@pydocstyle *.py

pep8:
	@echo Running pep8...
	@pycodestyle --ignore=E501 *.py

codespell:
	@echo Running codespell...
	@codespell *.py

lint:
	@echo Running pylint...
	@pylint --rcfile=.pylintrc *.py

bandit:
	@echo Running bandit...
	@bandit --quiet -r .


test: pep8 docstyle pyflakes lint codespell bandit
