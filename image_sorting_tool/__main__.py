""" Image sorting tool module. This script launches a tkinter GUI that allows images to be sorted
based on their date taken.
"""
import logging
from image_sorting_tool.gui import GUI


# Create root logger
LOG_FORMAT = '%(levelname)s %(asctime)s : %(message)s'
logger = logging.getLogger('root')
logger.setLevel(logging.INFO)

# Log to stdout
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(logging.Formatter(LOG_FORMAT))
stream_handler.setLevel(logging.DEBUG)
logger.addHandler(stream_handler)

def run():
    """Entry point of program
    """
    logger.info('Launching Image Sorting Tool')
    root = GUI()
    root.draw_main()
    root.mainloop()

if __name__ == "__main__":
    run()
