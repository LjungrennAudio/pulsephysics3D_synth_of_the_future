"""This is the main script for generating spectrograms for a given training data set.

:param path: root path of the spectrogram data set
:param colormap: matplotlib colormap used for spectrogram generation
:param resolution: Target resolution of the generated spectrogram images (e.g., -r 896 128 )
"""

import argparse
from pathlib import Path

from spectrogram_images.generator import make_spectrograms, Resolution
from spectrogram_images.directory_manager import DirectoryManager
from spectrogram_images.sample_files_list import SampleFileList

parser = argparse.ArgumentParser(
    description="Generate spectrogram images from the time signal sample files. ",
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
)
parser.add_argument(
    "-p",
    "--path",
    type=Path,
    required=True,
    help="root path of the spectrogram data set",
)
parser.add_argument(
    "-c",
    "--colormap",
    type=str,
    default="viridis",
    help="matplotlib colormap used for spectrogram generation",
)
parser.add_argument(
    "-r",
    "--resolution",
    nargs=2,
    default=[1024, 192],
    type=int,
    metavar=("x", "y"),
    help="Target resolution of the generated spectrogram images (e.g., -r 896 128 )",
)


if __name__ == "__main__":
    args = parser.parse_args()

    # Container of the datasets folder structure
    dir_manager = DirectoryManager(args.path)

    # Read all sample files from "results" directory
    sample_files = SampleFileList(dir_manager)

    # Exclude spectrograms that are intended to be generated by a tx-rx-loop using a specific USRP
    sample_files = sample_files.get_wo_usrp_txrx_loop()

    print("generate spectrogram images from signal sample files...")

    make_spectrograms(
        sample_files=sample_files,
        png_resolution=Resolution(x=args.resolution[0], y=args.resolution[1]),
        colormap=args.colormap,
        auto_normalization=False,
    )
