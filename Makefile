default: compile clean

compile:
	nuitka --python-version=2.7 --recurse-all emucios-latest.py

clean:
	rm -rf emucios-latest.build
