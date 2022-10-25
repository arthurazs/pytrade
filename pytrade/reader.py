from pathlib import Path

from pytrade.configuration import Configuration
from pytrade.data import Data

filepath = Path("data")
filename = filepath / "example1"
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


def run() -> int:
    cfg = Configuration.load(cfg_path)
    dat = Data.load(dat_path, cfg)
    examples(dat)
    plot(dat)
    return 0


if __name__ == "__main__":
    exit(run())
