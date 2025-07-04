"""
Command-line evaluation tool for computing task metrics.
"""

import json
import os
from typing import List, Dict

from computeruse.utils.utils import LogParser, get_unique_task_id
from computeruse.analysis.metrics import (
    MetricsCalculator, 
    EvaluationResult, 
    aggregate_metrics, 
    format_metrics_report, 
    format_aggregate_report
)


def load_evaluations(evaluations_file: str) -> Dict[str, EvaluationResult]:
    """Load evaluations from JSON file."""
    if not os.path.exists(evaluations_file):
        return {}
    
    try:
        with open(evaluations_file, 'r') as f:
            data = json.load(f)
        
        evaluations = {}
        for task_id, eval_data in data.items():
            evaluations[task_id] = EvaluationResult(**eval_data)
        
        return evaluations
    except Exception as e:
        print(f"Error loading evaluations: {e}")
        return {}


def save_evaluations(evaluations: Dict[str, EvaluationResult], evaluations_file: str) -> None:
    """Save evaluations to JSON file."""
    # Convert EvaluationResult objects to dictionaries
    evaluations_dict = {task_id: eval_result.to_dict() 
                        for task_id, eval_result in evaluations.items()}
    
    os.makedirs(os.path.dirname(evaluations_file), exist_ok=True)
    
    with open(evaluations_file, 'w') as f:
        json.dump(evaluations_dict, f, indent=2)


def evaluate_task(log_file: str, evaluations_file: str, save: bool = True) -> EvaluationResult:
    """Evaluate a task from a log file and optionally save results."""
    parser = LogParser(log_file)
    tasks = parser.parse_tasks()
    
    if not tasks:
        print(f"No tasks found in log file: {log_file}")
        return None
    
    # Use the first task for now
    task = tasks[0]
    task_id = get_unique_task_id(task)
    
    print(f"Evaluating task {task_id}: {task.name}")
    
    # Load existing evaluations
    evaluations = load_evaluations(evaluations_file)
    
    # Calculate metrics
    calculator = MetricsCalculator(task)
    metrics = calculator.calculate_metrics()
    
    # Create evaluation result
    evaluation = EvaluationResult(
        task_id=task_id,
        task_name=task.name,
        log_file=log_file,
        metrics=metrics
    )
    
    # Display metrics
    print("\n" + format_metrics_report(evaluation))
    
    if save:
        # Save updated evaluations
        evaluations[task_id] = evaluation
        save_evaluations(evaluations, evaluations_file)
        print(f"Evaluation saved to {evaluations_file}")
    
    return evaluation


def evaluate_directory(
    log_dir: str, 
    evaluations_file: str, 
    save: bool = True
) -> List[EvaluationResult]:
    """Evaluate all log files in a directory."""
    results = []
    
    # Get all JSON files in the directory
    log_files = [os.path.join(log_dir, f) for f in os.listdir(log_dir) 
                if f.endswith('.json') and os.path.isfile(os.path.join(log_dir, f))]
    
    if not log_files:
        print(f"No JSON log files found in directory: {log_dir}")
        return results
    
    # Load existing evaluations
    evaluations = load_evaluations(evaluations_file)
    
    # Evaluate each log file
    for log_file in log_files:
        parser = LogParser(log_file)
        tasks = parser.parse_tasks()
        
        if not tasks:
            print(f"No tasks found in log file: {log_file}")
            continue
        
        # Use the first task for now
        task = tasks[0]
        task_id = get_unique_task_id(task)
        
        print(f"Evaluating task {task_id}: {task.name}")
        
        # Calculate metrics
        calculator = MetricsCalculator(task)
        metrics = calculator.calculate_metrics()
        
        # Create evaluation result
        evaluation = EvaluationResult(
            task_id=task_id,
            task_name=task.name,
            log_file=log_file,
            metrics=metrics
        )
        
        results.append(evaluation)
        
        if save:
            # Save updated evaluations
            evaluations[task_id] = evaluation
    
    if save and results:
        save_evaluations(evaluations, evaluations_file)
        print(f"Evaluations saved to {evaluations_file}")
    
    # Display aggregate metrics
    if results:
        agg_metrics = aggregate_metrics([r.metrics for r in results])
        print("\n" + format_aggregate_report(agg_metrics, len(results)))
    
    return results


def display_evaluations(evaluations_file: str):
    """Display all evaluations in a file."""
    evaluations = load_evaluations(evaluations_file)
    
    if not evaluations:
        print(f"No evaluations found in {evaluations_file}")
        return
    
    print(f"Found {len(evaluations)} evaluations:\n")
    
    for i, (task_id, evaluation) in enumerate(evaluations.items(), 1):
        print(f"{i}. Task: {evaluation.task_name}")
        print(f"   ID: {task_id}")
        print(f"   Log file: {evaluation.log_file}")
        print()
    
    # Calculate and display aggregate metrics
    metrics_list = [e.metrics for e in evaluations.values()]
    agg_metrics = aggregate_metrics(metrics_list)
    print(format_aggregate_report(agg_metrics, len(evaluations)))


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Evaluate Claude Computer Use logs")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Evaluate a single log file
    eval_parser = subparsers.add_parser("evaluate", help="Evaluate a single log file")
    eval_parser.add_argument("log_file", help="Path to log file")
    eval_parser.add_argument("--output", "-o", default="data/evaluations/evaluations.json", 
                           help="Path to save evaluations")
    eval_parser.add_argument("--no-save", action="store_true", 
                           help="Don't save evaluation results")
    
    # Evaluate all log files in a directory
    dir_parser = subparsers.add_parser("evaluate-dir", help="Evaluate all log files in a directory")
    dir_parser.add_argument("log_dir", help="Path to directory containing log files")
    dir_parser.add_argument("--output", "-o", default="data/evaluations/evaluations.json", 
                          help="Path to save evaluations")
    dir_parser.add_argument("--no-save", action="store_true", 
                          help="Don't save evaluation results")
    
    # Display evaluations
    list_parser = subparsers.add_parser("list", help="List all evaluations")
    list_parser.add_argument("evaluations_file", nargs="?", 
                           default="data/evaluations/evaluations.json",
                           help="Path to evaluations file")
    
    args = parser.parse_args()
    
    if args.command == "evaluate":
        evaluate_task(args.log_file, args.output, not args.no_save)
    elif args.command == "evaluate-dir":
        evaluate_directory(args.log_dir, args.output, not args.no_save)
    elif args.command == "list":
        display_evaluations(args.evaluations_file)
    else:
        parser.print_help()
