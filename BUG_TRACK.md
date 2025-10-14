
# Development Bug Tracker

This file is intended to be used during development. Each entry contains: brief title, symptoms, reproduction steps, affected files, likely root cause, commit references (if applicable), priority, owner (suggested), acceptance criteria, and suggested tests or mitigation tasks.

Guidance:
- Use `git show <hash>` to view the fix/introducing diffs.
- Mark issues with priority: P0 (blocker), P1 (high), P2 (medium), P3 (low/cleanup).

---

### BUG-001: Unit tests failing due to GIS engine/processor API changes
- Symptoms: Backend unit tests fail around GIS processing and map task orchestration.
- Reproduce (quick):
  1. cd backend
 2. pytest tests -q (or run failing tests found in CI logs)
- Affected files:
  - `backend/app/gis/engine.py`
  - `backend/app/gis/processor.py`
- Likely root cause: Behavior or signature changes in core engine/processor functions used by tests.
- Commits: 41c56772bdc4... ("backend: fix unit tests") — inspect for the exact change that made tests fail/fixed them.
- Priority: P1
- Owner: assign to backend/GIS owner
- Acceptance criteria:
  - Unit tests that previously failed are passing.
  - Behavioural contract of the processor functions is documented in a small test or docstring.
- Suggested work/tickets:
  - Add focused unit tests for processor entry points (happy and edge cases).
  - Create a small integration test that runs a trivial map task through the processor using mocked raster inputs.

---

### BUG-002: Build errors in admin routes / storage
- Symptoms: Local build/CI shows import or runtime errors related to admin endpoints or storage module.
- Reproduce (quick):
  1. cd backend
 2. run `python -m pytest` or run a static import smoke test:
     python -c "import app.api.routes.admin; import app.core.storage; print('ok')"
- Affected files:
  - `backend/app/api/routes/admin.py`
  - `backend/app/core/storage.py`
- Likely root cause: Refactor introduced mismatched imports or changed function signatures.
- Commits: 893530322aa5... ("fix build errors")
- Priority: P1
- Owner: backend API owner
- Acceptance criteria:
  - `python -c` smoke import above prints `ok` without error.
  - CI build step that failed now passes.
- Suggested tests:
  - Add a small smoke test that imports admin routes and storage functions.

---

### BUG-003: Cancelled tasks incorrectly marked as SUCCESS
- Symptoms: Task lifecycle shows cancelled background tasks as SUCCESS in the UI/DB.
- Reproduce (quick):
  1. Create a map task via API
 2. Cancel it (simulate cancellation in TaskMonitor or API endpoint)
 3. Inspect task status via admin endpoint or DB
- Affected files:
  - Task state handling (likely `backend/app/task/service.py` and map-task monitor code)
- Likely root cause: Final status update path overwrote CANCELLED with SUCCESS when finalizing.
- Commits: b9724c1a521a... (fix)
- Priority: P1
- Owner: backend task/service owner
- Acceptance criteria:
  - When a task is cancelled, final state remains CANCELLED and is visible via API and UI.
  - No regression where successful tasks are mis-labelled.
- Suggested tests:
  - Unit test for task lifecycle transitions covering CANCELLED and SUCCESS terminal states.
  - Integration test that requests cancellation mid-run and asserts final DB state.

---

### BUG-004: build_ranges / suitability factor tuple creation and logging
- Symptoms: Errors or confusing logs when users define scoring breakpoints; UI may surface error messages.
- Reproduce (quick):
  1. In web UI create a new map with edge-case suitability factor values (empty breakpoints, None, out-of-range values) OR run the backend function directly.
 2. Check backend logs and error messages.
- Affected files:
  - `backend/app/gis/engine_models.py`
  - `backend/app/gis/processor.py`
  - `backend/app/models.py`
  - Webfront inputs: `webfront/src/crud-dashboard/components/new-map/SuitabilityFactorsStep.tsx`
- Likely root cause: Unsafe tuple/list construction from user inputs and insufficient input validation; logging not descriptive.
- Commits: 0e26d95e3db2... (improve error logging and tuple creation)
- Priority: P2
- Owner: backend GIS + webfront owner (needs coordination)
- Acceptance criteria:
  - Invalid user inputs produce clear, actionable error messages.
  - `build_ranges` handles empty/None inputs safely and returns a validated structure.
- Suggested tests:
  - Unit tests for `build_ranges` with:
    - empty list
    - None values
    - single breakpoint
    - breakpoints out of expected range

---

### BUG-005: Raster nodata/reclassify/union edge-cases
- Symptoms: Raster processes fail or produce incorrect outputs when nodata values are present; combination results unexpected.
- Reproduce (quick):
  1. Create small raster files (3x3 or 10x10) with a nodata value and try reclassify/union in engine functions.
 2. Run the specific function (e.g., `RPL_Reclassify`, `RPL_Union_analysis`) and compare output to expected.
- Affected files:
  - `backend/app/gis/functions.py`
  - `backend/app/gis/engine.py`
  - `backend/app/gis/processor.py`
  - `backend/app/gis/__init__.py`
- Likely root cause: Missing nodata propagation logic or wrong dtype assumptions (remap ranges not validated).
- Commits: 0229c96..., fdf1324..., 35ec4e3... (various RPL fixes)
- Priority: P1
- Owner: backend GIS owner
- Acceptance criteria:
  - Reclassify and union handle nodata correctly (nodata preserved or handled per spec) and outputs match expected arrays.
  - Reclassify remap ranges validated and raise descriptive errors for invalid remap mappings.
- Suggested tests:
  - Small raster unit tests using NumPy arrays and temporary GeoTIFF/COG files. Use rasterio/GDAL in test env or mock where not available.

---

### BUG-006: Progress / TaskMonitor messaging clarity
- Symptoms: Progress messages are unclear or not granular; admin API progress endpoints need improvements.
- Reproduce: Run a map task and observe progress messages in logs and admin progress endpoint responses.
- Affected files:
  - `backend/app/task/service.py`
  - Task monitor definitions and integration points
- Likely root cause: Low message granularity and inconsistent update patterns.
- Commits: various (improving messages and integrating TaskMonitor)
- Priority: P3
- Owner: backend task/service owner
- Acceptance criteria:
  - Progress endpoint returns a clear sequence of messages and percentages.
  - UI displays consistent progress based on endpoint output.
- Suggested tests:
  - Integration test that runs a dummy task and asserts progress events recorded in DB or returned by API.
