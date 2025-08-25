from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Tuple

from sqlmodel import Session, select

from app.core.config import settings
from app.core.db import engine as db_engine
from app.models import MapTaskDB, MapTaskFileDB, MapTaskStatus, MapTaskProgressDB
from app.gis.engine import SiteSuitabilityEngine
from app.gis.engine_models import EngineConfigs, RestrictedFactor, SuitabilityFactor, TaskMonitor

logger = logging.getLogger(__name__)


class MapTaskMonitor:
	"""Task monitor backed by DB rows.

	- is_cancelled(): short-lived DB read of t_map_task.status
	- update_progress(): throttled insert into t_map_task_progress
	"""

	def __init__(self, task_id: int, user_id: int, min_interval: float = 1.0) -> None:
		# min_interval kept for signature compatibility but unused (no throttling)
		self.task_id = task_id
		self.user_id = user_id

	@staticmethod
	def _clamp_percent(v: int) -> int:
		try:
			iv = int(v)
		except Exception:
			iv = 0
		return 0 if iv < 0 else 100 if iv > 100 else iv

	def is_cancelled(self) -> bool:
		with Session(db_engine) as session:
			stmt = select(MapTaskDB).where(MapTaskDB.id == self.task_id)
			obj = session.exec(stmt).first()
			if not obj:
				# If task is missing, treat as cancelled for safety
				return True
			return obj.status == MapTaskStatus.CANCELLED

	def update_progress(self, percent: int, phase: str | None = None, description: str | None = None) -> None:
		p = self._clamp_percent(percent)
		ph = (phase or "").strip() or None
		desc = (description or "").strip() or None

		try:
			with Session(db_engine) as session:
				row = MapTaskProgressDB(
					map_task_id=self.task_id,
					user_id=self.user_id,
					percent=p,
					description=desc,
					phase=ph,
				)
				session.add(row)
				session.commit()
		except Exception as e:
			# Log and continue; progress persistence shouldn't crash the worker
			logger.debug("progress insert failed for task %s: %s", self.task_id, e)

	def record_error(self, error_msg: str, phase: str | None = None, percent: int | None = None, description: str | None = None) -> None:
		ph = (phase or "").strip() or None
		desc = (description or "").strip() or None
		msg = (error_msg or "").strip() or "Error"
		p = None if percent is None else self._clamp_percent(percent)

		try:
			with Session(db_engine) as session:
				row = MapTaskProgressDB(
					map_task_id=self.task_id,
					user_id=self.user_id,
					percent=p if p is not None else 0,
					description=desc,
					phase=ph,
					error_msg=msg,
				)
				session.add(row)
				session.commit()
		except Exception as e:
			logger.debug("record_error failed for task %s: %s", self.task_id, e)
	
	def record_file(self, file_type:str, file_path: str) -> None: 
		try:
			with Session(db_engine) as session:
				row = MapTaskFileDB(
					map_task_id=self.task_id,
					user_id=self.user_id,
					file_type=file_type,
					file_path=file_path
				)
				session.add(row)
				session.commit()
		except Exception as e:
			logger.debug("record_file failed for task %s: %s", self.task_id, e)


def _quick_update_task(task_id: int, **fields) -> None:
	"""Update a MapTaskDB row with minimal session lifetime."""
	with Session(db_engine) as session:
		stmt = select(MapTaskDB).where(MapTaskDB.id == task_id)
		obj = session.exec(stmt).first()
		if not obj:
			return
		for k, v in fields.items():
			setattr(obj, k, v)
		session.add(obj)
		session.commit()


def _load_task(task_id: int) -> MapTaskDB | None:
	with Session(db_engine) as session:
		stmt = select(MapTaskDB).where(MapTaskDB.id == task_id)
		return session.exec(stmt).first()


def process_map_task(task_id: int) -> None:
	"""Background job: run GIS engine for a map task.

	Steps:
	- fetch task by id; if not found or already terminal, exit
	- mark PROCESSING and set started_at
	- build EngineConfigs from stored JSON factors
	- run SiteSuitabilityEngine with input/output paths from settings
	- on success: set SUCCESS and ended_at; on failure: set FAILURE and error_msg
	"""
	task = _load_task(task_id)
	if not task:
		logger.warning("MapTask %s not found; skipping.", task_id)
		return

	if task.status in (MapTaskStatus.SUCCESS, MapTaskStatus.FAILURE, MapTaskStatus.CANCELLED):
		logger.info("MapTask %s already in terminal state %s; skipping.", task_id, task.status)
		return

	# Transition to PROCESSING quickly
	_quick_update_task(
		task_id,
		status=MapTaskStatus.PROCESSING,
		started_at=task.started_at or datetime.now(timezone.utc),
		error_msg=None,
	)
	user_id = 0
	try:
		# Reload current snapshot (avoid holding session for long)
		task = _load_task(task_id)
		user_id = task.user_id
		if not task:
			raise RuntimeError("Task disappeared during processing")
		if task.status == MapTaskStatus.CANCELLED:
			logger.info("MapTask %s cancelled before start; aborting.", task_id)
			return

		# Build engine configs from stored JSON
		try:
			constraint_factors = json.loads(task.constraint_factors or "[]")
		except Exception:
			constraint_factors = []
		try:
			suitability_factors = json.loads(task.suitability_factors or "[]")
		except Exception:
			suitability_factors = []

		restricted: List[RestrictedFactor] = []
		for cf in constraint_factors:
			try:
				kind = str(cf.get("kind"))
				value = cf.get("value")
				buffer_distance = int(value) if value is not None else 0
				restricted.append(RestrictedFactor(kind=kind, buffer_distance=buffer_distance))
			except Exception as e:
				logger.warning("Skip invalid constraint factor on task %s: %r (%s)", task_id, cf, e)

		suitables: List[SuitabilityFactor] = []
		for sf in suitability_factors:
			try:
				kind = str(sf.get("kind"))
				weight = float(sf.get("weight"))
				ranges_src = sf.get("ranges") or []
				ranges: List[Tuple[float, float, int]] = []
				for r in ranges_src:
					ranges.append((float(r.get("start")), float(r.get("end")), int(r.get("points"))))
				# allow None ranges if empty to defer to engine defaults
				suitables.append(
					SuitabilityFactor(kind=kind, weight=weight, ranges=ranges or None)
				)
			except Exception as e:
				logger.warning("Skip invalid suitability factor on task %s: %r (%s)", task_id, sf, e)

		configs = EngineConfigs(restricted_factors=restricted, suitability_factors=suitables)

		# Resolve IO paths
		data_dir: Path = settings.INPUT_DATA_DIR
		base_out: Path = settings.OUTPUT_DATA_DIR
		task_out: Path = base_out / "engine" / f"task-{task_id}"
		task_out.mkdir(parents=True, exist_ok=True)

		# Run engine for the selected district code
		engine = SiteSuitabilityEngine(str(data_dir), str(task_out), configs)
		selected = [task.district]
		monitor = MapTaskMonitor(task_id,user_id)
		monitor.update_progress(0, "init", "Starting")
		results = engine.run(selected_districts=selected, monitor=monitor)
		if not monitor.is_cancelled():
			monitor.update_progress(100, "success", "Completed")

			_quick_update_task(
				task_id,
				status=MapTaskStatus.SUCCESS,
				ended_at=datetime.now(timezone.utc),
			)
	except Exception as e:
		# Truncate error message to fit DB column (255)
		msg = str(e)
		if len(msg) > 250:
			msg = msg[:247] + "..."
		logger.exception("MapTask %s failed: %s", task_id, msg)
		try:
			MapTaskMonitor(task_id, user_id).record_error(msg, phase="error", description="Failed")
		except Exception:
			pass
		_quick_update_task(
			task_id,
			status=MapTaskStatus.FAILURE,
			error_msg=msg,
			ended_at=datetime.now(timezone.utc),
		)
