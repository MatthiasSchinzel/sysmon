.PHONY: package  # Start a given service.
package:
	rm -rf src/dist
	cd src && python3 setup.py sdist bdist_wheel
	rm -rf build
