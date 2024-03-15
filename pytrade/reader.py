import decimal as dec
import logging
import sys
from pathlib import Path

from pytrade.configuration import Configuration
from pytrade.data import Data

logging.basicConfig(format="%(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)


def plot(dat: Data) -> None:
    try:
        import matplotlib.pyplot as plt  # type: ignore[import]
    except ModuleNotFoundError:
        logger.exception("\nmatplotlib not found\nplotting will be skipped...")
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
            new = pd.DataFrame(dat.get_analogs_by(channel_name), columns=["ms", unit])
            new["channel"] = channel_name
            new["type"] = channel_type
            df_analog = pd.concat((df_analog, new), ignore_index=True)
    df_analog["V"] = df_analog.kV * dec.Decimal(1e3)

    df_digital = pd.DataFrame(dat.get_digitals_by("TRIP"), columns=["ms", "TRIP"])

    palette = "Blues_r" if False else "colorblind"
    sns.set_theme(
        font="Times New Roman",
        palette=palette,
    )

    _, axes = plt.subplots(3, figsize=(7, 6), gridspec_kw={"height_ratios": [3, 3, 1]})

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
    plt.savefig("figura.pdf", dpi=100, bbox_inches="tight")


def main() -> int:
    filename = Path("data") / "1999sub0"
    cfg_path = filename.with_suffix(".CFG")
    dat_path = filename.with_suffix(".DAT")

    cfg = Configuration.load(cfg_path)
    dat = Data.load(dat_path, cfg)
    plot(dat)
    return 0

def debug() -> int:
    filename = Path("data") / "pub1"
    cfg_path = filename.with_suffix(".cfg")
    dat_path = filename.with_suffix(".dat")

    cfg = Configuration.load(cfg_path)
    dat = Data.load(dat_path, cfg)

    logger.info(cfg.summary)
    for channel in cfg.analogs.values():
        logger.info("%s\n", channel.summary)
    for channel in cfg.digitals.values():
        logger.info("%s\n", channel.summary)
    logger.info(dat.summary)

    return 0


if __name__ == "__main__":
    sys.exit(main())

