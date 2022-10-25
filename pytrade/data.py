import decimal as dec
from typing import TYPE_CHECKING, NamedTuple

if TYPE_CHECKING:
    from os import PathLike
    from typing import Iterator, Sequence

    from pytrade.configuration import Configuration


class Sample(NamedTuple):
    timestamp: int
    analogs: "Sequence[dec.Decimal]"
    digitals: "Sequence[dec.Decimal]"


class ChannelsSample(NamedTuple):
    timestamp: dec.Decimal
    samples: "Sequence[dec.Decimal]"


class ChannelSample(NamedTuple):
    timestamp: dec.Decimal
    sample: dec.Decimal


class Channels:
    __slots__ = ()
    _timestamp = 0
    _channels: dict[str, dec.Decimal] = {}

    @property
    def samples(self: "Channels") -> "Sequence[dec.Decimal]":
        return tuple(self._channels.values())

    @property
    def timestamp(self: "Channels") -> int:
        return self._timestamp

    def convert_timestamp(
        self: "Channels", multiplication_factor: dec.Decimal, in_microseconds: bool
    ) -> dec.Decimal:
        fraction: dec.Decimal = 1_000 * (1_000**in_microseconds)
        return (self._timestamp * multiplication_factor) / fraction

    def __getitem__(self: "Channels", item: str) -> dec.Decimal:
        return self._channels[item]

    def __str__(self: "Channels") -> str:
        return repr(self)

    def __repr__(self: "Channels") -> str:
        return f"{self.timestamp}: {self.samples}"


class Digitals(Channels):
    def __init__(
        self: "Digitals",
        timestamp: str,
        channels: "Sequence[str]",
        cfg_total_analog: int,
        cfg_digitals_order: "Sequence[str]",
    ) -> None:
        self._timestamp = int(timestamp)
        self._channels = {}
        for index, channel in enumerate(cfg_digitals_order):
            self._channels[channel] = dec.Decimal(channels[cfg_total_analog + index])


class Analogs(Channels):
    def __init__(
        self: "Analogs",
        timestamp: str,
        channels: "Sequence[str]",
        cfg_analogs_order: "Sequence[str]",
    ) -> None:
        self._timestamp = int(timestamp)
        self._channels = {}
        for index, channel in enumerate(cfg_analogs_order):
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

    def get_samples(self: "Data") -> "Iterator[Sample]":
        for count, (analogs, digitals) in enumerate(
            zip(self._analog_samples, self._digital_samples)
        ):
            yield Sample(analogs.timestamp, analogs.samples, digitals.samples)
            if count > 10:
                break

    @staticmethod
    def _get_raw_samples(
        all_samples: "Sequence[Channels]",
    ) -> "Iterator[tuple[int, Sequence[dec.Decimal]]]":
        for samples in all_samples:
            yield samples.timestamp, samples.samples

    @staticmethod
    def _get_raw_samples_by(
        item: str, all_samples: "Sequence[Channels]"
    ) -> "Iterator[tuple[int, dec.Decimal]]":
        for sample in all_samples:
            yield sample.timestamp, sample[item]

    def get_raw_analogs(self: "Data") -> "Iterator[tuple[int, Sequence[dec.Decimal]]]":
        for timestamp, samples in self._get_raw_samples(self._analog_samples):
            yield timestamp, samples

    def get_raw_analogs_by(
        self: "Data", item: str
    ) -> "Iterator[tuple[int, dec.Decimal]]":
        for timestamp, sample in self._get_raw_samples_by(item, self._analog_samples):
            yield timestamp, sample

    def get_analogs(
        self: "Data", channels: "Sequence[str]"
    ) -> "Iterator[Sequence[dec.Decimal]]":
        factor = self.cfg.multiplication_factor
        in_us = self.cfg.in_microseconds
        for samples in self._analog_samples:
            selected_samples: list[dec.Decimal] = []
            # TODO Add support to get ALL channels
            for channel in channels:
                convert = self.cfg.analogs[channel].convert
                selected_samples.append(convert(samples[channel]))
            # TODO Improve return typing
            yield samples.convert_timestamp(factor, in_us), *selected_samples

    def get_analogs_by(self: "Data", item: str) -> "Iterator[ChannelSample]":
        convert = self.cfg.analogs[item].convert
        factor = self.cfg.multiplication_factor
        in_us = self.cfg.in_microseconds
        for sample in self._analog_samples:
            yield ChannelSample(
                sample.convert_timestamp(factor, in_us), convert(sample[item])
            )

    def get_digitals_by(
        self: "Data", item: str
    ) -> "Iterator[tuple[dec.Decimal, dec.Decimal]]":
        factor = self.cfg.multiplication_factor
        in_us = self.cfg.in_microseconds
        for sample in self._digital_samples:
            yield sample.convert_timestamp(factor, in_us), sample[item]

    def get_raw_digitals(self: "Data") -> "Iterator[tuple[int, Sequence[dec.Decimal]]]":
        for timestamp, samples in self._get_raw_samples(self._digital_samples):
            yield timestamp, samples

    def get_raw_digitals_by(
        self: "Data", item: str
    ) -> "Iterator[tuple[int, dec.Decimal]]":
        for timestamp, sample in self._get_raw_samples_by(item, self._digital_samples):
            yield timestamp, sample

    @property
    def summary(self: "Data") -> str:
        return (
            f"ID: {repr(self._cfg)}\n"
            f"First timestamp: {self._timestamps[0]}\n"
            f"Last timestamp: {self._timestamps[-1]}\n"
            f"Analog samples: {len(self._analog_samples)} * {self._cfg.total_analog}"
            f" = {len(self._analog_samples) * self._cfg.total_analog}\n"
            f"Digital samples: {len(self._digital_samples)} * {self._cfg.total_digital}"
            f" = {len(self._digital_samples) * self._cfg.total_digital}\n"
        )

    @classmethod
    def load(cls: type["Data"], path: "PathLike[str]", cfg: "Configuration") -> "Data":
        """Loads .dat file. Expects a .cfg object.

        Args:
            path: Path to the .dat file.
            cfg: Loaded .cfg file.

        Returns:
            Loaded .dat object.

        Raises:
            ValueError: If the number of channels in .dat differs from .cfg.
        """
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
                digital_samples.append(
                    Digitals(timestamp, channels, cfg.total_analog, cfg.digitals_order)
                )
            return cls(timestamps, analog_samples, digital_samples, cfg)
