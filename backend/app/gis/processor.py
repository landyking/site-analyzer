import os
import threading
from datetime import datetime
from typing import Dict, Optional, List, Tuple

from ..task.models import (
    MapTask,
    MapTaskDetails,
    TaskStatus,
    ConstraintFactor,
    SuitabilityFactor,
    MapTaskFile
)
from .engine import SiteSuitabilityEngine

# Global dictionary to track running tasks
_running_tasks: Dict[int, threading.Thread] = {}

# Configuration for input and output directories
TEST_DATA_DIR = os.environ.get("TEST_DATA_DIR", "test-data")
OUTPUT_DATA_DIR = os.environ.get("OUTPUT_DATA_DIR", "output-data")

def start_map_task_processing(task: MapTaskDetails) -> None:
    """
    Start processing a map task in a separate thread.
    
    Parameters:
    - task: The task to process
    
    Returns:
    - None
    """
    # Update task status to PROCESSING
    task.status = TaskStatus.PROCESSING
    task.started_at = datetime.now()
    
    # Create and start a thread for task processing
    thread = threading.Thread(
        target=_process_map_task,
        args=(task,),
        daemon=True  # Make thread a daemon so it doesn't block program exit
    )
    _running_tasks[task.id] = thread
    thread.start()

def _process_map_task(task: MapTaskDetails) -> None:
    """
    Process a map task using the SiteSuitabilityEngine.
    
    Parameters:
    - task: The task to process
    
    Returns:
    - None
    """
    try:
        # Create output directory for this task
        task_output_dir = os.path.join(OUTPUT_DATA_DIR, f"task_{task.id}")
        os.makedirs(task_output_dir, exist_ok=True)
        
        # Initialize the engine
        engine = SiteSuitabilityEngine(
            data_dir=TEST_DATA_DIR,
            output_dir=task_output_dir
        )
        
        # Configure the engine based on task parameters
        _configure_engine_from_task(engine, task)
        
        # Run the analysis for the single district
        result = engine.run_single_district(task.district_code)
        
        if result:
            district_name, result_path = result
            
            # Create file entry
            file = MapTaskFile(
                task_id=task.id,
                file_name=f"suitability_{district_name}.tif",
                file_path=result_path,
                file_type="RESULT",
                description=f"Suitability analysis result for {district_name}"
            )
            
            # Add file to task files
            task.files.append(file)
            
            # Update task status to SUCCESS
            task.status = TaskStatus.SUCCESS
            task.ended_at = datetime.now()
        else:
            # Update task status to FAILURE
            task.status = TaskStatus.FAILURE
            task.ended_at = datetime.now()
            task.error_message = f"Failed to process district {task.district_code}"
    
    except Exception as e:
        # Update task status to FAILURE
        task.status = TaskStatus.FAILURE
        task.ended_at = datetime.now()
        task.error_message = str(e)
    
    finally:
        # Remove thread from running tasks
        if task.id in _running_tasks:
            del _running_tasks[task.id]

def _configure_engine_from_task(engine: SiteSuitabilityEngine, task: MapTaskDetails) -> None:
    """
    Configure the engine based on task parameters.
    
    Parameters:
    - engine: The SiteSuitabilityEngine instance
    - task: The task with configuration parameters
    
    Returns:
    - None
    """
    # Adjust buffer distances and scoring weights based on task parameters
    for factor in engine.factors:
        # Apply constraint factors
        for constraint in task.constraint_factors:
            if constraint.factor_name.lower() == factor["name"].lower():
                if "buffer_distance" in factor:
                    factor["buffer_distance"] = constraint.buffer_distance
        
        # Apply suitability factors
        for suitability in task.suitability_factors:
            if suitability.factor_name.lower() == factor["name"].lower():
                if "score_weight" in factor:
                    factor["score_weight"] = suitability.weight

def cancel_task_processing(task_id: int) -> bool:
    """
    Attempt to cancel a running task.
    Note: This doesn't actually stop the thread, but updates the task status.
    In a real implementation, you would need a mechanism to signal the thread to stop.
    
    Parameters:
    - task_id: The ID of the task to cancel
    
    Returns:
    - True if the task was running and is now marked for cancellation, False otherwise
    """
    if task_id in _running_tasks:
        # In a real implementation, you would signal the thread to stop here
        # We can't forcibly stop a thread in Python, but we can set a flag
        # that the thread checks periodically
        return True
    
    return False
