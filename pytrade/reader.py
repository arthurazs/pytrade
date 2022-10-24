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
    # print(dat)
    print(dat.summary)

    for count, (timestamp, channels_sample) in enumerate(dat.get_analogs()):
        if count > 5:
            break
        print("all analogs:", timestamp, channels_sample)
    for count, (timestamp, channel_samples) in enumerate(dat.get_analogs_by("IAW")):
        if count > 5:
            break
        print("IAW analogs:", timestamp, channel_samples)
    print()
    for count, (timestamp, channels_sample) in enumerate(dat.get_digitals()):
        if count > 5:
            break
        print("all digitals:", timestamp, channels_sample)
    for count, (timestamp, channel_samples) in enumerate(dat.get_digitals_by("TRIP")):
        if count > 5:
            break
        print("TRIP digitals:", timestamp, channel_samples)

    print("\nAll samples:")
    for all_sample in dat.get_samples():
        print(
            "\t",
            all_sample.timestamp,
            "\n\tAnalogs:",
            all_sample.analogs,
            "\n\tDigitals:",
            all_sample.digitals,
            "\n",
        )

    for count, (timestamp, analog_channel_samples) in enumerate(dat.get_analogs()):
        if count > 5:
            break
        string = f"{timestamp}: "
        for name, sample in zip(cfg.analogs_order, analog_channel_samples):
            string += f"{name} {sample} | "
        print(string)

    return 0


if __name__ == "__main__":
    exit(run())
