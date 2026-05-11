"""Unit tests for the gui module."""

from collections.abc import Generator
from unittest.mock import patch

import pytest

from image_sorting_tool.gui import GUI
from image_sorting_tool.image_sort import JPEG_EXTENSIONS


@pytest.fixture(name="gui_app")
def fixture_gui_app() -> Generator[GUI, None, None]:
    """Fixture to instantiate and cleanup the Tkinter GUI."""
    app = GUI()
    app.draw_main()
    yield app
    app.destroy()


def test_get_extensions_to_sort(gui_app) -> None:
    """Test that checkboxes accurately map to the extensions list."""
    gui_app.get_extensions_to_sort()
    assert set(gui_app.ext_to_sort) == set(JPEG_EXTENSIONS)

    gui_app.png_sort.set(1)
    gui_app.mp4_sort.set(1)
    gui_app.get_extensions_to_sort()
    assert ".png" in gui_app.ext_to_sort
    assert ".mp4" in gui_app.ext_to_sort


def test_assert_paths_are_valid(gui_app, tmp_path) -> None:
    """Test path validation logic."""
    # Invalid Source
    gui_app.source_dir_var.set("invalid_path_123")
    gui_app.destination_dir_var.set("invalid_path_456")
    with patch("image_sorting_tool.gui.messagebox.showerror") as mock_err:
        assert not gui_app.assert_paths_are_valid()
        mock_err.assert_called()

    # Child Path rejection
    src = tmp_path / "src"
    src.mkdir()
    dst = src / "dst"
    dst.mkdir()
    gui_app.source_dir_var.set(str(src))
    gui_app.destination_dir_var.set(str(dst))
    with patch("image_sorting_tool.gui.messagebox.showerror") as mock_err:
        assert not gui_app.assert_paths_are_valid()
        mock_err.assert_called()

    # Valid Paths
    dst2 = tmp_path / "dst2"
    dst2.mkdir()
    gui_app.destination_dir_var.set(str(dst2))
    assert gui_app.assert_paths_are_valid()


def test_enable_buttons(gui_app) -> None:
    """Test button state management based on input variables."""
    gui_app.source_dir_var.set("src")
    gui_app.find_flag = False
    gui_app.enable_buttons()
    assert str(gui_app.find_button["state"]) == "normal"
    assert str(gui_app.start_button["state"]) == "disabled"

    gui_app.destination_dir_var.set("dst")
    gui_app.find_flag = True
    gui_app.enable_buttons()
    assert str(gui_app.start_button["state"]) == "normal"
