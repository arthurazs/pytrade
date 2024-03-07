import datetime as dt
import decimal as dec
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from os import PathLike
    from typing import Sequence


class Analog:

    __slots__ = (
        "_identifier",
        "_phase",
        "_circuit_component",
        "_unit",
        "_multiplier",
        "_offset",
        "_skew",
        "_min",
        "_max",
        "_primary",
        "_secondary",
        "_is_primary",
    )

    def __init__(
        self: "Analog",
        identifier: str,
        phase: str,
        circuit_component: str,
        unit: str,
        multiplier: str,
        offset_adder: str,
        skew: str,
        minimum: str,
        maximum: str,
        primary: str,
        secondary: str,
        primary_or_secondary: str,
    ) -> None:

        self._identifier = identifier
        self._phase = phase
        self._circuit_component = circuit_component
        self._unit = unit
        self._multiplier = dec.Decimal(multiplier)
        self._offset = dec.Decimal(offset_adder)
        self._skew = dec.Decimal(skew)
        self._min = dec.Decimal(minimum)
        self._max = dec.Decimal(maximum)
        self._primary = dec.Decimal(primary)
        self._secondary = dec.Decimal(secondary)
        self._is_primary = primary_or_secondary.strip().lower() == "p"

    def __str__(self: "Analog") -> str:
        return (
            f"{self._identifier} ({self._phase}, {self._circuit_component})\n"
            f"Primary:\n > {self._is_primary} ({self._min} ~ {self._max})\n"
            f" > Primary: {self._primary}\n > Secondary: {self._secondary}\n"
            f"Skew: {self._skew} us\n"
            f"Unit: {self._unit} ({self._multiplier} * x + {self._offset})"
        )

    def convert(self: "Analog", x: dec.Decimal) -> dec.Decimal:
        return (self._multiplier * x) + self._offset

    @property
    def id(self: "Analog") -> str:
        return self._identifier

    @property
    def phase(self: "Analog") -> str:
        return self._phase

    @property
    def unit(self: "Analog") -> str:
        return self._unit

    @property
    def skew(self: "Analog") -> dec.Decimal:
        return self._skew


class Digital:

    __slots__ = ("_identifier", "_phase", "_circuit_component", "_state")

    def __init__(
        self: "Digital", identifier: str, phase: str, circuit_component: str, state: str
    ) -> None:
        self._identifier = identifier
        self._phase = phase
        self._circuit_component = circuit_component
        self._state = int(state)

    def __str__(self: "Digital") -> str:
        return (
            f"{self._identifier} ({self._phase}, {self._circuit_component})\n"
            f"State: {self._state}"
        )

    def __repr__(self: "Digital") -> str:
        return self._identifier


class DataType(Enum):
    ASCII = "ASCII"


class Configuration:
    __slots__ = (
        "_station_name",
        "_identification",
        "_revision",
        "_total_channels",
        "_total_analog",
        "_total_digital",
        "_analogs_order",
        "_analogs",
        "_digitals_order",
        "_digitals",
        "_frequency",
        "_sample_rate",
        "_last_sample",
        "_in_microseconds",
        "_start_datetime",
        "_trigger_datetime",
        "_data_file_type",
        "_multiplication_factor",
    )

    def __init__(
        self: "Configuration",
        station_name: str,
        identification: str,
        revision: str,
        total_channels: str,
        total_analog: int,
        total_digital: int,
        analogs_order: "Sequence[str]",
        analogs: dict[str, "Analog"],
        digitals_order: "Sequence[str]",
        digitals: dict[str, "Digital"],
        frequency: str,
        sample_rates: str,
        sample_rate: str,
        last_sample: str,
        start_datetime: str,
        trigger_datetime: str,
        data_file_type: str,
        multiplication_factor: str,
    ) -> None:
        self._station_name = station_name
        self._identification = identification
        self._revision = int(revision)
        self._total_channels = int(total_channels)
        self._total_analog = total_analog
        self._total_digital = total_digital
        if self._total_channels != self._total_analog + self._total_digital:
            raise ValueError(
                "Number of Total Channels != Analog Channels + Digital Channels"
            )
        self._analogs_order = analogs_order
        self._analogs = analogs
        self._digitals_order = digitals_order
        self._digitals = digitals
        self._frequency = dec.Decimal(frequency)
        if int(sample_rates) > 1:
            raise NotImplementedError(
                "COMTRADE with multiple sample rates not implemented yet"
            )
        self._sample_rate = dec.Decimal(sample_rate)
        self._last_sample = int(last_sample)
        self._in_microseconds = len(start_datetime.split(".")[-1].strip()) > 6
        self._start_datetime = dt.datetime.strptime(
            start_datetime.strip(), "%d/%m/%Y,%H:%M:%S.%f"
        )
        self._trigger_datetime = dt.datetime.strptime(
            trigger_datetime.strip(), "%d/%m/%Y,%H:%M:%S.%f"
        )
        self._data_file_type = DataType(data_file_type)
        self._multiplication_factor = dec.Decimal(multiplication_factor)

    @property
    def start_datetime(self: "Configuration") -> dt.datetime:
        return self._start_datetime

    @property
    def trigger_datetime(self: "Configuration") -> dt.datetime:
        return self._trigger_datetime

    @property
    def data_file_type(self: "Configuration") -> DataType:
        return self._data_file_type

    @property
    def in_microseconds(self: "Configuration") -> bool:
        return self._in_microseconds

    @property
    def multiplication_factor(self: "Configuration") -> dec.Decimal:
        return self._multiplication_factor

    @property
    def total_channels(self: "Configuration") -> int:
        return self._total_channels

    @property
    def total_analog(self: "Configuration") -> int:
        return self._total_analog

    @property
    def total_digital(self: "Configuration") -> int:
        return self._total_digital

    @property
    def analogs_order(self: "Configuration") -> "Sequence[str]":
        return self._analogs_order

    @property
    def analogs(self: "Configuration") -> dict[str, "Analog"]:
        return self._analogs

    @property
    def digitals_order(self: "Configuration") -> "Sequence[str]":
        return self._digitals_order

    @property
    def digitals(self: "Configuration") -> dict[str, "Digital"]:
        return self._digitals

    @property
    def frequency(self: "Configuration") -> dec.Decimal:
        return self._frequency

    @property
    def last_sample(self: "Configuration") -> int:
        return self._last_sample

    def __str__(self: "Configuration") -> str:
        return (
            f"Station name: {self._station_name}\n"
            f"Recording device identification: {self._identification}\n"
            f"COMTRADE standard revision year: {self._revision}\n\n"
            f"Number of analog channels: {self._total_analog}\n"
            f"\tChannels: {self._analogs}\n\n"
            f"Number of digital channels: {self._total_digital}\n"
            f"\tChannels: {self._digitals}\n\n"
            f"Line frequency: {self._frequency} Hz\n\n"
            f"Sample rate: {self._sample_rate} Hz\n"
            f"Last sample number: {self._last_sample}\n\n"
            f"Datetime of the first data value: {self._start_datetime}\n"
            f"Trigger datetime: {self._trigger_datetime}\n\n"
            f"Data file type: {self._data_file_type}\n\n"
            f"Multiplication factor for "
            f"the time differential: {self._multiplication_factor}"
        )

    @property
    def id(self: "Configuration") -> str:
        return self._station_name + "_" + self._identification

    @classmethod
    def load(cls: type["Configuration"], path: "PathLike[str]") -> "Configuration":
        with open(path, "r") as cfg_file:
            station_name, rec_dev_id, rev_year = cfg_file.readline().split(",")
            tt, ta_string, td_string = cfg_file.readline().split(",")
            if "A" not in ta_string.upper():
                raise ValueError(f"{ta_string} missing letter 'A'")
            if "D" not in td_string.upper():
                raise ValueError(f"{td_string} missing letter 'D'")
            ta = int(ta_string[:-1])
            td = int(td_string.strip()[:-1])

            analogs_order = []
            analogs = {}
            for _ in range(ta):
                (
                    _,
                    ch_id,
                    ph,
                    ccbm,
                    uu,
                    a,
                    b,
                    skew,
                    min_,
                    max_,
                    primary,
                    secondary,
                    p_or_s,
                ) = cfg_file.readline().split(",")
                analogs_order.append(ch_id)
                analogs[ch_id] = Analog(
                    ch_id,
                    ph,
                    ccbm,
                    uu,
                    a,
                    b,
                    skew,
                    min_,
                    max_,
                    primary,
                    secondary,
                    p_or_s,
                )

            digitals_order = []
            digitals = {}
            for _ in range(td):
                _, ch_id, ph, ccbm, y = cfg_file.readline().split(",")
                digitals_order.append(ch_id)
                digitals[ch_id] = Digital(ch_id, ph, ccbm, y)

            lf = cfg_file.readline()

            nrates = cfg_file.readline()
            samp, endsamp = cfg_file.readline().split(",")

            startdt = cfg_file.readline()
            tdt = cfg_file.readline()

            ft = cfg_file.readline().strip()

            timemult = cfg_file.readline()

            return cls(
                station_name,
                rec_dev_id,
                rev_year,
                tt,
                ta,
                td,
                analogs_order,
                analogs,
                digitals_order,
                digitals,
                lf,
                nrates,
                samp,
                endsamp,
                startdt,
                tdt,
                ft,
                timemult,
            )
