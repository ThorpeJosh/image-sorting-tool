""" Image sorting tool module. This script launches a tkinter GUI that allows images to be sorted
based on their date taken.
"""
import os
import threading
import shutil
import multiprocessing
from datetime import datetime
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import scrolledtext
from PIL import Image

class GUI(tk.Tk):
    """Tkinter GUI object"""
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.title("Image Sorting Tool")
        self.init_vars()
        self.source_dir_var.trace("w", self.enable_buttons)
        self.destination_dir_var.trace("w", self.enable_buttons)

    def init_vars(self):
        """Method called during __init__ that initialises some user variables and parameters
        """
        self.source_dir_var = tk.StringVar()
        self.destination_dir_var = tk.StringVar()
        self.textbox_width = 100
        self.scroll_width = 100
        self.scroll_height = 40
        self.find_flag = False # True if the image finding function has run.

    def draw_main(self):
        """ Main window for GUI
        """
        for widget in self.winfo_children():
            widget.destroy()

        #Main GUI has 3 columns
        no_col = 3

        #Allow middle column to grow when window is resized
        self.columnconfigure(1, weight=1, minsize=self.textbox_width*5)

        #First row
        title_label = ttk.Label(self, text='Image Sorting Tool - Maintained by Joshua Thorpe')
        title_label.grid(column=0, row=0, columnspan=no_col, pady=5)

        #Second row
        message = 'Source directory: Directory which to search recursively for .jpg files \n' \
                + 'Destination directory: Directory to place the sorted images into in the following structure "yy/mm/yyyymmdd-HHMMSS.jpg"'
        description_message = tk.Message(self, text = message, width=1000)
        description_message.grid(column=0, row=1, columnspan=no_col, pady=5)

        #Source Directory Widgets
        ttk.Label(self, text="Source Directory").grid(column=0, row=2, padx=5, sticky='W')
        self.source_textbox = ttk.Entry(self, textvariable=self.source_dir_var, width=self.textbox_width)
        self.source_textbox.grid(column=1, row=2, sticky='EW')
        ttk.Button(self, text='Browse', command=lambda: self.get_directory(self.source_dir_var)).grid(column=2, row=2, padx=5, sticky='E')

        #Output File Widgets
        ttk.Label(self, text="Destination Directory").grid(column=0, row=3, padx=5, sticky='W')
        self.destination_textbox = ttk.Entry(self, textvariable=self.destination_dir_var, width=self.textbox_width)
        self.destination_textbox.grid(column=1, row=3, sticky='EW')
        ttk.Button(self, text='Browse', command=lambda: self.get_directory(self.destination_dir_var)).grid(column=2, row=3, padx=5, sticky='E')

        #Begin Button
        self.start_button = tk.Button(self, text='Start', command=self.sort_images)
        self.start_button.grid(column=no_col-1, row=4, padx=5, pady=5, sticky='EW')
        self.start_button.config(state='disabled')

        #Find Images Button
        self.find_button = tk.Button(self, text='Find Images', command=self.find_images)
        self.find_button.grid(column=no_col-2, row=4, padx=5, pady=5)
        self.find_button.config(state='disabled')

        #Quit Button
        quit_button = tk.Button(self, text='Quit', command=self._quit)
        quit_button.grid(column=0, row=4, padx=5, pady=5, sticky='EW')

        #Scrolled Text Widget
        scroll_text_row = 5
        self.scroll = scrolledtext.ScrolledText(self, width=self.scroll_width, height=self.scroll_height, wrap=tk.WORD)
        self.scroll.grid(column=0, row=scroll_text_row, columnspan=no_col, padx=5, pady=(0, 5), sticky='NSEW')
        self.rowconfigure(scroll_text_row, weight=1)
        self.scroll.insert(tk.INSERT, 'Welcome, Enter a source and destination directory, then click "Find Images"')
        self.scroll.configure(state='disabled')  # Read Only

    def find_images(self):
        """Wrapper to call _find_images after botton state has changed
        """
        self.find_button.config(text='Processing', state='disabled')
        self.after(100, self._find_images)

    def _find_images(self):
        """Run the image finding function from the image sorting tool.
        """
        self.sorting_tool = ImageSort(self.source_dir_var.get(), self.destination_dir_var.get(), self.scroll)
        self.sorting_tool.find_images()
        self.find_button.config(text='Finished Finding Images', state='normal')
        self.find_flag = True
        self.enable_buttons()

    def sort_images(self):
        self.start_button.config(text='Processing', state='disabled')
        self.after(100, self._sort_images)

    def _sort_images(self):
        threading.Thread(target=self.sorting_tool.run_parallel_sorting, daemon=True).start()
        self.start_button.config(text='Finished Sorting!', state='normal')

    def _quit(self):
        self.quit()
        self.destroy()
        exit()

    @staticmethod
    def get_directory(tk_var_to_change):
        """Launches a native browse window to allow user to select a directory.
        Sets the input as the chosen directoy.
        """
        directory = filedialog.askdirectory(title = "Select a directory")
        # If user cancelled, filedialog doesn't return a string
        if isinstance(directory, str):
            tk_var_to_change.set(directory)
    
    def enable_buttons(self, *args):
        """Callback for a trace on the source_dir and desitnation_dir variables.
        Enables the start button if both variables contain valid filenames
        """
        source_text = self.source_dir_var.get()
        destination_text = self.destination_dir_var.get()

        #Offset to account for non-uniform letter spacing
        offset = 0

        if len(source_text) > self.textbox_width+offset or len(destination_text) > self.textbox_width+offset:
            self.source_textbox.config(width=max(len(source_text), len(destination_text)))
            self.destination_textbox.config(width=max(len(source_text), len(destination_text)))

        if source_text and destination_text and self.find_flag: 
            # If both directories have been supplied and the images have been found, allow sorting
            self.start_button.config(state='normal')
            self.find_button.config(state='normal')
        elif source_text:
            # If a source directory has been supplied then allow the find function to be run.
            self.find_button.config(state='normal')
            self.start_button.config(state='disabled')
        else:
            # No source directory is given so do not allow access to any functions
            self.start_button.config(state='disabled')
            self.find_button.config(state='disabled')


class ImageSort:
    """Image sorting tool
    """
    def __init__(self, source_dir, destination_dir, tk_text_object):
        self.source_dir = source_dir
        self.destination_dir = destination_dir
        self.tk_text_object = tk_text_object
        self.threads_to_use = max(1, int(multiprocessing.cpu_count()/2))
        self.manager = multiprocessing.Manager()
        self.message_queue = self.manager.Queue()
        threading.Thread(target=self.read_queue, daemon=True).start()

    def find_images(self):
        """The image finding function
        Searches for all .jpg and .png in the source directory, including all subfolders
        Returns a log message of the number of images found as well as storing the paths for later.
        """
        self.image_list = []
        for root_path, __, files in os.walk(self.source_dir):
            for file_name in files:
                if file_name.lower().endswith(('.png', '.jpg', '.jpeg')):
                    self.image_list.append(os.path.join(root_path, file_name))
        self.tk_text_object.configure(state='normal')  # Make writable
        self.tk_text_object.delete('1.0', tk.END)
        self.tk_text_object.insert(tk.INSERT, "Found {} images in {} ..... press 'start' to begin sorting them\n".format(len(self.image_list), self.source_dir))
        self.tk_text_object.yview(tk.END)
        self.tk_text_object.configure(state='disabled')  # Read Only

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
            date_taken = Image.open(source_image_path)._getexif()[36867]
            dt= datetime.strptime(date_taken, '%Y:%m:%d %H:%M:%S')
            new_name = '{}{}{}_{}{}{}{}'.format(str(dt.year).zfill(4), str(dt.month).zfill(2), str(dt.day).zfill(2), str(dt.hour).zfill(2), str(dt.minute).zfill(2), str(dt.second).zfill(2), os.path.splitext(source_image_path)[1])
            new_path = os.path.join(destination_dir, str(dt.year).zfill(4), str(dt.month).zfill(2))
            os.makedirs(new_path, exist_ok=True)
            image_destination_path = os.path.join(new_path, new_name)
            shutil.copyfile(source_image_path, image_destination_path)
            message_queue.put("Sorted: {} --> {}\n".format(source_image_path, image_destination_path))
        except Exception as error:
            print('Error {}: {}'.format(error, source_image_path))
            message_queue.put("Failed: {}\n".format(source_image_path))
            new_path = os.path.join(destination_dir, 'failed_to_sort')
            new_name = os.path.split(source_image_path)[1]
            os.makedirs(new_path, exist_ok=True)
            shutil.copyfile(source_image_path, os.path.join(new_path, new_name))

    def run_parallel_sorting(self):
        """Creates a pool of workers and runs the image sorting across multiple threads.
        The pool size is equal to half the number of available threads the machine has.
        SSD's benifit from multithreading while HDD's will generally be the bottleneck.
        """
        with multiprocessing.Pool(processes=self.threads_to_use) as pool:
            inputs = [(self.message_queue, self.destination_dir, image)
                      for image in self.image_list]
            pool.starmap(self.sort_image, inputs)

    def read_queue(self):
        """Method to receive and log the messages from the workers in the pool
        """
        while True:
            message = self.message_queue.get()
            self.tk_text_object.configure(state='normal')  # Make writable
            self.tk_text_object.insert(tk.INSERT, message)
            self.tk_text_object.yview(tk.END)
            self.tk_text_object.configure(state='disabled')  # Read Only


if __name__ == "__main__":
    root = GUI()
    root.draw_main()
    root.mainloop()
