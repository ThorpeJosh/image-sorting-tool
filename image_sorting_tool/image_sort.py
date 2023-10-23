""" Image sorting tool code that performs the parallel sorting operation
"""
import logging
import multiprocessing
import os
import shutil
import threading
import time
import tkinter as tk
from datetime import datetime

from dateutil import parser
from PIL import Image

JPEG_EXTENSIONS = [".jpg", ".jpeg", ".jif", ".jpe", ".jfif", ".jfi", ".jp2", ".jpx"]

logger = logging.getLogger("image-sorting-tool")


class File:
    """File class for custom file metadata"""

    def __init__(self, fullpath):
        self.fullpath = os.path.abspath(fullpath)
        self.filename = os.path.split(fullpath)[1]
        self.extension = os.path.splitext(fullpath)[1]
        self.datetime = None
        self.destination_relative_path = (
            None  # Relative path such as '<month>/<day>' or 'faild_to_sort'
        )
        self.sorted_filename = None
        self.duplicate_idx = None
        self.sort_flag = False  # only sort this file if True

    def __repr__(self):
        """String to generate when __repr__ or __str__ methods are called"""
        return (
            f"File('{self.fullpath}','{self.filename}','{self.extension}', {self.datetime}, "
            f"'{self.destination_relative_path}', '{self.sorted_filename}', {self.duplicate_idx})"
        )


class ImageSort:
    """Image sorting tool"""

    # pylint: disable=too-many-instance-attributes

    def __init__(self, source_dir, destination_dir, tk_text_object):
        self.source_dir = source_dir
        self.destination_dir = destination_dir
        self.tk_text_object = tk_text_object
        self.threads_to_use = max(1, int(multiprocessing.cpu_count() / 2))
        self.manager = multiprocessing.Manager()
        self.message_queue = self.manager.Queue()
        threading.Thread(target=self.read_queue, daemon=True).start()
        self.files_list = []  # Master list of files
        self.sort_list = []  # Index positions on self.files_list
        self.other_list = []  # Index positions on self.files_list
        self.failed_list = []  # Index positions on self.files_list
        self.duplicates_list = []  # Index positions on self.files_list
        self.ext_to_sort = []
        self.rename_duplicates = False
        self.copy_unsorted = False
        self.sorting_complete = False

    def find_images(self):
        """The image finding function
        Searches for all `self.ext_to_sort` in the source directory, including all subfolders
        Returns a log message of the number of images found as well as storing the paths for later.
        """
        # Clear the category lists in case they were populated from a previous run
        self.sort_list = []
        self.other_list = []
        self.failed_list = []

        # Find all files in the source_dir
        self._find_files()

        # Extract datetimes from all files
        logger.info("Extracting datetimes in a process pool")
        with multiprocessing.Pool(processes=self.threads_to_use) as pool:
            self.files_list = pool.map(self.get_datetime, self.files_list)
        logger.debug(
            "Extracted datetimes :\n%s\n",
            "\n".join([f"{i.fullpath}:{i.datetime}" for i in self.files_list]),
        )

        # Create a hashmap to keep track of duplicate datetimes
        # Keys=datetime.datetime objects, Value=count of the Key
        duplicate_hashmap = {}

        # Categorize the input files and set their destination dir
        for index, input_file in enumerate(self.files_list):
            # Check if extension matches list user has requested to sort
            requested_sort = input_file.extension.lower().endswith(
                tuple(self.ext_to_sort)
            )
            if input_file.datetime and requested_sort:
                # Case: File is sortable and extension matches user selection

                # Check and update duplicates hashmap
                if input_file.datetime in duplicate_hashmap:
                    duplicate_hashmap[input_file.datetime] += 1
                else:
                    duplicate_hashmap[input_file.datetime] = 1

                # Set output filename and destination dir
                input_file.sorted_filename = (
                    f"{input_file.datetime.year:0>4}{input_file.datetime.month:0>2}{input_file.datetime.day:0>2}"
                    f"_{input_file.datetime.hour:0>2}{input_file.datetime.minute:0>2}{input_file.datetime.second:0>2}{input_file.extension}"
                )
                input_file.destination_relative_path = os.path.join(
                    str(input_file.datetime.year).zfill(4),
                    str(input_file.datetime.month).zfill(2),
                )
                self.sort_list.append(index)
                input_file.sort_flag = True
            elif (not input_file.datetime) and requested_sort:
                # Case: File was requested to be sorted but datetime was not extracted
                input_file.sorted_filename = input_file.filename
                input_file.destination_relative_path = "failed_to_sort"
                self.failed_list.append(index)
                input_file.sort_flag = True
            else:
                # Case: file type was not requested to be sorted
                input_file.sorted_filename = input_file.filename
                input_file.destination_relative_path = "other_files"
                self.other_list.append(index)
                if self.copy_unsorted:
                    input_file.sort_flag = True

        # Create a hashmap to keep track of duplicate index values
        # Keys=datetime.datetime objects, Value=index
        duplicate_idx_hashmap = {}
        # Generate a list of duplicates and calculate their duplicate index
        for index in self.sort_list:
            input_file = self.files_list[index]
            if duplicate_hashmap[input_file.datetime] > 1:
                # Datetime occured more than once. Duplicate
                self.duplicates_list.append(index)

                # Check and update the index hashmap
                if input_file.datetime in duplicate_idx_hashmap:
                    duplicate_idx_hashmap[input_file.datetime] += 1
                else:
                    duplicate_idx_hashmap[input_file.datetime] = 1

                # Set the input_file duplicate index
                input_file.duplicate_idx = duplicate_idx_hashmap[input_file.datetime]

        # Log Stats for files to be sorted
        logger.info(
            "Found %i files to sort in %s", len(self.sort_list), self.source_dir
        )
        logger.debug(
            "Sortable files :\n%s\n",
            "\n".join(
                [i.fullpath for i in [self.files_list[j] for j in self.sort_list]]
            ),
        )

        # Log Stats for files Not to be sorted
        logger.info(
            "Found %i files not matching sort options in %s",
            len(self.other_list),
            self.source_dir,
        )
        logger.debug(
            "Sortable files not matching sort options :\n%s\n",
            "\n".join(
                [i.fullpath for i in [self.files_list[j] for j in self.other_list]]
            ),
        )

        # Log Stats for files that will fail to be sorted
        logger.info(
            "Found %i unsortable files in %s", len(self.failed_list), self.source_dir
        )
        logger.debug(
            "Unsortable files : \n%s\n",
            "\n".join(
                [i.fullpath for i in [self.files_list[j] for j in self.failed_list]]
            ),
        )

        # Log stats regarding duplicate datetime files
        logger.info(
            "Found %i files with duplicate timestamps in %s",
            len(self.duplicates_list),
            self.source_dir,
        )
        logger.debug(
            "Duplicate timestamp files : \n%s\n",
            "\n".join(
                [
                    f"{i.fullpath}:{i.datetime} idx_{i.duplicate_idx}"
                    for i in [self.files_list[j] for j in self.duplicates_list]
                ]
            ),
        )
        if self.tk_text_object is not None:
            # Only run if a GUI object is provided
            self.tk_text_object.configure(state="normal")  # Make writable
            self.tk_text_object.insert(
                tk.INSERT,
                f"\nFound {len(self.sort_list)} images/videos meeting the above criteria in\n"
                f"{self.source_dir}\n",
            )
            if self.other_list:
                self.tk_text_object.insert(
                    tk.INSERT,
                    f"\nWARNING: Found {len(self.other_list)} files that won't be sorted (videos, docs, etc), "
                    "tick the 'Copy all other files' box above "
                    "if you want them copied to the destination "
                    "folder during sorting\n",
                )

            if self.duplicates_list:
                duplicate_ratio = len(self.duplicates_list) / len(self.sort_list)
                self.tk_text_object.insert(
                    tk.INSERT,
                    f"\nWARNING: Found {len(self.duplicates_list)}({duplicate_ratio:.0%}) files "
                    "with duplicate timestamps.\n"
                    "You can enable 'Rename' option above to keep all duplicates "
                    " or ignore this warning to filter out all duplicates.\n",
                )
            self.tk_text_object.insert(
                tk.INSERT, "\nPress 'Start' to begin sorting them....\n"
            )
            self.tk_text_object.yview(tk.END)
            self.tk_text_object.configure(state="disabled")  # Read Only

    def _find_files(self):
        """Generate a list of files found in the source_dir"""
        for root_path, __, files in os.walk(self.source_dir):
            for file_name in files:
                self.files_list.append(File(os.path.join(root_path, file_name)))

        # Log info about the number of files found
        logger.info("Found %i files in %s", len(self.files_list), self.source_dir)
        logger.debug("Found files :\n%s", "\n".join([str(i) for i in self.files_list]))
        if self.tk_text_object is not None:
            # Only run if a GUI object is provided
            self.tk_text_object.configure(state="normal")  # Make writable
            self.tk_text_object.delete("1.0", tk.END)
            self.tk_text_object.insert(
                tk.INSERT,
                f"Found {len(self.files_list)} files in the input folder. Running analysis on them now...\n",
            )
            self.tk_text_object.yview(tk.END)
            self.tk_text_object.configure(state="disabled")  # Read Only

    @staticmethod
    def get_datetime(input_file: File) -> File:
        """Attempt to extract datetime from a file

        Arguments:
            input_file: File object
        Returns: File object with datetime modified
        """
        try:
            if input_file.extension.lower().endswith(tuple(JPEG_EXTENSIONS)):
                # the file is JPEG so try extract datetime from EXIF
                input_file.datetime = ImageSort._get_datetime_from_exif(
                    input_file.fullpath
                )
            else:
                input_file.datetime = ImageSort._get_datetime_from_filename(
                    input_file.fullpath
                )

        # str_dtime = str(dtime)
        # dup_idx_str = ""
        # if str_dtime in dup_date_counter:
        #     dup_idx = dup_date_counter.get(str_dtime) + 1
        #     dup_idx_str = f"_{dup_idx:0>2}"
        # dup_date_counter.update({str_dtime: 1})

        # ext = os.path.splitext(image_path)[1]
        # new_name_diff = new_name_diff_off.replace(ext, f"{dup_idx_str}{ext}")

        except Exception as error:
            logger.warning(
                "Failed to get datetime for: %s from error: %s",
                input_file.fullpath,
                error,
            )
            input_file.datetime = None
        return input_file

    @staticmethod
    def _get_datetime_from_exif(filepath):
        """Attempt to get the datetime an image was taken from the EXIF data"""
        # pylint: disable=(protected-access) #This is the call to _getexif
        # pylint: disable=(broad-except)
        try:
            date_taken = Image.open(filepath)._getexif()[36867]
            dtime = datetime.strptime(date_taken, "%Y:%m:%d %H:%M:%S")
            return dtime
        except Exception:
            # Reading from exif failed, try filename instead
            return ImageSort._get_datetime_from_filename(filepath)

    @staticmethod
    def _get_datetime_from_filename(filepath):
        """Attempt to get the datetime of a file from it's filename"""
        filename = os.path.split(filepath)[1]
        # See if the years from 1970-2099 exist in the filename
        valid_years = [str(year) for year in range(1970, 2100)]
        in_years = [year in filename for year in valid_years]
        if sum(in_years) == 0:
            raise ValueError(f"No year found in {filename}")
        # Extract only numbers from the filename
        filename = os.path.splitext(filename)[0]
        numbers = [char for char in filename if char.isdigit()]
        numbers = "".join(numbers)
        # Extract datetime from numbers
        dtime = parser.parse(numbers)
        return dtime

    def run_parallel_sorting(self):
        """Creates a pool of workers and runs the image sorting across multiple threads.
        The pool size is equal to half the number of available threads the machine has.
        SSD's benifit from multithreading while HDD's will generally be the bottleneck.
        """
        self.sorting_complete = False

        with multiprocessing.Pool(processes=self.threads_to_use) as pool:
            inputs = [
                (self.message_queue, self.destination_dir, input_file)
                for input_file in self.files_list
                if input_file.sort_flag
            ]
            print(inputs)
            pool.starmap(self.copy_file, inputs)

        self.sorting_complete = True
        logger.info("Sorting Completed")

    @staticmethod
    def copy_file(message_queue, destination_dir: str, input_file: File):
        """Copy method that copies files into the structured output folder.
        Arguments:
            message_queue: a Queue to put log messages on for the GUI to display
            destination_dir: the output folder selected by the user
            input_file: File object
        """
        new_path = os.path.join(destination_dir, input_file.destination_relative_path)
        os.makedirs(new_path, exist_ok=True)
        destination_fullpath = os.path.join(new_path, input_file.sorted_filename)
        shutil.copyfile(input_file.fullpath, destination_fullpath)
        message_queue.put(
            f"Processed : {input_file.fullpath} --> {destination_fullpath}\n"
        )

    def read_queue(self):
        """Method to receive and log the messages from the workers in the pool"""
        while True:
            message = self.message_queue.get()
            if message == "kill":
                break
            if self.tk_text_object is not None:
                # Only run if a GUI object is provided
                self.tk_text_object.configure(state="normal")  # Make writable
                self.tk_text_object.insert(tk.INSERT, message)
                self.tk_text_object.yview(tk.END)
                self.tk_text_object.configure(state="disabled")  # Read Only

    def cleanup(self):
        """Cleanup function that kills any threads spawned on instance creation"""
        logger.debug("Running cleanup on queue thread")
        self.message_queue.put("kill")
        time.sleep(0.2)
