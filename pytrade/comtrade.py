from typing import TYPE_CHECKING

from pytrade.configuration import Configuration
from pytrade.data import Data

if TYPE_CHECKING:
    from pathlib import Path


class Comtrade:
    __slots__ = ("_cfg", "_dat")

    def __init__(self: "Comtrade", cfg: "Configuration", dat: "Data") -> None:
        self._cfg = cfg
        self._dat = dat

    @classmethod
    def load(cls: type["Comtrade"], cfg_path: "Path", dat_path: "Path") -> "Comtrade":
        cfg = Configuration.load(cfg_path)
        dat = Data.load(dat_path, cfg)
        return cls(cfg, dat)

    @property
    def cfg(self: "Comtrade") -> "Configuration":
        return self._cfg

    @property
    def dat(self: "Comtrade") -> "Data":
        return self._dat

