.PHONY: all build install test

all:
	@echo "Possible Commands"
	@echo "\tbuild: Builds Bevy2Flask"
	@echo "\tinstall: Installs via pip, needs to be built before installing"
	@echo "\ttest: Starts test server, needs Bevy2Flask to installed via pip"

build:
	@python3 -m build

install:
	@python3 -m pip uninstall Bevy2Flask -y
	@cd dist; python3 -m pip install *.whl

test:
	@cd tests; python3 -m Bevy2Flask config.json

clean:
	@rm -rfv dist
	@rm -rfv src/Bevy2Flask.egg-info
	@rm -rfv build