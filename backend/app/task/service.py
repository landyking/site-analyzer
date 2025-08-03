from typing import List, Optional
from datetime import datetime
import random
from pydantic import EmailStr

from .models import (
    MapTask,
    MapTaskDetails,
    TaskStatus,
    ConstraintFactor,
    SuitabilityFactor,
    MapTaskFile,
    CreateMapTaskReq
)

# Import the GIS processor
from ..gis.processor import start_map_task_processing, cancel_task_processing

# Mock database - this would be replaced with actual database interaction
_mock_tasks = {}
_next_id = 1


def get_user_map_tasks(user_id: int, completed: Optional[bool] = None) -> List[MapTask]:
    """
    Get all map tasks for a user, optionally filtered by completion status.
    """
    tasks = list(_mock_tasks.values())
    # Filter by user_id
    tasks = [task for task in tasks if task.user_id == user_id]
    
    # Filter by completion status if specified
    if completed is not None:
        if completed:
            # Tasks with status SUCCESS or FAILURE are considered completed
            tasks = [task for task in tasks if task.status in [TaskStatus.SUCCESS, TaskStatus.FAILURE]]
        else:
            # Tasks with other statuses are considered not completed
            tasks = [task for task in tasks if task.status not in [TaskStatus.SUCCESS, TaskStatus.FAILURE]]
    
    return tasks


def get_map_task(user_id: int, task_id: int) -> Optional[MapTaskDetails]:
    """
    Get a specific map task by ID for a user.
    """
    task = _mock_tasks.get(task_id)
    if task and task.user_id == user_id:
        # In a real implementation, we would fetch the latest task details from the database
        # For our mock implementation, we need to return the task with any updated fields
        
        # This is a simplified approach - in a real system, task data would be consistently 
        # updated in the database
        if hasattr(task, '_task_details'):
            return task._task_details
            
        # If no detailed version exists yet, create one
        task_details = MapTaskDetails(
            **task.dict(),
            files=[],  # In a real implementation, fetch associated files
            constraint_factors=[],  # In a real implementation, fetch constraint factors
            suitability_factors=[]  # In a real implementation, fetch suitability factors
        )
        
        # Store for future reference
        task._task_details = task_details
        
        return task_details
    return None


def create_map_task(user_id: int, user_email: EmailStr, req: CreateMapTaskReq) -> MapTaskDetails:
    """
    Create a new map task for a user.
    """
    global _next_id
    
    # In a real implementation, district_name would be fetched from a database
    district_name = f"District {req.district_code}"
    
    # Create a new map task
    task = MapTask(
        id=_next_id,
        name=req.name,
        user_id=user_id,
        user_email=user_email,
        district_code=req.district_code,
        district_name=district_name,
        status=TaskStatus.CREATED,
        created_at=datetime.now()
    )
    
    # Store in mock database
    _mock_tasks[_next_id] = task
    _next_id += 1
    
    # Return as MapTaskDetails
    task_details = MapTaskDetails(
        **task.dict(),
        files=[],
        constraint_factors=req.constraint_factors,
        suitability_factors=req.suitability_factors
    )
    
    # Start processing the task in the background
    start_map_task_processing(task_details)
    
    return task_details


def cancel_map_task(user_id: int, task_id: int) -> bool:
    """
    Cancel a map task if it belongs to the user and is in a cancellable state.
    """
    task = _mock_tasks.get(task_id)
    if not task or task.user_id != user_id:
        return False
    
    # Only tasks that are CREATED or PROCESSING can be cancelled
    if task.status in [TaskStatus.CREATED, TaskStatus.PROCESSING]:
        # Try to cancel the task processing
        cancelled = cancel_task_processing(task_id)
        
        # Update task status
        task.status = TaskStatus.CANCELLED
        task.ended_at = datetime.now()
        return True
    
    return False
