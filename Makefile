# for macOS (sorry Windows..)
addons21 = ~/Library/Application\ Support/Anki2/addons21

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
