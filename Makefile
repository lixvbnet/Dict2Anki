# for macOS (sorry Windows..)
addons21 = ~/Library/Application\ Support/Anki2/addons21

install:
	@echo "Creating symbolic link..."
	ln -sf $(PWD)/Dict2Anki $(addons21)/

install_test_addon:
	@echo "Creating symbolic link..."
	ln -sf $(PWD)/test_addon $(addons21)/