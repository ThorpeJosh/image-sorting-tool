""" Image sorting tool tkinter GUI module
"""

import os
import sys
import logging
import time
import threading
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import scrolledtext
from tkinter import messagebox
from image_sorting_tool import __version__
from image_sorting_tool.image_sort import ImageSort
from image_sorting_tool.image_sort import JPEG_EXTENSIONS

logger = logging.getLogger("image-sorting-tool")


class GUI(tk.Tk):
    """Tkinter GUI object"""

    # pylint: disable=(too-many-instance-attributes)
    # pylint: disable=(attribute-defined-outside-init)
    # pylint does not play well with tkinter, often thinking variables are declared
    # outside __init__ when they aren't.
    # Also picks up on Widgets defined in their respective draw method

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.title("Image Sorting Tool")
        self.init_vars()
        self.source_dir_var.trace("w", self.enable_buttons)
        self.destination_dir_var.trace("w", self.enable_buttons)

    def init_vars(self):
        """Method called during __init__ that initialises some user variables and parameters"""
        self.source_dir_var = tk.StringVar()
        self.destination_dir_var = tk.StringVar()
        self.jpeg_sort = tk.IntVar(value=1)  # Preselect the JPEG option
        self.png_sort = tk.IntVar()
        self.gif_sort = tk.IntVar()
        self.mp4_sort = tk.IntVar()
        self.rename_duplicates = tk.IntVar()
        self.copy_other_files = tk.IntVar()
        self.textbox_width = 100
        self.scroll_width = 100
        self.scroll_height = 40
        self.find_flag = False  # True if the image finding function has run.
        self.ext_to_sort = []

    def draw_main(self):
        """Main window for GUI"""
        # pylint: disable=too-many-locals
        # pylint: disable=too-many-statements

        # Clear all widgets from root window
        for widget in self.winfo_children():
            widget.destroy()

        logger.debug("Drawing main window")

        # Main GUI has 3 columns
        no_col = 3
        title_row = 0
        description_row = 1
        sample_structure_row = 2
        file_options_row = 3
        extra_options_row = 4
        source_dir_row = 5
        description_dir_row = 6
        button_row = 7
        scroll_text_row = 8

        # Allow middle column to grow when window is resized
        self.columnconfigure(1, weight=1, minsize=self.textbox_width * 5)

        # First row
        title_label = ttk.Label(
            self,
            text=f"Image Sorting Tool - Maintained by Joshua Thorpe - v{__version__}",
        )
        title_label.grid(column=0, row=title_row, columnspan=no_col, pady=10)

        # description row
        description_message_text = (
            "This tool reads the files from the 'Input Folder' "
            "and creates a sorted copy of the files in the 'Output Folder'."
        )
        description_message = tk.Message(self, text=description_message_text, width=700)
        description_message.grid(
            column=0, row=description_row, columnspan=no_col, pady=0
        )
        structure_text = (
            "The 'Output Folder' structure follows 'yyyy/mm/yyyymmdd_HHMMSS.jpg', for example:\n"
            "    ├── 2019\n"
            "       └── 12\n"
            "          ├── 20191011_180520.jpg\n"
            "          └── 20191029_204731.png\n"
            "    └── 2020\n"
            "       ├── 01\n"
            "          └── 20200114_135312.mp4\n"
            "       └── 03\n"
            "          └── 20200301_110330.jpg"
        )
        sample_structure_message = tk.Message(self, text=structure_text, width=500)
        sample_structure_message.grid(
            column=0, row=sample_structure_row, columnspan=no_col, pady=5
        )

        # Filetype options frame
        file_type_options_frame = ttk.LabelFrame(self, text="File types to sort:")
        file_type_options_frame.grid(column=1, row=file_options_row, sticky="EW")

        # Checkbox for JPEG
        jpeg_checkbox = ttk.Checkbutton(
            file_type_options_frame,
            text="JPG, JPEG: Common format for images captured by camera",
            variable=self.jpeg_sort,
            state="normal",
        )
        jpeg_checkbox.pack(anchor="w")

        # Checkbox for PNG
        png_checkbox = ttk.Checkbutton(
            file_type_options_frame,
            text="PNG: Commonly used for screenshots or graphic images from internet",
            variable=self.png_sort,
            state="normal",
        )
        png_checkbox.pack(anchor="w")

        # Checkbox for GIF
        gif_checkbox = ttk.Checkbutton(
            file_type_options_frame,
            text="GIF: Animated pictures from internet or moving pictures taken with phone",
            variable=self.gif_sort,
            state="normal",
        )
        gif_checkbox.pack(anchor="w")

        # Checkbox for MP4
        mp4_checkbox = ttk.Checkbutton(
            file_type_options_frame,
            text="MP4: Common video format for phones and cameras",
            variable=self.mp4_sort,
            state="normal",
        )
        mp4_checkbox.pack(anchor="w")

        # Extra options frame
        extra_options_frame = ttk.LabelFrame(self, text="Extra Options:")
        extra_options_frame.grid(column=1, row=extra_options_row, sticky="EW")

        # Checkbox for renaming duplicate files
        duplicate_checkbox_text = (
            "Rename images with duplicate 'date taken' times to "
            "'<date_taken>_1.jpg', '<date taken>_2.jpg'..."
            # "Useful for burst shots or if you fear duplicates exist with different resolutions. "
            # "Default behaviour is to overwrite duplicates."
        )
        duplicate_checkbox = ttk.Checkbutton(
            extra_options_frame,
            text=duplicate_checkbox_text,
            variable=self.rename_duplicates,
            state="normal",
        )
        duplicate_checkbox.pack(anchor="w")

        # Checkbox for copying unsortable files
        unsortable_checkbox_text = (
            "Copy all other files (documents, binaries, etc) to the "
            "destination directory under an 'other_files' folder"
        )
        unsortable_checkbox = ttk.Checkbutton(
            extra_options_frame,
            text=unsortable_checkbox_text,
            variable=self.copy_other_files,
            state="normal",
        )
        unsortable_checkbox.pack(anchor="w")

        # Source Directory Widgets
        ttk.Label(self, text="Input Folder").grid(
            column=0, row=source_dir_row, padx=5, sticky="W"
        )
        self.source_textbox = ttk.Entry(
            self, textvariable=self.source_dir_var, width=self.textbox_width
        )
        self.source_textbox.grid(column=1, row=source_dir_row, sticky="EW")
        ttk.Button(
            self, text="Browse", command=lambda: self.get_directory(self.source_dir_var)
        ).grid(column=2, row=source_dir_row, padx=5, sticky="E")

        # Output File Widgets
        ttk.Label(self, text="Output Folder").grid(
            column=0, row=description_dir_row, padx=5, sticky="W"
        )
        self.destination_textbox = ttk.Entry(
            self, textvariable=self.destination_dir_var, width=self.textbox_width
        )
        self.destination_textbox.grid(column=1, row=description_dir_row, sticky="EW")
        ttk.Button(
            self,
            text="Browse",
            command=lambda: self.get_directory(self.destination_dir_var),
        ).grid(column=2, row=description_dir_row, padx=5, sticky="E")

        # Begin Button
        self.start_button = ttk.Button(self, text="Start", command=self.sort_images)
        self.start_button.grid(
            column=no_col - 1, row=button_row, padx=5, pady=5, sticky="EW"
        )
        self.start_button.config(state="disabled")

        # Find Images Button
        self.find_button = ttk.Button(
            self, text="Analyse Source Directory", command=self.find_images
        )
        self.find_button.grid(column=no_col - 2, row=button_row, padx=5, pady=5)
        self.find_button.config(state="disabled")

        # Quit Button
        quit_button = ttk.Button(self, text="Quit", command=self._quit)
        quit_button.grid(column=0, row=button_row, padx=5, pady=5, sticky="EW")

        # Scrolled Text Widget
        self.scroll = scrolledtext.ScrolledText(
            self, width=self.scroll_width, height=self.scroll_height, wrap=tk.WORD
        )
        self.scroll.grid(
            column=0,
            row=scroll_text_row,
            columnspan=no_col,
            padx=5,
            pady=(0, 5),
            sticky="NSEW",
        )
        self.rowconfigure(scroll_text_row, weight=1)
        self.scroll.insert(
            tk.INSERT,
            (
                "Welcome, Enter a source and destination directory, "
                'then click "Analyse Source Directory"\n',
            ),
        )
        self.scroll.configure(state="disabled")  # Read Only

    def get_extensions_to_sort(self):
        """Checks the state of all the file type checkboxes and updates the list accordingly"""
        self.ext_to_sort = []
        if self.jpeg_sort.get():
            self.ext_to_sort.extend(JPEG_EXTENSIONS)
        if self.png_sort.get():
            self.ext_to_sort.append(".png")
        if self.gif_sort.get():
            self.ext_to_sort.append(".gif")
        if self.mp4_sort.get():
            self.ext_to_sort.append(".mp4")
        logger.debug("Extensions to sort: %s", self.ext_to_sort)

    def find_images(self):
        """Wrapper to call _find_images after botton state has changed"""
        logger.debug("Finding has been called from GUI")
        if self.assert_paths_are_valid(ignore_output_path=True):
            self.get_extensions_to_sort()
            self.find_button.config(text="Processing", state="disabled")
            self.after(100, self._find_images)

    def _find_images(self):
        """Run the image finding function from the image sorting tool."""
        self.sorting_tool = ImageSort(
            self.source_dir_var.get(), self.destination_dir_var.get(), self.scroll
        )
        self.sorting_tool.ext_to_sort = self.ext_to_sort
        if self.copy_other_files.get():
            logger.info("Copy 'other files' has been selected")
            self.sorting_tool.copy_unsorted = True
        if self.rename_duplicates.get():
            logger.info("Rename duplicates has been selected")
            self.sorting_tool.rename_duplicates = True
        self.sorting_tool.find_images()
        self.find_button.config(text="Finished Analysing Input Folder", state="normal")
        self.find_flag = True
        self.enable_buttons()

    def sort_images(self):
        """Wrapper for calling _sort_images after button state has changed."""
        logger.debug("Sorting has been called from GUI")
        if self.assert_paths_are_valid():
            self.sorting_tool.destination_dir = self.destination_dir_var.get()
            self.start_button.config(text="Processing", state="disabled")
            self.find_button.config(state="disabled")
            self.after(100, self._sort_images)

    def _sort_images(self):
        """Run the image sorting tool in a seperate thread so the GUI will continue functioning"""
        threading.Thread(
            target=self.sorting_tool.run_parallel_sorting, daemon=True
        ).start()
        threading.Thread(target=self._reset_buttons, daemon=True).start()

    def _reset_buttons(self):
        """Waits for sorting process to finish and then reactivates the start button and prints
        a message to the text window
        """
        while not self.sorting_tool.sorting_complete:
            time.sleep(1)
        # Sorting has finished, display message to GUI
        self.start_button.config(text="Finished Sorting!", state="normal")
        self.find_button.config(state="normal")
        self.scroll.configure(state="normal")  # Make writable
        self.scroll.insert(tk.INSERT, "<<<<< SORTING FINISHED >>>>>\n")
        self.scroll.yview(tk.END)
        self.scroll.configure(state="disabled")  # Read Only

    def _quit(self):
        """Quit the program"""
        logger.info("Quiting Image Sorting Tool")
        try:
            self.sorting_tool.cleanup()
        except AttributeError:
            pass
        self.quit()
        self.destroy()
        sys.exit()

    @staticmethod
    def get_directory(tk_var_to_change):
        """Launches a native browse window to allow user to select a directory.
        Sets the input as the chosen directoy.
        """
        directory = filedialog.askdirectory(title="Select a directory")
        # If user cancelled, filedialog doesn't return a string
        if isinstance(directory, str):
            tk_var_to_change.set(directory)

    def assert_paths_are_valid(self, ignore_output_path=False):
        """Check to ensure destination dir is not a child of source dir, and both are valid"""
        src_path, dst_path = self.source_dir_var.get(), self.destination_dir_var.get()
        if not os.path.isdir(src_path):
            logger.error("Input directory does not exist. '%s'", src_path)
            messagebox.showerror(
                "Input Folder Error", f"Input folder does not exist:\n{src_path}"
            )
            return False
        if not ignore_output_path:
            # No need to check output path for finding images
            if not os.path.isdir(dst_path):
                logger.error("Output directory does not exist. '%s'", dst_path)
                messagebox.showerror(
                    "Output Folder Error", f"Output folder does not exist:\n{dst_path}"
                )
                return False
            if os.path.abspath(
                os.path.commonpath([src_path, dst_path])
            ) == os.path.abspath(src_path):
                logger.error(
                    "Output directory cannot be a child of (or same as) input directory"
                )
                messagebox.showerror(
                    "Output Folder Error",
                    "Output folder needs to be located outside of the input folder",
                )
                return False
        return True

    def enable_buttons(self, *args):
        """Callback for a trace on the source_dir and destination_dir variables.
        Enables the start button if both variables contain valid filenames
        """
        # pylint: disable=(unused-argument) # Tkinter expects *args when running a trace
        source_text = self.source_dir_var.get()
        destination_text = self.destination_dir_var.get()

        logger.debug("Trace on 'Entry' textboxes activated")
        logger.debug("Src dir: %s - Dst dir: %s", source_text, destination_text)

        # Offset to account for non-uniform letter spacing
        offset = 0

        if (
            len(source_text) > self.textbox_width + offset
            or len(destination_text) > self.textbox_width + offset
        ):
            self.source_textbox.config(
                width=max(len(source_text), len(destination_text))
            )
            self.destination_textbox.config(
                width=max(len(source_text), len(destination_text))
            )

        if source_text and destination_text and self.find_flag:
            # If both directories have been supplied and the images have been found, allow sorting
            self.start_button.config(state="normal")
            self.find_button.config(state="normal")
        elif source_text:
            # If a source directory has been supplied then allow the find function to be run.
            self.find_button.config(state="normal")
            self.start_button.config(state="disabled")
        else:
            # No source directory is given so do not allow access to any functions
            self.start_button.config(state="disabled")
            self.find_button.config(state="disabled")
