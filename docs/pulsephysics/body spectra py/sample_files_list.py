"""This module reads sample files from a dataset in order to provide it to the 
spectrogram generator.
"""
import itertools
from dataclasses import dataclass
from pathlib import Path
from typing import List

import pandas as pd

from spectrogram_images.directory_manager import DirectoryManager


@dataclass
class SampleFile:
    """Container for information about a sample file (path and sample_rate)."""

    path: Path
    sample_rate: float


class SampleFileList:
    """This class contains a list of SampleFile(s) that are found at a "results" directory
    within a dataset path given by a DirectoryManager.
    """

    def __init__(self, dir_manager: DirectoryManager) -> None:
        """Reads all sample files from a "results" folder within a datasets root path,
        given by the dir_manager.

        :param dir_manager: Provides a root path and folder structure of a dataset.
        :type dir_manager: DirectoryManager
        :raises FileNotFoundError: If there is no samples file in the datasets "result" path.
        """
        self.dir_manager = dir_manager
        self.sample_files = []

        # Filter files by generated sample rates
        for file_path in self.dir_manager.path_results.iterdir():
            if (
                file_path.stem.startswith("result")
                and file_path.is_file()
                and file_path.suffix != ".png"
                and file_path.suffix != ".txt"
            ):
                split = file_path.stem.split("_")
                sample_rate = float(split[split.index("bw") + 1])
                # if sample_rate not in self.sample_files_per_rate:
                #     self.sample_files_per_rate[sample_rate] = []
                # self.sample_files_per_rate[sample_rate].append(filename)
                self.sample_files.append(
                    SampleFile(
                        path=file_path,
                        sample_rate=sample_rate,
                    )
                )

        if not self.sample_files:
            raise FileNotFoundError(
                f"No valid file found in {self.dir_manager.path_results}"
            )

    def get_wo_usrp_txrx_loop(self) -> List[SampleFile]:
        """Filter out all samples where the noise_lvl is flagged with "usrp_txrx_loop".

        Returns:
            List[SampleFile]: All sample files that does not require a usrp to generate it
        """

        def read_labels(filename: str, rate: float) -> pd.DataFrame:
            label_filename = filename.replace("result_frame_", "labels_") + ".csv"
            return pd.read_csv(
                self.dir_manager.path_merged_frames
                / ("bw_" + str(int(rate / 1e6)) + "e6")
                / label_filename
            )

        def usrp_flag(sample_file: SampleFile) -> bool:
            df_labels = read_labels(sample_file.path.name, sample_file.sample_rate)
            usrp_flag = bool()
            if not df_labels.empty:
                usrp_flag = df_labels.iloc[-1]["noise_lvl"] == "usrp_txrx_loop"
            else:
                # For empty frames make flag half of them generated by usrp loop
                usrp_flag = True  # bool(random.getrandbits(1))
            return usrp_flag

        sample_files_wo_usrp_txrx_loop = list(
            itertools.filterfalse(
                usrp_flag,
                self.sample_files,
            )
        )

        return sample_files_wo_usrp_txrx_loop