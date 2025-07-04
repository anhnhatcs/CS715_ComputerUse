"""
Utility functions for parsing and processing log files.
"""

import json
import os
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Step:
    """Represents a single step in a task."""
    tool_name: str
    tool_input: Dict[str, Any]
    tool_output: Dict[str, Any]
    success: bool
    timestamp: str
    efficiency: Optional[float] = None


@dataclass
class Task:
    """Represents a complete task with steps."""
    id: str
    category: str
    test_id: str
    instruction: str
    steps: List[Step]
    log_path: str


class LogParser:
    """Parser for log files."""
    
    @staticmethod
    def parse_json_log(log_path: str) -> Optional[Task]:
        """Parse a JSON log file and extract task and step information."""
        try:
            with open(log_path, 'r') as f:
                log_data = json.load(f)
            
            # Extract task information
            task_id = log_data.get("session_id", "unknown")
            category = "unknown"
            test_id = "unknown"
            
            # Look for session metadata
            for event in log_data.get("events", []):
                if event.get("type") == "session_metadata":
                    metadata = event.get("data", {})
                    if "Cat" in metadata:
                        category = metadata["Cat"]
                    if "Test_ID" in metadata:
                        test_id = metadata["Test_ID"]
            
            # Extract user instruction
            instruction = ""
            for event in log_data.get("events", []):
                if event.get("type") == "user_input":
                    data = event.get("data", {})
                    if "instruction" in data:
                        instruction = data["instruction"]
                        break
            
            # Create a Task object
            task = Task(
                id=task_id,
                category=category,
                test_id=test_id,
                instruction=instruction,
                steps=[],
                log_path=log_path
            )
            
            # Extract steps
            steps = LogParser.extract_steps_from_json(log_data)
            task.steps = steps
            
            return task
        
        except Exception as e:
            print(f"Error parsing JSON log: {e}")
            return None
    
    @staticmethod
    def extract_steps_from_json(log_data: Dict) -> List[Step]:
        """Extract steps from JSON log data."""
        steps = []
        tool_calls = []
        
        # Process events in chronological order
        for event in log_data.get("events", []):
            event_type = event.get("type")
            
            # Handle API responses (assistant actions)
            if event_type == "api_response":
                content = event.get("data", {}).get("content", [])
                
                for item in content:
                    item_type = item.get("type")
                    
                    # Handle tool uses
                    if item_type == "tool_use":
                        tool_id = item.get("id")
                        tool_name = item.get("name")
                        input_data = item.get("input", {})
                        
                        # Store tool call for later matching with results
                        tool_calls.append({
                            "id": tool_id,
                            "name": tool_name,
                            "input": input_data,
                            "timestamp": event.get("timestamp")
                        })
            
            # Handle tool results
            elif event_type == "tool_result":
                tool_use_id = event.get("data", {}).get("tool_use_id")
                result = event.get("data", {})
                
                # Find matching tool call
                matching_call = next(
                    (call for call in tool_calls if call["id"] == tool_use_id), 
                    None
                )
                
                if matching_call:
                    # Create a step
                    step = Step(
                        tool_name=matching_call["name"],
                        tool_input=matching_call["input"],
                        tool_output=result,
                        success="error" not in result,
                        timestamp=matching_call["timestamp"],
                        efficiency=None  # Efficiency will be determined during evaluation
                    )
                    
                    steps.append(step)
                    # Remove processed tool call
                    tool_calls = [call for call in tool_calls if call["id"] != tool_use_id]
        
        return steps


def get_unique_task_id(task: Task) -> str:
    """
    Generate a unique ID for a task.
    
    Format: <test_id>_<category>_<session_id>
    """
    return f"{task.test_id}_{task.category}_{task.id}"


def find_log_files(directory: str) -> List[str]:
    """Find all JSON log files in the given directory."""
    log_files = []
    
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.json'):
                log_files.append(os.path.join(root, file))
    
    return log_files


def save_evaluation(eval_result: Dict, output_path: str) -> None:
    """Save evaluation results to a JSON file."""
    with open(output_path, 'w') as f:
        json.dump(eval_result, f, indent=2)


def load_evaluation(input_path: str) -> Dict:
    """Load evaluation results from a JSON file."""
    with open(input_path, 'r') as f:
        return json.load(f)


def format_timestamp() -> str:
    """Format current timestamp for filenames."""
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def get_task_key(task: Task) -> str:
    """Get a unique key for a task."""
    return f"{task.category}_{task.test_id}"


def get_default_eval_path() -> str:
    """Get default path for saving evaluations."""
    eval_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "evaluations")
    os.makedirs(eval_dir, exist_ok=True)
    return eval_dir


def get_default_log_path() -> str:
    """Get default path for log files."""
    log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "logs")
    os.makedirs(log_dir, exist_ok=True)
    return log_dir


def get_default_screenshot_path() -> str:
    """Get default path for screenshots."""
    screenshot_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "screenshots")
    os.makedirs(screenshot_dir, exist_ok=True)
    return screenshot_dir
