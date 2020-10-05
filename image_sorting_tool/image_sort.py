""" Image sorting tool code that performs the parallel sorting operation
"""
import os
import shutil
import logging
import multiprocessing
import threading
import time
import tkinter as tk
from datetime import datetime
from dateutil import parser
from PIL import Image

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
        self.copy_unsortable = False
        self.sorting_complete = False

    def find_images(self):
        """The image finding function
        Searches for all .jpg and .mp4 in the source directory, including all subfolders
        Returns a log message of the number of images found as well as storing the paths for later.
        """
        self.sort_list = []
        for root_path, __, files in os.walk(self.source_dir):
            for file_name in files:
                if file_name.lower().endswith((".jpg", ".jpeg", ".mp4", ".gif")):
                    # JPGs and MP4 only for sorting
                    self.sort_list.append(os.path.join(root_path, file_name))
                else:
                    # Other files for a copy operation
                    self.other_list.append(os.path.join(root_path, file_name))
        logger.info("Found %i sortable files in %s", len(self.sort_list), self.source_dir)
        logger.info(
            "Found %i unsortable files in %s", len(self.other_list), self.source_dir
        )
        if self.tk_text_object is not None:
            # Only run if a GUI object is provided
            self.tk_text_object.configure(state="normal")  # Make writable
            self.tk_text_object.delete("1.0", tk.END)
            self.tk_text_object.insert(
                tk.INSERT,
                "Found {} sortable images/videos in {} ..... press 'start' to \
begin sorting them\n".format(
                    len(self.sort_list), self.source_dir
                ),
            )
            self.tk_text_object.insert(
                tk.INSERT,
                "Found {} unsortable files (videos, docs, etc) tick the box above if \
you want them copied to the destination folder during sorting\n".format(
                    len(self.other_list)
                ),
            )
            self.tk_text_object.yview(tk.END)
            self.tk_text_object.configure(state="disabled")  # Read Only

    @staticmethod
    def sort_image(message_queue, destination_dir, source_image_path):
        """Image sorting method that sorts a single image.
        The image is opened and the date taken is attempted to be read from the EXIF data.
        The image is then sorted according to the date taken in the following format...

            destination_dir/yyyy/mm/yyyymmdd-HHMMSS.jpg

        If the date taken is not extracted then the image will be copied to
        destination_dir/failed_to_sort/ with the filename unchanged.
        """
        destination_dir = os.path.abspath(destination_dir)
        source_image_path = os.path.abspath(source_image_path)
        try:
            # pylint: disable=(protected-access) #This is the call to _getexif
            # pylint: disable=(broad-except)
            try:
                if source_image_path.lower().endswith((".mp4", ".gif")):
                    # Skip straight to filename datetime extraction
                    raise KeyError
                # Try get datetime from exif
                date_taken = Image.open(source_image_path)._getexif()[36867]
                dtime = datetime.strptime(date_taken, "%Y:%m:%d %H:%M:%S")
            except KeyError as date_taken_err:
                # Exif failed, try filename instead
                filename = os.path.split(source_image_path)[1]
                valid_years = [str(year) for year in range(1990, 2100)]
                in_years = [year in filename for year in valid_years]
                if sum(in_years) == 0:
                    raise ValueError(
                        "No year found in {}".format(filename)
                    ) from date_taken_err
                # Extract only numbers from the filename
                filename = os.path.splitext(filename)[0]
                numbers = [letter for letter in filename if letter.isdigit()]
                numbers = "".join(numbers)
                # Extract datetime from numbers
                dtime = parser.parse(numbers)

            new_name = "{}{}{}_{}{}{}{}".format(
                str(dtime.year).zfill(4),
                str(dtime.month).zfill(2),
                str(dtime.day).zfill(2),
                str(dtime.hour).zfill(2),
                str(dtime.minute).zfill(2),
                str(dtime.second).zfill(2),
                os.path.splitext(source_image_path)[1],
            )
            new_path = os.path.join(
                destination_dir, str(dtime.year).zfill(4), str(dtime.month).zfill(2)
            )
            os.makedirs(new_path, exist_ok=True)
            image_destination_path = os.path.join(new_path, new_name)
            shutil.copyfile(source_image_path, image_destination_path)
            message_queue.put(
                "Sorted: {} --> {}\n".format(source_image_path, image_destination_path)
            )

        except Exception as error:
            logger.warning("Failed from: %s: %s", error, source_image_path)
            message_queue.put("Failed: {}\n".format(source_image_path))
            new_path = os.path.join(destination_dir, "failed_to_sort")
            new_name = os.path.split(source_image_path)[1]
            os.makedirs(new_path, exist_ok=True)
            shutil.copyfile(source_image_path, os.path.join(new_path, new_name))

    def run_parallel_sorting(self):
        """Creates a pool of workers and runs the image sorting across multiple threads.
        The pool size is equal to half the number of available threads the machine has.
        SSD's benifit from multithreading while HDD's will generally be the bottleneck.
        """
        self.sorting_complete = False
        with multiprocessing.Pool(processes=self.threads_to_use) as pool:
            inputs = [
                (self.message_queue, self.destination_dir, image)
                for image in self.sort_list
            ]
            pool.starmap(self.sort_image, inputs)

        # Run copy operation on unsortable files if requested
        if self.copy_unsortable:
            logger.info("Starting unsorted image copying stage")
            self.run_parallel_copy()
        self.sorting_complete = True
        logger.info("Sorting Completed")

    @staticmethod
    def copy_file(message_queue, destination_dir, source_path):
        """File copy method that copies unsortable files to the destination folder"""
        source_path = os.path.abspath(source_path)
        destination_dir = os.path.abspath(destination_dir)
        os.makedirs(destination_dir, exist_ok=True)

        destination_path = os.path.abspath(
            os.path.join(destination_dir, os.path.split(source_path)[1])
        )
        shutil.copyfile(source_path, destination_path)
        logger.debug("Copied unsortable file %s --> %s", source_path, destination_path)
        message_queue.put(
            "Copied unsortable file {} --> {}\n".format(source_path, destination_path)
        )

    def run_parallel_copy(self):
        """Creates a pool of workers and runs the unsortable file copying across multiple threads.
        The pool size is equal to half the number of available threads the machine has.
        SSD's benifit from multithreading while HDD's will generally be the bottleneck.
        """
        unsortable_dir = os.path.abspath(
            os.path.join(self.destination_dir, "other_files/")
        )
        with multiprocessing.Pool(processes=self.threads_to_use) as pool:
            inputs = [
                (self.message_queue, unsortable_dir, filename)
                for filename in self.other_list
            ]
            pool.starmap(self.copy_file, inputs)

    def read_queue(self):
        """Method to receive and log the messages from the workers in the pool"""
        while True:
            message = self.message_queue.get()
            if message == "kill":
                break
            self.tk_text_object.configure(state="normal")  # Make writable
            self.tk_text_object.insert(tk.INSERT, message)
            self.tk_text_object.yview(tk.END)
            self.tk_text_object.configure(state="disabled")  # Read Only

    def cleanup(self):
        """Cleanup function that kills any threads spawned on instance creation"""
        logger.debug("Running cleanup on queue thread")
        self.message_queue.put("kill")
        time.sleep(0.2)
