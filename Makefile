all:
	for f in locale/*/LC_MESSAGES/copyfilepath.po; do \
		directory="debian/gedit-plugin-copy-file-path/usr/share/`dirname $${f}`"; \
		mkdir -p $$directory; \
		msgfmt -o "$${directory}/copyfilepath.mo" $${f}; \
	done

