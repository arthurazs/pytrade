from pathlib import Path

from pytrade.configuration import Configuration
from pytrade.data import Data

filepath = Path("data")
filename = filepath / "example"
cfg_path = filename.with_suffix(".CFG")
dat_path = filename.with_suffix(".DAT")


def run() -> int:
    cfg = Configuration.load(cfg_path)
    dat = Data.load(dat_path, cfg)
    print(dat)
    return 0
