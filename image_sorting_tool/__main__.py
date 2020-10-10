""" Image sorting tool module. This script launches a tkinter GUI that allows images to be sorted
based on their date taken.
"""
import argparse
import logging
from image_sorting_tool.gui import GUI


# Create root logger
LOG_FORMAT = '%(levelname)s %(asctime)s : %(message)s'
logger = logging.getLogger('root')
logger.setLevel(logging.DEBUG)

# Log to stdout
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(logging.Formatter(LOG_FORMAT))
logger.addHandler(stream_handler)

def run():
    """Entry point of program
    """
    # Set log level from command line arguments
    args = parse_args()
    stream_handler.setLevel(logging.WARNING - (args.verbosity*10))

    logger.info('Launching Image Sorting Tool')
    root = GUI()
    root.draw_main()
    root.mainloop()

def parse_args():
    """Parse arguments from the command line"""
    parser = argparse.ArgumentParser(description='Image sorting tool - Launches a GUI')

    parser.add_argument('-v', '--verbosity', action='count', default=0,
                      help='Increase verbosity of log messages. -v will give info level,'
                            ' -vv will give debug level')
    return parser.parse_args()

if __name__ == "__main__":
    run()
