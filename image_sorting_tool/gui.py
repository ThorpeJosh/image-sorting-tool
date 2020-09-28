""" Image sorting tool tkinter GUI module
"""
import sys
import threading
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import scrolledtext
from image_sorting_tool.image_sort import ImageSort


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
        self.textbox_width = 100
        self.scroll_width = 100
        self.scroll_height = 40
        self.find_flag = False  # True if the image finding function has run.

    def draw_main(self):
        """Main window for GUI"""
        for widget in self.winfo_children():
            widget.destroy()

        # Main GUI has 3 columns
        no_col = 3

        # Allow middle column to grow when window is resized
        self.columnconfigure(1, weight=1, minsize=self.textbox_width * 5)

        # First row
        title_label = ttk.Label(
            self, text="Image Sorting Tool - Maintained by Joshua Thorpe"
        )
        title_label.grid(column=0, row=0, columnspan=no_col, pady=5)

        # Second row
        message = (
            "Source directory: Directory which to search recursively for .jpg files \n"
            + 'Destination directory: Directory to place the sorted images into in the \
following structure "yyyy/mm/yyyymmdd-HHMMSS.jpg"'
        )
        description_message = tk.Message(self, text=message, width=1000)
        description_message.grid(column=0, row=1, columnspan=no_col, pady=5)

        # Source Directory Widgets
        ttk.Label(self, text="Source Directory").grid(
            column=0, row=2, padx=5, sticky="W"
        )
        self.source_textbox = ttk.Entry(
            self, textvariable=self.source_dir_var, width=self.textbox_width
        )
        self.source_textbox.grid(column=1, row=2, sticky="EW")
        ttk.Button(
            self, text="Browse", command=lambda: self.get_directory(self.source_dir_var)
        ).grid(column=2, row=2, padx=5, sticky="E")

        # Output File Widgets
        ttk.Label(self, text="Destination Directory").grid(
            column=0, row=3, padx=5, sticky="W"
        )
        self.destination_textbox = ttk.Entry(
            self, textvariable=self.destination_dir_var, width=self.textbox_width
        )
        self.destination_textbox.grid(column=1, row=3, sticky="EW")
        ttk.Button(
            self,
            text="Browse",
            command=lambda: self.get_directory(self.destination_dir_var),
        ).grid(column=2, row=3, padx=5, sticky="E")

        # Begin Button
        self.start_button = tk.Button(self, text="Start", command=self.sort_images)
        self.start_button.grid(column=no_col - 1, row=4, padx=5, pady=5, sticky="EW")
        self.start_button.config(state="disabled")

        # Find Images Button
        self.find_button = tk.Button(self, text="Find Images", command=self.find_images)
        self.find_button.grid(column=no_col - 2, row=4, padx=5, pady=5)
        self.find_button.config(state="disabled")

        # Quit Button
        quit_button = tk.Button(self, text="Quit", command=self._quit)
        quit_button.grid(column=0, row=4, padx=5, pady=5, sticky="EW")

        # Scrolled Text Widget
        scroll_text_row = 5
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
            'Welcome, Enter a source and destination directory, then click "Find Images"',
        )
        self.scroll.configure(state="disabled")  # Read Only

    def find_images(self):
        """Wrapper to call _find_images after botton state has changed"""
        self.find_button.config(text="Processing", state="disabled")
        self.after(100, self._find_images)

    def _find_images(self):
        """Run the image finding function from the image sorting tool."""
        self.sorting_tool = ImageSort(
            self.source_dir_var.get(), self.destination_dir_var.get(), self.scroll
        )
        self.sorting_tool.find_images()
        self.find_button.config(text="Finished Finding Images", state="normal")
        self.find_flag = True
        self.enable_buttons()

    def sort_images(self):
        """Wrapper for calling _sort_images after button state has changed.
        """
        self.sorting_tool.destination_dir = self.destination_dir_var.get()
        self.start_button.config(text="Processing", state="disabled")
        self.after(100, self._sort_images)

    def _sort_images(self):
        """Run the image sorting tool in a seperate thread so the GUI will continue functioning
        """
        threading.Thread(
            target=self.sorting_tool.run_parallel_sorting, daemon=True
        ).start()
        self.start_button.config(text="Finished Sorting!", state="normal")

    def _quit(self):
        """Quit the program
        """
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

    def enable_buttons(self, *args):
        """Callback for a trace on the source_dir and desitnation_dir variables.
        Enables the start button if both variables contain valid filenames
        """
        # pylint: disable=(unused-argument) # Tkinter expects *args when running a trace
        source_text = self.source_dir_var.get()
        destination_text = self.destination_dir_var.get()

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