import decimal as dec
import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, NamedTuple

if TYPE_CHECKING:
    from pathlib import Path
    from typing import Iterator, Sequence

    from pytrade.configuration import Configuration

logger = logging.getLogger(__name__)

S2MS = dec.Decimal(1_000)
S2US = S2MS * S2MS


@dataclass(frozen=True, kw_only=True, slots=True)
class Sample:
    timestamp: int
    analogs: "Sequence[dec.Decimal]"
    digitals: "Sequence[dec.Decimal]"


@dataclass(frozen=True, kw_only=True, slots=True)
class ChannelsSample:
    timestamp: dec.Decimal
    samples: "Sequence[dec.Decimal]"


class ChannelSample(NamedTuple):
    timestamp: dec.Decimal
    sample: dec.Decimal



class Channels:
    __slots__ = ()
    _timestamp: int
    _channels: dict[str, dec.Decimal]
    _in_microseconds: bool

    @property
    def samples(self: "Channels") -> "Sequence[dec.Decimal]":
        return tuple(self._channels.values())

    @property
    def timestamp(self: "Channels") -> int:
        return self._timestamp

    def convert_timestamp(self: "Channels", multiplication_factor: dec.Decimal) -> dec.Decimal:
        """Return"""
        return (self._timestamp * multiplication_factor) / (S2US if self._in_microseconds else S2MS)

    def __getitem__(self: "Channels", item: str) -> dec.Decimal:
        return self._channels[item]

    def __str__(self: "Channels") -> str:
        return repr(self)

    def __repr__(self: "Channels") -> str:
        return f"{self.timestamp}: {self.samples}"


class Digitals(Channels):
    __slots__ = ("_timestamp", "_in_microseconds", "_channels")

    def __init__(
        self: "Digitals",
        *,
        timestamp: int,
        in_microseconds: bool,
        channels: "Sequence[str]",
        total_analogs: int,
        digitals_order: "Sequence[str]",
    ) -> None:
        self._timestamp = timestamp
        self._in_microseconds = in_microseconds
        self._channels = {}
        for index, channel in enumerate(digitals_order):
            self._channels[channel] = dec.Decimal(channels[total_analogs + index])


class Analogs(Channels):
    __slots__ = ("_timestamp", "_in_microseconds", "_channels")

    def __init__(
        self: "Analogs",
        *,
        timestamp: int,
        in_microseconds: bool,
        channels: "Sequence[str]",
        analogs_order: "Sequence[str]",
    ) -> None:
        self._timestamp = timestamp
        self._in_microseconds = in_microseconds
        self._channels = {}
        for index, channel in enumerate(analogs_order):
            self._channels[channel] = dec.Decimal(channels[index])


class Data:
    __slots__ = ("_timestamps", "_analog_samples", "_digital_samples", "_cfg")

    def __init__(
        self: "Data",
        timestamps: "Sequence[int]",
        analog_samples: "Sequence[Analogs]",
        digital_samples: "Sequence[Digitals]",
        cfg: "Configuration",
    ) -> None:
        self._timestamps = timestamps
        self._analog_samples = analog_samples
        self._digital_samples = digital_samples
        self._cfg = cfg

    @property
    def cfg(self: "Data") -> "Configuration":
        return self._cfg

    @property
    def timestamps(self: "Data") -> "Sequence[int]":
        return self._timestamps

    def __str__(self: "Data") -> str:
        string = "Analog Samples:\n"
        for analog in self._analog_samples:
            string += f"\t{analog.timestamp}: {analog.samples}\n"
        string += "Digital Samples:\n"
        for digital in self._digital_samples:
            string += f"\t{digital.timestamp}: {digital.samples}\n"
        return string

    def get_analogs_by(self: "Data", item: str) -> "Iterator[ChannelSample]":
        convert_analog = self.cfg.analogs[item].convert
        factor = self.cfg.multiplication_factor
        for sample in self._analog_samples:
            yield ChannelSample(
                timestamp=sample.convert_timestamp(factor),
                sample=convert_analog(sample[item]),
            )

    def get_digitals_by(self: "Data", item: str) -> "Iterator[ChannelSample]":
        factor = self.cfg.multiplication_factor
        for sample in self._digital_samples:
            yield ChannelSample(timestamp=sample.convert_timestamp(factor), sample=sample[item])

    @property
    def summary(self: "Data") -> str:
        return (
            f"ID: {self._cfg.id}\n"
            f"First timestamp: {self._timestamps[0]}\n"
            f"Last timestamp: {self._timestamps[-1]}\n"
            f"Analog samples: {len(self._analog_samples)} * {self._cfg.total_analog}"
            f" = {len(self._analog_samples) * self._cfg.total_analog}\n"
            f"Digital samples: {len(self._digital_samples)} * {self._cfg.total_digital}"
            f" = {len(self._digital_samples) * self._cfg.total_digital}\n"
        )

    @classmethod
    def load(cls: type["Data"], path: "Path", cfg: "Configuration") -> "Data":
        """Loads .dat file. Expects a .cfg object.

        Args:
            path: Path to the .dat file.
            cfg: Loaded .cfg file.

        Returns:
            Loaded .dat object.

        Raises:
            ValueError: If the number of channels in .dat differs from .cfg.
        """
        with path.open() as dat_file:
            timestamps = []
            analog_samples = []
            digital_samples = []
            for _ in range(cfg.last_sample):
                _, s_timestamp, *channels = dat_file.readline().split(",")
                timestamp = int(s_timestamp)

                if cfg.total_channels != len(channels):
                    msg = "The number of channels in .dat differs from the .cfg file"
                    raise ValueError(msg)

                timestamps.append(timestamp)
                in_us = cfg.in_microseconds
                analog_samples.append(Analogs(
                    timestamp=timestamp,
                    in_microseconds=in_us,
                    channels=channels,
                    analogs_order=cfg.analogs_order,
                ))
                digital_samples.append(Digitals(
                        timestamp=timestamp,
                        in_microseconds=in_us,
                        channels=channels,
                        total_analogs=cfg.total_analog,
                        digitals_order=cfg.digitals_order,
                ))
            return cls(timestamps, analog_samples, digital_samples, cfg)
