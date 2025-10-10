from unittest.mock import patch


def test_empty_task_monitor_logging():
    import importlib

    em = importlib.import_module("app.gis.engine_models")
    mon = em.EmptyTaskMonitor()
    with patch.object(em, "logger") as log:
        assert mon.is_cancelled() is False
        mon.update_progress(10, phase="prep", description="start")
        mon.record_error("oops", phase="x", percent=5, description="bad")
        mon.record_file("raster", "/x/y.tif")
        assert log.info.call_count >= 2
        assert log.error.call_count == 1
