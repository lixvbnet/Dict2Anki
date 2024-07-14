# for macOS (sorry Windows..)
addons21 = ~/Library/Application\ Support/Anki2/addons21

.PHONY: install uninstall install_test_addon uninstall_test_addon clean fix_qt_versions build publish


install:
	@echo "Creating symbolic link..."
	ln -sf $(PWD) $(addons21)/

uninstall:
	@echo "Deleting symbolic link..."
	rm -f $(addons21)/Dict2Anki


install_test_addon:
	@echo "Creating symbolic link..."
	ln -sf $(PWD)/test_addon $(addons21)/

uninstall_test_addon:
	@echo "Deleting symbolic link..."
	rm -f $(addons21)/test_addon


clean:
	rm -rf build/

fix_qt_versions:
	./FixQtVersions.sh

build: clean fix_qt_versions
	@echo "Building..."
	python3 deploy.py build -d build/
