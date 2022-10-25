# PyTRADE

Python COMTRADE reader for revision 1999.

## TODO

- [ ] Reader for revision 1991 and 2013.
- [ ] Reader for BINARY, BINARY32 and FLOAT32 types.
- [ ] Unit testing.

## Quickstart

pytrade is meant to be used as a lib. The `poetry run rc` below is a mere example to show you what it does.

```bash
git clone https://github.com/arthurazs/pytrade
cd pytrade

# requirements
pip3.10 install poetry
poetry install --without dev          # for regular pytrade
poetry install --without dev -E plot  # for plotting the examples

# if you get an error running the plots, try installing tk
apt install python3.10-tk

# running the examples
poetry run rc
```

See [reader.py](pytrade/reader.py) for the code ran.
