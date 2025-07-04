"""
Main entry point for the CS715 Computer Use Evaluation package.

This module provides high-level functions to start different components
of the evaluation system.
"""

import os
import sys
from typing import List, Optional

from computeruse.analysis.metrics import (
    EvaluationResult,
    MetricsCalculator, 
    aggregate_metrics, 
)
from computeruse.ui.run_eval import run_evaluation
from computeruse.ui.streamlit_app import run_streamlit_app
from computeruse.utils.utils import LogParser


# Add the parent directory to sys.path to allow importing modules from the package
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)


def run_ui(port: int = 8501) -> None:
    """
    Start the Streamlit UI.

    Args:
        port: The port to run the Streamlit UI on (default: 8501)
    """
    run_streamlit_app(port=port)


def run_evaluation_cli(
    log_file: str, 
    output_file: Optional[str] = None,
    save_results: bool = True
) -> EvaluationResult:
    """
    Run evaluation on a log file from the command line.

    Args:
        log_file: Path to the log file to evaluate
        output_file: Path to save evaluation results (default: None, uses default path)
        save_results: Whether to save results to file (default: True)

    Returns:
        EvaluationResult: The evaluation results
    """
    return run_evaluation(log_file, output_file, save_results)


def analyze_logs(log_files: List[str]) -> dict:
    """
    Analyze multiple log files and return aggregate metrics.

    Args:
        log_files: List of paths to log files

    Returns:
        dict: Aggregate metrics for all tasks
    """
    all_metrics = []
    
    for log_file in log_files:
        parser = LogParser(log_file)
        tasks = parser.parse_tasks()
        
        if not tasks:
            print(f"No tasks found in log file: {log_file}")
            continue
        
        # Use the first task for now
        task = tasks[0]
        calculator = MetricsCalculator(task)
        metrics = calculator.calculate_metrics()
        all_metrics.append(metrics)
    
    # Calculate aggregate metrics
    if all_metrics:
        return aggregate_metrics(all_metrics)
    
    return {}


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="CS715 Computer Use Evaluation Tool")
    
    subparsers = parser.add_subparsers(
        dest="command", help="Command to run")
    
    # UI command
    ui_parser = subparsers.add_parser(
        "ui", help="Start the Streamlit UI")
    ui_parser.add_argument(
        "--port", type=int, default=8501, 
        help="Port to run the UI on")
    
    # Evaluate command
    eval_parser = subparsers.add_parser(
        "evaluate", help="Evaluate a log file")
    eval_parser.add_argument(
        "log_file", help="Path to log file")
    eval_parser.add_argument(
        "--output", "-o", 
        help="Path to save evaluation results")
    eval_parser.add_argument(
        "--no-save", action="store_true", 
        help="Don't save evaluation results")
    
    args = parser.parse_args()
    
    if args.command == "ui":
        run_ui(port=args.port)
    elif args.command == "evaluate":
        run_evaluation_cli(
            args.log_file, 
            args.output, 
            not args.no_save
        )
    else:
        parser.print_help()
