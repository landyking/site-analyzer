from unittest.mock import MagicMock, patch
from types import SimpleNamespace, ModuleType
import sys


def test_version_is_timestamp_like():
    # Import module fresh and check string exists
    import importlib
    tools = importlib.import_module("app.gis.tools")
    assert isinstance(tools.version, str) and len(tools.version) >= 10


def test_show_file_info_paths_and_errors(tmp_path, capsys):
    import importlib
    tools = importlib.import_module("app.gis.tools")

    # Create fake small files
    shp = tmp_path / "a.shp"
    tif = tmp_path / "b.tif"
    other = tmp_path / "c.xyz"
    for p in (shp, tif, other):
        p.write_bytes(b"1234")

    # For shapefile, cause read_file to raise -> exercise error branch
    with patch.object(tools.gpd, "read_file", side_effect=Exception("bad shp")):
        tools.show_file_info(str(shp))
        out = capsys.readouterr().out
        assert "File:" in out and ".shp" in out
        assert "Error reading shapefile" in out

    # For raster, fake rasterio open context
    fake_src = MagicMock()
    fake_src.__enter__.return_value = SimpleNamespace(meta={"tags": "ok"})
    fake_src.__exit__.return_value = False
    with patch.object(tools.rasterio, "open", return_value=fake_src):
        tools.show_file_info(str(tif))
        out = capsys.readouterr().out
        assert "metadata:" in out

    # For unknown extension
    tools.show_file_info(str(other))
    out = capsys.readouterr().out
    assert "Type: .xyz" in out


def test_plot_helpers_do_not_crash(tmp_path):
    import importlib
    tools = importlib.import_module("app.gis.tools")

    # Provide a fake matplotlib.pyplot to avoid import errors
    fake_pyplot = ModuleType("matplotlib.pyplot")
    fake_pyplot.imshow = MagicMock()
    fake_pyplot.colorbar = MagicMock()
    fake_pyplot.figure = MagicMock()
    fake_pyplot.axis = MagicMock()
    fake_pyplot.title = MagicMock()
    fake_pyplot.show = MagicMock()
    fake_pyplot.subplots = MagicMock(return_value=(MagicMock(), MagicMock()))

    with patch.dict(sys.modules, {"matplotlib": ModuleType("matplotlib"), "matplotlib.pyplot": fake_pyplot}):
        # Patch underlying IO
        with patch("app.gis.tools.rasterio.open") as rio_open, \
             patch("app.gis.tools.gpd.read_file") as read_file:
            # Raster
            rio_open.return_value.__enter__.return_value = SimpleNamespace(read=lambda b: [[1, 2], [3, 0]], nodata=0)
            tools.show_raster_plot("/tmp/f.tif")
            assert fake_pyplot.imshow.called

            # Shapefile
            read_file.return_value = MagicMock(plot=MagicMock())
            tools.show_shapefile_plot("/tmp/f.shp")
            assert fake_pyplot.subplots.called
