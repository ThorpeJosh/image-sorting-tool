"""Image-sorting-tool."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("image-sorting-tool")
except PackageNotFoundError:
    __version__ = "unknown"
