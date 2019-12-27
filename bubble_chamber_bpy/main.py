import argparse
import logging

from bubble_chamber_bpy import __version__

log = logging.getLogger(__name__)


def main():
    args = argparse.ArgumentParser(
        prog="bubble-chamber-bpy",
        description="Bubble chamber simulation in Blender + Python",
    )
    args.add_argument("--version", action="version", version=__version__)
    args = args.parse_args()

    print("Hello World!")


if __name__ == "__main__":
    main()
