""" Image sorting tool code that performs the parallel sorting operation
"""
import os
import shutil
import logging
import multiprocessing
import threading
import time
import tkinter as tk
from collections import Counter
from datetime import datetime
from dateutil import parser
from PIL import Image

JPEG_EXTENSIONS = [".jpg", ".jpeg", ".jif", ".jpe", ".jfif", ".jfi", ".jp2", ".jpx"]

logger = logging.getLogger("root")


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
        self.sort_list = []
        self.other_list = []
        self.ext_to_sort = []
        self.rename_duplicates = False
        self.copy_unsorted = False
        self.sorting_complete = False

    @staticmethod
    def get_datetime_from_exif(filepath):
        """Attempt to get the datetime an image was taken from the EXIF data"""
        # pylint: disable=(protected-access) #This is the call to _getexif
        # pylint: disable=(broad-except)
        try:
            date_taken = Image.open(filepath)._getexif()[36867]
            dtime = datetime.strptime(date_taken, "%Y:%m:%d %H:%M:%S")
            return dtime
        except Exception:
            # Reading from exif failed, try filename instead
            return ImageSort.get_datetime_from_filename(filepath)

    @staticmethod
    def get_datetime_from_filename(filepath):
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

    def find_images(self):
        """The image finding function
        Searches for all .jpg and .mp4 in the source directory, including all subfolders
        Returns a log message of the number of images found as well as storing the paths for later.
        """
        # pylint: disable=(broad-except)
        dup_date_counter = Counter()

        def get_new_path(image_path):
            try:
                if image_path.lower().endswith(tuple(JPEG_EXTENSIONS)):
                    # the file is JPEG so try extract datetime from EXIF
                    dtime = ImageSort.get_datetime_from_exif(image_path)
                else:
                    dtime = ImageSort.get_datetime_from_filename(image_path)

                str_dtime = str(dtime)
                dup_idx_str = ""
                if str_dtime in dup_date_counter:
                    dup_idx = dup_date_counter.get(str_dtime) + 1
                    dup_idx_str = f"_{dup_idx:0>2}"
                dup_date_counter.update({str_dtime: 1})

                ext = os.path.splitext(image_path)[1]
                new_name_diff_off = (
                    f"{dtime.year:0>4}{dtime.month:0>2}{dtime.day:0>2}"
                    f"_{dtime.hour:0>2}{dtime.minute:0>2}{dtime.second:0>2}{ext}"
                )
                new_name_diff = new_name_diff_off.replace(ext, f"{dup_idx_str}{ext}")
                new_path = os.path.join(
                    self.destination_dir,
                    str(dtime.year).zfill(4),
                    str(dtime.month).zfill(2),
                )

            except Exception as error:
                logger.warning("Failed from: %s: %s", error, image_path)
                self.message_queue.put(f"Failed: {image_path}\n")
                new_path = os.path.join(self.destination_dir, "failed_to_sort")
                new_name_diff_off = os.path.split(image_path)[1]
                new_name_diff = new_name_diff_off

            return new_path, new_name_diff_off, new_name_diff

        self.sort_list = []
        for root_path, __, files in os.walk(self.source_dir):
            for file_name in files:
                file_path = os.path.join(root_path, file_name)
                if file_name.lower().endswith(tuple(self.ext_to_sort)):
                    new_path, new_name, new_name_diff = get_new_path(file_path)
                    self.sort_list.append(
                        (file_path, new_path, new_name, new_name_diff)
                    )
                else:
                    # Other files for a copy operation
                    new_path = os.path.join(self.destination_dir, "other_files")
                    self.other_list.append((file_path, new_path, file_name, None))
        logger.info(
            "Found %i sortable files in %s", len(self.sort_list), self.source_dir
        )
        logger.debug("Sortable files : %s", self.sort_list)
        logger.info(
            "Found %i unsortable files in %s", len(self.other_list), self.source_dir
        )
        logger.debug("Unsortable files : %s", self.other_list)
        logger.info(
            "Found %i dupplicated files in %s",
            sum(dup_date_counter.values()) - len(dup_date_counter),
            self.source_dir,
        )
        if self.tk_text_object is not None:
            # Only run if a GUI object is provided
            self.tk_text_object.configure(state="normal")  # Make writable
            self.tk_text_object.delete("1.0", tk.END)
            self.tk_text_object.insert(
                tk.INSERT,
                f"Found {len(self.sort_list)} images/videos meeting the above criteria in "
                f"{self.source_dir} ..... press 'start' to begin sorting them\n",
            )
            self.tk_text_object.insert(
                tk.INSERT,
                f"Found {len(self.other_list)} files that won't be sorted (videos, docs, etc), "
                "tick the 'Copy all other files' box above "
                "if you want them copied to the destination "
                "folder during sorting\n",
            )

            n_dup_images = sum(v for v in dup_date_counter.values() if v != 1)
            n_total_images = sum(dup_date_counter.values())
            if n_total_images > 0:
                dup_ratio = (100 * n_dup_images) / n_total_images
                self.tk_text_object.insert(
                    tk.INSERT,
                    f"Found {n_dup_images}({dup_ratio}%) files duplicated on target filepath. "
                    "They have exact same timestamp.\n"
                    "You can enable 'Rename' option above or just ignore this warning\n",
                )
            self.tk_text_object.yview(tk.END)
            self.tk_text_object.configure(state="disabled")  # Read Only

    @staticmethod
    def copy_file(
        message_queue, destination_dir, source_image_path, new_path, new_name
    ):
        """Image sorting method that sorts a single image.
        The image is opened and the date taken is attempted to be read from the EXIF data.
        The image is then sorted according to the date taken in the following format...

            destination_dir/yyyy/mm/yyyymmdd-HHMMSS.jpg

        If the date taken is not extracted then the image will be copied to
        destination_dir/failed_to_sort/ with the filename unchanged.
        """
        destination_dir = os.path.abspath(destination_dir)
        source_image_path = os.path.abspath(source_image_path)
        os.makedirs(new_path, exist_ok=True)
        image_destination_path = os.path.join(new_path, new_name)
        shutil.copyfile(source_image_path, image_destination_path)
        message_queue.put(
            f"Processed : {source_image_path} --> {image_destination_path}\n"
        )

    def run_parallel_sorting(self):
        """Creates a pool of workers and runs the image sorting across multiple threads.
        The pool size is equal to half the number of available threads the machine has.
        SSD's benifit from multithreading while HDD's will generally be the bottleneck.
        """
        self.sorting_complete = False
        with multiprocessing.Pool(processes=self.threads_to_use) as pool:
            inputs = [
                (
                    self.message_queue,
                    self.destination_dir,
                    source_image_path,
                    new_path,
                    new_name_diff if self.rename_duplicates else new_name,
                )
                for (
                    source_image_path,
                    new_path,
                    new_name,
                    new_name_diff,
                ) in self.sort_list
            ]
            pool.starmap(self.copy_file, inputs)

        # Run copy operation on unsortable files if requested
        if self.copy_unsorted:
            logger.info("Starting unsorted image copying stage")
            self.run_parallel_copy()
        self.sorting_complete = True
        logger.info("Sorting Completed")

    def run_parallel_copy(self):
        """Creates a pool of workers and runs the unsortable file copying across multiple threads.
        The pool size is equal to half the number of available threads the machine has.
        SSD's benefit from multi-threading while HDD's will generally be the bottleneck.
        """
        unsortable_dir = os.path.abspath(
            os.path.join(self.destination_dir, "other_files/")
        )
        with multiprocessing.Pool(processes=self.threads_to_use) as pool:
            inputs = [
                (
                    self.message_queue,
                    unsortable_dir,
                    source_file_path,
                    new_path,
                    new_name,
                )
                for (source_file_path, new_path, new_name, _) in self.other_list
            ]
            pool.starmap(self.copy_file, inputs)

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
