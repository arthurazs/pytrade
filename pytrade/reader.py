from pathlib import Path

from pytrade.configuration import Configuration
from pytrade.data import Data

filepath = Path("data")
filename = filepath / "1999sub0"
cfg_path = filename.with_suffix(".CFG")
dat_path = filename.with_suffix(".DAT")


def examples(dat: Data) -> None:

    print(dat.summary)

    for count, (timestamp, channels_sample) in enumerate(dat.get_raw_analogs()):
        if count > 5:
            break
        print("all analogs:", timestamp, channels_sample)
    for count, (timestamp, channel_samples) in enumerate(dat.get_raw_analogs_by("IAW")):
        if count > 5:
            break
        print("IAW analogs:", timestamp, channel_samples)
    print()
    for count, (timestamp, channels_sample) in enumerate(dat.get_raw_digitals()):
        if count > 5:
            break
        print("all digitals:", timestamp, channels_sample)
    for count, (timestamp, channel_samples) in enumerate(
        dat.get_raw_digitals_by("TRIP")
    ):
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

    for count, (timestamp, analog_channel_samples) in enumerate(dat.get_raw_analogs()):
        if count > 5:
            break
        string = f"{timestamp}: "
        for name, sample in zip(dat.cfg.analogs_order, analog_channel_samples):
            string += f"{name} {sample} | "
        print(string)


def plot(dat: Data) -> None:
    try:
        import matplotlib.pyplot as plt  # type: ignore[import]
    except ModuleNotFoundError:
        print("\nmatplotlib not found\nplotting will be skipped...")
        return
    import pandas as pd  # type: ignore[import]
    import seaborn as sns  # type: ignore[import]

    channels = {
        "current": ("IAW", "IBW", "ICW"),
        "voltage": ("VAY", "VBY", "VCY"),
    }

    df_analog = pd.DataFrame()
    for channel_type, channel_names in channels.items():
        for channel_name in channel_names:
            unit = dat.cfg.analogs[channel_name].unit
            new = pd.DataFrame(
                dat.get_analogs_by(channel_name),
                columns=[
                    "ms",
                    "V" if unit != "A" else "A",
                ],
            )
            new["channel"] = channel_name
            new["type"] = channel_type
            df_analog = pd.concat((df_analog, new), ignore_index=True)
    df_analog["V"] *= 1_000

    df_digital = pd.DataFrame(
        dat.get_digitals_by("TRIP"),
        columns=["ms", "TRIP"],
    )

    palette = "Blues_r" if False else "colorblind"
    sns.set_theme(
        font="Times New Roman",
        palette=palette,
    )

    fig, axes = plt.subplots(
        3, figsize=(7, 6), gridspec_kw={"height_ratios": [3, 3, 1]}
    )

    sns.lineplot(
        ax=axes[0],
        x="ms",
        y="A",
        hue="channel",
        data=df_analog.query("type == 'current'"),
    )
    sns.lineplot(
        ax=axes[1],
        x="ms",
        y="V",
        hue="channel",
        data=df_analog.query("type == 'voltage'"),
    )
    ax = sns.lineplot(ax=axes[2], x="ms", y="TRIP", data=df_digital)

    ax.set_yticks([0, 1])
    ax.set_yticklabels(["False", "True"])

    plt.subplots_adjust(left=0.12, right=0.99, top=0.99, bottom=0.1, hspace=0.01)
    # plt.savefig('figura.pdf', dpi=100, bbox_inches='tight')
    plt.show()


def to_csv_analog(dat: "Data") -> None:
    from time import time

    start = time()
    import pandas as pd

    current_channels = tuple(f"I{phase}W" for phase in ("A", "B", "C"))
    voltage_channels = tuple(f"V{phase}Y" for phase in ("A", "B", "C"))
    channels = current_channels + voltage_channels

    print("Building dataframe...")
    df = pd.DataFrame(dat.get_analogs(channels), columns=["us", *channels])

    for channel in channels:
        df[channel] *= 1_000

    for channel in voltage_channels:
        df[channel] *= 100

    df["us"] = df["us"] * 1_000

    # for channel in ("us",) + channels:
    for channel in ("us",) + channels:
        df[channel] = df[channel].astype(int)
    print("Saving to .csv file...")
    new_file = filename.parent / (filename.name + "_analog")
    # df.drop("us", axis=1).iloc[::2].to_csv(new_file.with_suffix(".csv"), index=False)
    df.drop("us", axis=1).to_csv(new_file.with_suffix(".csv"), index=False)
    # df.to_csv(new_file.with_suffix(".csv"), index=False)
    print(f"Done in {(time() - start) * 1_000:.3f} ms...")


def to_csv_digital(dat: "Data") -> None:
    from time import time

    start = time()
    import pandas as pd

    channels = ("TRIP", "50P1", "VB001")

    print("Building dataframe...")
    df = pd.DataFrame(dat.get_digitals(channels), columns=["us", *channels])
    df["us"] = df["us"] * 1_000

    # only save different rows
    df = df[df.groupby('TRIP')['50P1'].diff().ne(0)]

    print("Saving to .csv file...")
    new_file = filename.parent / (filename.name + "_digital")
    df.to_csv(new_file.with_suffix(".csv"), index=False)
    print(f"Done in {(time() - start) * 1_000:.3f} ms...")


def run() -> int:
    cfg = Configuration.load(cfg_path)
    dat = Data.load(dat_path, cfg)
    # examples(dat)
    # to_csv_analog(dat)
    # plot(dat)
    to_csv_digital(dat)
    return 0


if __name__ == "__main__":
    exit(run())
