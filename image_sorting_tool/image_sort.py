""" Image sorting tool code that performs the parallel sorting operation
"""
import os
import shutil
import multiprocessing
import threading
import tkinter as tk
from datetime import datetime
from PIL import Image

class ImageSort:
    """Image sorting tool"""

    def __init__(self, source_dir, destination_dir, tk_text_object):
        self.source_dir = source_dir
        self.destination_dir = destination_dir
        self.tk_text_object = tk_text_object
        self.threads_to_use = max(1, int(multiprocessing.cpu_count() / 2))
        self.manager = multiprocessing.Manager()
        self.message_queue = self.manager.Queue()
        threading.Thread(target=self.read_queue, daemon=True).start()
        self.image_list = []

    def find_images(self):
        """The image finding function
        Searches for all .jpg and .png in the source directory, including all subfolders
        Returns a log message of the number of images found as well as storing the paths for later.
        """
        self.image_list = []
        for root_path, __, files in os.walk(self.source_dir):
            for file_name in files:
                if file_name.lower().endswith((".png", ".jpg", ".jpeg")):
                    self.image_list.append(os.path.join(root_path, file_name))
        if self.tk_text_object is not None:
            # Only run if a GUI object is provided
            self.tk_text_object.configure(state="normal")  # Make writable
            self.tk_text_object.delete("1.0", tk.END)
            self.tk_text_object.insert(
                tk.INSERT,
                "Found {} images in {} ..... press 'start' to begin sorting them\n".format(
                    len(self.image_list), self.source_dir
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
        try:
            # pylint: disable=(protected-access) #This is the call to _getexif
            # pylint: disable=(broad-except)
            date_taken = Image.open(source_image_path)._getexif()[36867]
            dtime = datetime.strptime(date_taken, "%Y:%m:%d %H:%M:%S")
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
            print("Error {}: {}".format(error, source_image_path))
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
        with multiprocessing.Pool(processes=self.threads_to_use) as pool:
            inputs = [
                (self.message_queue, self.destination_dir, image)
                for image in self.image_list
            ]
            pool.starmap(self.sort_image, inputs)

    def read_queue(self):
        """Method to receive and log the messages from the workers in the pool"""
        while True:
            message = self.message_queue.get()
            self.tk_text_object.configure(state="normal")  # Make writable
            self.tk_text_object.insert(tk.INSERT, message)
            self.tk_text_object.yview(tk.END)
            self.tk_text_object.configure(state="disabled")  # Read Only
