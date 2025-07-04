"""
Metric calculation functions for evaluating task performance.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from computeruse.utils.utils import Task, Step, get_unique_task_id


@dataclass
class TaskMetrics:
    """Metrics for a single task."""
    task_id: str
    task_success_rate: float
    step_success_rate: float
    average_efficiency: float
    total_steps: int
    successful_steps: int
    failed_steps: int
    notes: Optional[str] = None

    def to_dict(self) -> Dict:
        """Convert metrics to dictionary."""
        return {
            "task_id": self.task_id,
            "task_success_rate": self.task_success_rate,
            "step_success_rate": self.step_success_rate,
            "average_efficiency": self.average_efficiency,
            "total_steps": self.total_steps,
            "successful_steps": self.successful_steps,
            "failed_steps": self.failed_steps,
            "notes": self.notes or ""
        }


@dataclass
class EvaluationResult:
    """Evaluation result for a set of tasks."""
    metrics: List[TaskMetrics]
    timestamp: str
    evaluator: str
    notes: Optional[str] = None


class MetricsCalculator:
    """Calculate metrics from task data."""
    
    @staticmethod
    def calculate_task_success_rate(task: Task) -> float:
        """
        Calculate Task Success Rate (TSR).
        
        TSR is 1.0 if all steps are successful, 0.0 otherwise.
        """
        if not task.steps:
            return 0.0
        
        failed_steps = [step for step in task.steps if not step.success]
        return 1.0 if not failed_steps else 0.0
    
    @staticmethod
    def calculate_step_success_rate(task: Task) -> float:
        """
        Calculate Step Success Rate (SSR).
        
        SSR is the proportion of successful steps.
        """
        if not task.steps:
            return 0.0
        
        successful_steps = sum(1 for step in task.steps if step.success)
        return successful_steps / len(task.steps)
    
    @staticmethod
    def calculate_average_efficiency(task: Task) -> float:
        """
        Calculate Average Efficiency (AE).
        
        AE is the average efficiency across all successful steps.
        """
        successful_steps = [step for step in task.steps if step.success]
        if not successful_steps:
            return 0.0
        
        total_efficiency = sum(step.efficiency for step in successful_steps if step.efficiency is not None)
        valid_steps = sum(1 for step in successful_steps if step.efficiency is not None)
        
        return total_efficiency / valid_steps if valid_steps > 0 else 0.0
    
    @classmethod
    def calculate_metrics(cls, task: Task) -> TaskMetrics:
        """Calculate all metrics for a task."""
        tsr = cls.calculate_task_success_rate(task)
        ssr = cls.calculate_step_success_rate(task)
        ae = cls.calculate_average_efficiency(task)
        
        total_steps = len(task.steps)
        successful_steps = sum(1 for step in task.steps if step.success)
        failed_steps = total_steps - successful_steps
        
        return TaskMetrics(
            task_id=get_unique_task_id(task),
            task_success_rate=tsr,
            step_success_rate=ssr,
            average_efficiency=ae,
            total_steps=total_steps,
            successful_steps=successful_steps,
            failed_steps=failed_steps
        )


def aggregate_metrics(metrics_list: List[TaskMetrics]) -> Dict:
    """
    Aggregate metrics across multiple tasks.
    
    Returns a dictionary with the following keys:
    - avg_task_success_rate: Average Task Success Rate
    - avg_step_success_rate: Average Step Success Rate
    - avg_average_efficiency: Average Efficiency
    - total_tasks: Total number of tasks
    - successful_tasks: Number of tasks with TSR = 1.0
    - total_steps: Total number of steps across all tasks
    - successful_steps: Total number of successful steps
    - failed_steps: Total number of failed steps
    """
    if not metrics_list:
        return {
            "avg_task_success_rate": 0.0,
            "avg_step_success_rate": 0.0,
            "avg_average_efficiency": 0.0,
            "total_tasks": 0,
            "successful_tasks": 0,
            "total_steps": 0,
            "successful_steps": 0,
            "failed_steps": 0
        }
    
    total_tasks = len(metrics_list)
    successful_tasks = sum(1 for m in metrics_list if m.task_success_rate == 1.0)
    
    avg_tsr = sum(m.task_success_rate for m in metrics_list) / total_tasks
    avg_ssr = sum(m.step_success_rate for m in metrics_list) / total_tasks
    avg_ae = sum(m.average_efficiency for m in metrics_list) / total_tasks
    
    total_steps = sum(m.total_steps for m in metrics_list)
    successful_steps = sum(m.successful_steps for m in metrics_list)
    failed_steps = sum(m.failed_steps for m in metrics_list)
    
    return {
        "avg_task_success_rate": avg_tsr,
        "avg_step_success_rate": avg_ssr,
        "avg_average_efficiency": avg_ae,
        "total_tasks": total_tasks,
        "successful_tasks": successful_tasks,
        "total_steps": total_steps,
        "successful_steps": successful_steps,
        "failed_steps": failed_steps
    }


def format_metrics_report(metrics: TaskMetrics) -> str:
    """Format metrics as a readable report."""
    report = f"Task ID: {metrics.task_id}\n"
    report += f"Task Success Rate (TSR): {metrics.task_success_rate:.2f}\n"
    report += f"Step Success Rate (SSR): {metrics.step_success_rate:.2f}\n"
    report += f"Average Efficiency (AE): {metrics.average_efficiency:.2f}\n"
    report += f"Total Steps: {metrics.total_steps}\n"
    report += f"Successful Steps: {metrics.successful_steps}\n"
    report += f"Failed Steps: {metrics.failed_steps}\n"
    
    if metrics.notes:
        report += f"Notes: {metrics.notes}\n"
    
    return report


def format_aggregate_report(agg_metrics: Dict) -> str:
    """Format aggregate metrics as a readable report."""
    report = "Aggregate Metrics\n"
    report += "================\n"
    report += f"Average Task Success Rate: {agg_metrics['avg_task_success_rate']:.2f}\n"
    report += f"Average Step Success Rate: {agg_metrics['avg_step_success_rate']:.2f}\n"
    report += f"Average Efficiency: {agg_metrics['avg_average_efficiency']:.2f}\n"
    report += f"Total Tasks: {agg_metrics['total_tasks']}\n"
    report += f"Successful Tasks: {agg_metrics['successful_tasks']}\n"
    report += f"Total Steps: {agg_metrics['total_steps']}\n"
    report += f"Successful Steps: {agg_metrics['successful_steps']}\n"
    report += f"Failed Steps: {agg_metrics['failed_steps']}\n"
    
    return report
