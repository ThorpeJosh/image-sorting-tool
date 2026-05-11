"""Unit tests for the __main__ module."""

from unittest.mock import patch

from image_sorting_tool.__main__ import parse_args


def test_parse_args() -> None:
    """Test argument parsing correctly extracts verbosity flags."""
    with patch("sys.argv", ["image-sorting-tool", "-vv"]):
        args = parse_args()
        assert args.verbosity == 2
