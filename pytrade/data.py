import decimal as dec
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from os import PathLike

    from pytrade.configuration import Configuration


class Analogs:
    def __init__(
        self, timestamp: str, channels: list[str], cfg_analogs: list[str]
    ) -> None:
        self._timestamp = int(timestamp)
        self._channels = {}
        for index, channel in enumerate(cfg_analogs):
            self._channels[channel] = dec.Decimal(channels[index])

    def __str__(self) -> str:
        return f"{self._timestamp}: {self._channels}"


class Data:
    __slots__ = ("_timestamps", "_analog_samples", "_digital_samples", "_cfg")

    def __init__(
        self,
        timestamps: list[int],
        analog_samples: list["Analogs"],
        digital_samples: list[list[str]],
        cfg: "Configuration",
    ) -> None:
        self._timestamps = timestamps
        self._analog_samples = analog_samples
        self._digital_samples = digital_samples
        self._cfg = cfg

    def __str__(self) -> str:
        return (
            f"ID: {repr(self._cfg)}\n"
            f"First timestamp: {self._timestamps[0]}\n"
            f"Last timestamp: {self._timestamps[-1]}\n"
            f"Analog samples: {len(self._analog_samples)} * {self._cfg.total_analog}"
            f" = {len(self._analog_samples) * self._cfg.total_analog}\n"
            f"Digital samples: {len(self._digital_samples)} * {self._cfg.total_digital}"
            f" = {len(self._digital_samples * self._cfg.total_digital)}\n"
        )

    def __repr__(self) -> str:
        return ""

    @classmethod
    def load(cls, path: "PathLike[str]", cfg: "Configuration") -> "Data":
        if cfg.data_file_type != "ASCII":
            raise NotImplementedError(
                "Reading non-ASCII .dat files not implemented yet"
            )
        with open(path, "r") as dat_file:
            timestamps = []
            analog_samples = []
            digital_samples = []
            for _ in range(cfg.last_sample):
                _, timestamp, *channels = dat_file.readline().split(",")

                if cfg.total_channels != len(channels):
                    raise ValueError(
                        "The number of channels in .dat differs from the .cfg file"
                    )

                timestamps.append(int(timestamp))
                analog_samples.append(Analogs(timestamp, channels, cfg.analogs_order))
                # TODO Create Digitals class
                digital_samples.append(channels[cfg.total_analog :])
            return cls(timestamps, analog_samples, digital_samples, cfg)
