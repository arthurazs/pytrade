# PyTRADE

Python COMTRADE reader for revision 1999.

## TODO

- [ ] Reader for revision 1991 and 2013.
- [ ] Reader for BINARY, BINARY32 and FLOAT32 types.
  - [x] BINARY
  - [ ] BINARY32
  - [ ] FLOAT32
- [ ] get_analog
  - [ ] primary
  - [ ] secondary
  - [x] default
- [ ] Unit testing.

## Quickstart

pytrade is meant to be used as a lib. The `rc` below is a mere example to show you what it does.

Tested on debian.

```bash
git clone https://github.com/arthurazs/pytrade
cd pytrade

# venv
python -m venv .venv
. .venv/bin/activate

# requirements
pip install .[dev,plot]

# if you get an error running the plots, try installing tk
sudo apt install python3.10-tk

# running the examples
rc
```

See [reader.py](pytrade/reader.py) for the example code.
