#!/usr/bin/env python3
"""
Simple test to simulate the evaluation save process
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from utils import LogParser, get_unique_task_id
from run_eval import EvaluationStorage, EvaluationResult
from datetime import datetime

def test_save_evaluation():
    """Test the save evaluation process for session_3_Basic_App_File_20250701_035818.json"""
    
    # Parse the log file
    log_file = "logs/session_3_Basic_App_File_20250701_035818.json"
    
    if not os.path.exists(log_file):
        print(f"❌ Error: Log file {log_file} not found")
        return
    
    print(f"✅ Testing save evaluation for: {log_file}")
    
    parser = LogParser()
    task = parser.parse_log_file(log_file)
    
    if task is None:
        print("❌ Error: Failed to parse task from log file")
        return
    
    unique_task_id = get_unique_task_id(task)
    print(f"Generated unique task ID: {unique_task_id}")
    
    # Create a test evaluation
    evaluation = EvaluationResult(
        task_id=unique_task_id,
        task_successful=True,  # Test value
        step_failures=[],
        optimal_step_count=5,  # Test value
        notes="Test evaluation from debug script",
        evaluated_by="Debug Script",
        evaluation_date=datetime.now().isoformat()
    )
    
    print(f"Created evaluation object:")
    print(f"  - task_id: {evaluation.task_id}")
    print(f"  - task_successful: {evaluation.task_successful}")
    print(f"  - evaluation_date: {evaluation.evaluation_date}")
    
    # Try to save it
    storage = EvaluationStorage()
    
    print(f"\nTesting save to: {storage.evaluations_file}")
    
    # Check current state
    existing_evaluations = storage.load_evaluations()
    print(f"Existing evaluations count: {len(existing_evaluations)}")
    
    if unique_task_id in existing_evaluations:
        print(f"⚠️  Task ID {unique_task_id} already exists!")
    else:
        print(f"✅ Task ID {unique_task_id} is new")
    
    # Manually do what save_evaluation does (without Streamlit)
    print("\n🔧 Manual save process...")
    
    import json
    
    # Load existing
    evaluations = storage.load_evaluations()
    print(f"Loaded {len(evaluations)} existing evaluations")
    
    # Add new one
    evaluations[evaluation.task_id] = evaluation
    print(f"Added evaluation, now have {len(evaluations)} evaluations")
    
    # Convert to dict
    data = {}
    for task_id, eval_result in evaluations.items():
        data[task_id] = {
            "task_id": eval_result.task_id,
            "task_successful": eval_result.task_successful,
            "step_failures": eval_result.step_failures,
            "optimal_step_count": eval_result.optimal_step_count,
            "notes": eval_result.notes,
            "evaluated_by": eval_result.evaluated_by,
            "evaluation_date": eval_result.evaluation_date
        }
    
    print(f"Converted to dict, will write {len(data)} evaluations")
    
    # Check file permissions
    directory = os.path.dirname(storage.evaluations_file)
    can_write = os.access(directory, os.W_OK)
    print(f"Directory {directory} writable: {can_write}")
    
    if os.path.exists(storage.evaluations_file):
        file_writable = os.access(storage.evaluations_file, os.W_OK)
        print(f"File {storage.evaluations_file} writable: {file_writable}")
    
    # Try to write
    try:
        with open(storage.evaluations_file, 'w') as f:
            json.dump(data, f, indent=2)
        print("✅ Successfully wrote to file")
        
        # Verify
        with open(storage.evaluations_file, 'r') as f:
            verification_data = json.load(f)
            if evaluation.task_id in verification_data:
                print(f"✅ VERIFICATION SUCCESS - {evaluation.task_id} found in written file")
            else:
                print(f"❌ VERIFICATION FAILED - {evaluation.task_id} NOT found in written file")
                
    except Exception as e:
        print(f"❌ Error writing file: {e}")

if __name__ == "__main__":
    test_save_evaluation()
