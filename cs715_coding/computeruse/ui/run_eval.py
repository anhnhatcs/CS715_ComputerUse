"""
Main evaluation runner with Streamlit interface for human evaluation.
"""

import streamlit as st
import json
import os
import random
from datetime import datetime
from typing import Dict, List, Optional
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from computeruse.utils.utils import LogParser, Task, get_unique_task_id
from computeruse.analysis.metrics import (
    MetricsCalculator, 
    EvaluationResult, 
    TaskMetrics, 
    aggregate_metrics, 
    format_metrics_report, 
    format_aggregate_report
)


class EvaluationStorage:
    """Handles storage and retrieval of evaluation results."""
    
    def __init__(self, eval_dir: str = "evaluations"):
        """Initialize with the directory for storing evaluations."""
        self.eval_dir = eval_dir
        os.makedirs(self.eval_dir, exist_ok=True)
    
    def save_evaluation(self, evaluation: EvaluationResult) -> str:
        """Save evaluation results to a JSON file."""
        timestamp = evaluation.timestamp.replace(":", "-")
        filename = f"evaluation_{timestamp}.json"
        filepath = os.path.join(self.eval_dir, filename)
        
        with open(filepath, "w") as f:
            json.dump({
                "metrics": [m.to_dict() for m in evaluation.metrics],
                "timestamp": evaluation.timestamp,
                "evaluator": evaluation.evaluator,
                "notes": evaluation.notes
            }, f, indent=2)
        
        return filepath
    
    def load_evaluations(self) -> List[Dict]:
        """Load all evaluations from the directory."""
        evaluations = []
        
        for filename in os.listdir(self.eval_dir):
            if filename.endswith(".json"):
                try:
                    with open(os.path.join(self.eval_dir, filename), "r") as f:
                        eval_data = json.load(f)
                        evaluations.append(eval_data)
                except Exception as e:
                    print(f"Error loading {filename}: {e}")
        
        return evaluations
    
    def get_task_results(self, task_id: str) -> List[Dict]:
        """Get all evaluation results for a specific task."""
        task_results = []
        
        evaluations = self.load_evaluations()
        for eval_data in evaluations:
            for metric in eval_data.get("metrics", []):
                if metric.get("task_id") == task_id:
                    result = {
                        "timestamp": eval_data.get("timestamp", ""),
                        "evaluator": eval_data.get("evaluator", ""),
                        "metrics": metric
                    }
                    task_results.append(result)
        
        return task_results


def get_screenshots_for_task(task: Task, screenshots_dir: str) -> List[str]:
    """Get paths to screenshots for a task."""
    if not task or not os.path.exists(screenshots_dir):
        return []
    
    # Extract task ID components
    parts = get_unique_task_id(task).split("_")
    if len(parts) < 2:
        return []
    
    test_id, category = parts[0], parts[1]
    
    # Look for screenshots matching the pattern
    screenshots = []
    for filename in os.listdir(screenshots_dir):
        if filename.startswith(f"{test_id}_{category}") and (filename.endswith(".png") or filename.endswith(".jpg")):
            screenshots.append(os.path.join(screenshots_dir, filename))
    
    return screenshots


def format_task_summary(task: Task) -> str:
    """Format a summary of the task for display."""
    if not task:
        return "No task selected"
    
    task_id = get_unique_task_id(task)
    summary = f"Task ID: {task_id}\n"
    summary += f"Instruction: {task.instruction}\n"
    summary += f"Steps: {len(task.steps)}\n"
    
    successful_steps = sum(1 for step in task.steps if step.success)
    summary += f"Successful steps: {successful_steps}/{len(task.steps)}\n"
    
    return summary


def format_task_display_name(task: Task) -> str:
    """Format a display name for the task."""
    if not task:
        return "Unknown Task"
    
    task_id = get_unique_task_id(task)
    parts = task_id.split("_")
    if len(parts) >= 2:
        return f"{parts[0]} - {parts[1]}"
    
    return task_id


def setup_streamlit_ui():
    """Set up the Streamlit UI."""
    st.set_page_config(
        page_title="Claude Computer Use Evaluation",
        page_icon="🧠",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS
    st.markdown("""
    <style>
        .main-header {
            font-size: 2.5rem;
            font-weight: bold;
            margin-bottom: 1rem;
        }
        .sub-header {
            font-size: 1.5rem;
            font-weight: bold;
            margin-top: 1rem;
            margin-bottom: 0.5rem;
        }
        .task-header {
            font-size: 1.2rem;
            font-weight: bold;
            margin-top: 0.5rem;
            margin-bottom: 0.25rem;
        }
        .step-container {
            padding: 0.5rem;
            border-radius: 0.25rem;
            margin-bottom: 0.5rem;
        }
        .step-success {
            background-color: rgba(0, 255, 0, 0.1);
            border-left: 3px solid green;
        }
        .step-failure {
            background-color: rgba(255, 0, 0, 0.1);
            border-left: 3px solid red;
        }
        .info-text {
            font-size: 0.9rem;
            color: #666;
        }
        .highlight {
            color: #FF5733;
            font-weight: bold;
        }
    </style>
    """, unsafe_allow_html=True)


def display_task_overview(task: Task, screenshots_dir: str):
    """Display an overview of the task."""
    if not task:
        st.warning("No task selected")
        return
    
    task_id = get_unique_task_id(task)
    
    # Task header
    st.markdown(f'<div class="task-header">{format_task_display_name(task)}</div>', unsafe_allow_html=True)
    
    # Task details
    with st.expander("Task Details", expanded=True):
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.code(format_task_summary(task))
            st.markdown(f"**Instruction:**\n{task.instruction}")
        
        with col2:
            # Display screenshots if available
            screenshots = get_screenshots_for_task(task, screenshots_dir)
            if screenshots:
                for screenshot_path in screenshots[:3]:  # Limit to first 3 screenshots
                    try:
                        st.image(screenshot_path, caption=os.path.basename(screenshot_path), use_column_width=True)
                    except Exception as e:
                        st.error(f"Error loading screenshot: {e}")
            else:
                st.info("No screenshots available for this task")


def display_step_details(task: Task, selected_step_idx: Optional[int] = None):
    """Display details for steps in the task."""
    if not task or not task.steps:
        st.warning("No steps to display")
        return
    
    # Step navigation
    step_options = [f"Step {i+1}: {step.tool_name}" for i, step in enumerate(task.steps)]
    step_options.insert(0, "All Steps")
    
    selected_option = st.selectbox("Select Step", step_options, key="step_selector")
    
    if selected_option == "All Steps":
        # Display all steps
        for i, step in enumerate(task.steps):
            step_class = "step-success" if step.success else "step-failure"
            st.markdown(f'<div class="step-container {step_class}">', unsafe_allow_html=True)
            
            st.markdown(f"**Step {i+1}: {step.tool_name}**")
            st.markdown(f"**Success:** {'✅' if step.success else '❌'}")
            
            with st.expander(f"Step {i+1} Details", expanded=False):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**Input:**")
                    st.code(json.dumps(step.tool_input, indent=2))
                
                with col2:
                    st.markdown("**Output:**")
                    st.code(json.dumps(step.tool_output, indent=2))
            
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        # Display selected step
        step_idx = step_options.index(selected_option) - 1
        step = task.steps[step_idx]
        
        step_class = "step-success" if step.success else "step-failure"
        st.markdown(f'<div class="step-container {step_class}">', unsafe_allow_html=True)
        
        st.markdown(f"**Step {step_idx+1}: {step.tool_name}**")
        st.markdown(f"**Success:** {'✅' if step.success else '❌'}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Input:**")
            st.code(json.dumps(step.tool_input, indent=2))
        
        with col2:
            st.markdown("**Output:**")
            st.code(json.dumps(step.tool_output, indent=2))
        
        st.markdown('</div>', unsafe_allow_html=True)


def evaluate_task(task: Task, prev_evaluation: Optional[Dict] = None):
    """Interface for evaluating a task."""
    if not task:
        st.warning("No task selected for evaluation")
        return None
    
    task_id = get_unique_task_id(task)
    
    st.markdown('<div class="sub-header">Task Evaluation</div>', unsafe_allow_html=True)
    
    with st.form(key=f"evaluation_form_{task_id}"):
        # Step evaluation
        st.markdown("### Step Evaluation")
        st.markdown("Mark each step as successful or failed, and provide efficiency ratings:")
        
        step_evaluations = []
        step_success_list = []
        step_efficiency_list = []
        
        for i, step in enumerate(task.steps):
            st.markdown(f"**Step {i+1}: {step.tool_name}**")
            
            # Default values from previous evaluation if available
            default_success = True
            default_efficiency = 0.5
            default_notes = ""
            
            if prev_evaluation and "steps" in prev_evaluation:
                if i < len(prev_evaluation["steps"]):
                    prev_step = prev_evaluation["steps"][i]
                    default_success = prev_step.get("success", True)
                    default_efficiency = prev_step.get("efficiency", 0.5)
                    default_notes = prev_step.get("notes", "")
            
            col1, col2 = st.columns([1, 2])
            
            with col1:
                step_success = st.checkbox(
                    "Success", 
                    value=default_success, 
                    key=f"step_{task_id}_{i}_success"
                )
                step_success_list.append(step_success)
            
            with col2:
                step_efficiency = st.slider(
                    "Efficiency (0-1)", 
                    min_value=0.0, 
                    max_value=1.0, 
                    value=default_efficiency,
                    step=0.1,
                    key=f"step_{task_id}_{i}_efficiency"
                )
                step_efficiency_list.append(step_efficiency)
            
            step_notes = st.text_area(
                "Notes for this step", 
                value=default_notes,
                key=f"step_{task_id}_{i}_notes"
            )
            
            step_evaluations.append({
                "success": step_success,
                "efficiency": step_efficiency,
                "notes": step_notes
            })
            
            st.markdown("---")
        
        # Overall task evaluation
        st.markdown("### Overall Evaluation")
        
        # Calculate metrics
        tsr = 1.0 if all(step_success_list) else 0.0
        ssr = sum(step_success_list) / len(step_success_list) if step_success_list else 0.0
        ae = sum(step_efficiency_list) / len(step_efficiency_list) if step_efficiency_list else 0.0
        
        # Default values from previous evaluation
        default_notes = ""
        if prev_evaluation:
            default_notes = prev_evaluation.get("notes", "")
        
        task_notes = st.text_area(
            "Overall Notes", 
            value=default_notes,
            key=f"task_{task_id}_notes"
        )
        
        # Summary metrics
        st.markdown("### Metrics Summary")
        col1, col2, col3 = st.columns(3)
        col1.metric("Task Success Rate", f"{tsr:.2f}")
        col2.metric("Step Success Rate", f"{ssr:.2f}")
        col3.metric("Average Efficiency", f"{ae:.2f}")
        
        submitted = st.form_submit_button("Save Evaluation")
    
    if submitted:
        # Create metrics object
        metrics = TaskMetrics(
            task_id=task_id,
            task_success_rate=tsr,
            step_success_rate=ssr,
            average_efficiency=ae,
            total_steps=len(task.steps),
            successful_steps=sum(step_success_list),
            failed_steps=len(task.steps) - sum(step_success_list),
            notes=task_notes
        )
        
        # Update step data
        for i, step in enumerate(task.steps):
            step.success = step_evaluations[i]["success"]
            step.efficiency = step_evaluations[i]["efficiency"]
        
        st.success(f"Evaluation saved for task {task_id}")
        return metrics
    
    return None


def main():
    """Main function."""
    setup_streamlit_ui()
    
    st.markdown('<div class="main-header">Claude Computer Use Evaluation</div>', unsafe_allow_html=True)
    
    # Initialize session state
    if "current_task" not in st.session_state:
        st.session_state.current_task = None
    if "task_list" not in st.session_state:
        st.session_state.task_list = []
    if "evaluator" not in st.session_state:
        st.session_state.evaluator = ""
    if "log_dir" not in st.session_state:
        st.session_state.log_dir = "logs"
    if "screenshots_dir" not in st.session_state:
        st.session_state.screenshots_dir = "screenshots"
    if "evaluations_dir" not in st.session_state:
        st.session_state.evaluations_dir = "evaluations"
    if "current_metrics" not in st.session_state:
        st.session_state.current_metrics = []
    if "evaluation_storage" not in st.session_state:
        st.session_state.evaluation_storage = EvaluationStorage(st.session_state.evaluations_dir)
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("Configuration")
        
        # Evaluator name
        st.session_state.evaluator = st.text_input("Evaluator Name", value=st.session_state.evaluator)
        
        # Directory inputs
        col1, col2 = st.columns(2)
        with col1:
            st.session_state.log_dir = st.text_input("Logs Directory", value=st.session_state.log_dir)
        with col2:
            st.session_state.screenshots_dir = st.text_input("Screenshots Directory", value=st.session_state.screenshots_dir)
        
        st.session_state.evaluations_dir = st.text_input("Evaluations Directory", value=st.session_state.evaluations_dir)
        
        # Update evaluation storage if directory changed
        if st.session_state.evaluation_storage.eval_dir != st.session_state.evaluations_dir:
            st.session_state.evaluation_storage = EvaluationStorage(st.session_state.evaluations_dir)
        
        # Load logs button
        if st.button("Load Logs"):
            if os.path.exists(st.session_state.log_dir):
                log_files = [f for f in os.listdir(st.session_state.log_dir) if f.endswith('.json')]
                
                if not log_files:
                    st.error(f"No JSON log files found in {st.session_state.log_dir}")
                else:
                    tasks = []
                    for log_file in log_files:
                        log_path = os.path.join(st.session_state.log_dir, log_file)
                        task = LogParser.parse_json_log(log_path)
                        if task:
                            tasks.append(task)
                    
                    if tasks:
                        st.session_state.task_list = tasks
                        st.success(f"Loaded {len(tasks)} tasks from {len(log_files)} log files")
                    else:
                        st.error("No valid tasks found in log files")
            else:
                st.error(f"Directory not found: {st.session_state.log_dir}")
        
        # Task selection
        if st.session_state.task_list:
            st.header("Task Selection")
            
            # Create a list of task display names
            task_options = {}
            for task in st.session_state.task_list:
                task_id = get_unique_task_id(task)
                task_options[task_id] = format_task_display_name(task)
            
            # Group tasks by category
            categories = {}
            for task in st.session_state.task_list:
                category = task.category
                if category not in categories:
                    categories[category] = []
                categories[category].append(task)
            
            # Create a selectbox for each category
            selected_category = st.selectbox("Category", list(categories.keys()), key="category_selector")
            
            if selected_category:
                category_tasks = categories[selected_category]
                category_task_options = {get_unique_task_id(task): format_task_display_name(task) for task in category_tasks}
                
                selected_task_id = st.selectbox(
                    "Task", 
                    list(category_task_options.keys()),
                    format_func=lambda x: category_task_options[x],
                    key="task_selector"
                )
                
                if selected_task_id:
                    # Find the selected task
                    st.session_state.current_task = next(
                        (task for task in st.session_state.task_list if get_unique_task_id(task) == selected_task_id),
                        None
                    )
    
    # Main content
    if not st.session_state.task_list:
        st.info("No tasks loaded. Use the sidebar to load logs.")
        return
    
    # Display task details
    if st.session_state.current_task:
        # Create tabs
        tab1, tab2, tab3 = st.tabs(["Task Overview", "Step Details", "Evaluation"])
        
        with tab1:
            display_task_overview(st.session_state.current_task, st.session_state.screenshots_dir)
        
        with tab2:
            display_step_details(st.session_state.current_task)
        
        with tab3:
            # Check for previous evaluations
            prev_evaluation = None
            task_id = get_unique_task_id(st.session_state.current_task)
            task_results = st.session_state.evaluation_storage.get_task_results(task_id)
            
            if task_results:
                st.info(f"Found {len(task_results)} previous evaluations for this task")
                
                # Show the most recent evaluation
                prev_evaluation = task_results[-1]["metrics"]
            
            # Evaluate the task
            metrics = evaluate_task(st.session_state.current_task, prev_evaluation)
            
            if metrics:
                # Add to metrics list
                if metrics not in st.session_state.current_metrics:
                    st.session_state.current_metrics.append(metrics)
                
                # Create and save evaluation result
                if st.session_state.evaluator:
                    result = EvaluationResult(
                        metrics=[metrics],
                        timestamp=datetime.now().strftime("%Y-%m-%d_%H:%M:%S"),
                        evaluator=st.session_state.evaluator,
                        notes=""
                    )
                    
                    filepath = st.session_state.evaluation_storage.save_evaluation(result)
                    st.success(f"Evaluation saved to {filepath}")
                else:
                    st.warning("Please enter an evaluator name to save the evaluation")
    else:
        st.info("Select a task from the sidebar to begin evaluation.")
    
    # Show metrics dashboard if we have evaluations
    if st.session_state.current_metrics:
        st.markdown('<div class="sub-header">Metrics Dashboard</div>', unsafe_allow_html=True)
        
        # Aggregate metrics
        agg_metrics = aggregate_metrics(st.session_state.current_metrics)
        
        # Display aggregate metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Average TSR", 
                f"{agg_metrics['avg_task_success_rate']*100:.1f}%",
                delta=None
            )
        
        with col2:
            st.metric(
                "Average SSR", 
                f"{agg_metrics['avg_step_success_rate']*100:.1f}%",
                delta=None
            )
        
        with col3:
            st.metric(
                "Average Efficiency", 
                f"{agg_metrics['avg_average_efficiency']:.2f}",
                delta=None
            )
        
        with col4:
            st.metric(
                "Successful Tasks", 
                f"{agg_metrics['successful_tasks']}/{agg_metrics['total_tasks']}",
                delta=None
            )
        
        # Detailed metrics table
        metrics_data = []
        for metric in st.session_state.current_metrics:
            metrics_data.append({
                "Task ID": metric.task_id,
                "TSR": f"{metric.task_success_rate*100:.1f}%",
                "SSR": f"{metric.step_success_rate*100:.1f}%",
                "Efficiency": f"{metric.average_efficiency:.2f}",
                "Total Steps": metric.total_steps,
                "Success Steps": metric.successful_steps,
                "Failed Steps": metric.failed_steps,
                "Notes": metric.notes or ""
            })
        
        df = pd.DataFrame(metrics_data)
        st.dataframe(df, use_container_width=True)
        
        # Export options
        st.markdown("### Export Options")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Export Metrics to JSON"):
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                export_path = os.path.join(st.session_state.evaluations_dir, f"metrics_export_{timestamp}.json")
                
                with open(export_path, "w") as f:
                    json.dump({
                        "metrics": [m.to_dict() for m in st.session_state.current_metrics],
                        "aggregate": agg_metrics,
                        "timestamp": timestamp,
                        "evaluator": st.session_state.evaluator
                    }, f, indent=2)
                
                st.success(f"Metrics exported to {export_path}")
        
        with col2:
            if st.button("Export Metrics to CSV"):
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                export_path = os.path.join(st.session_state.evaluations_dir, f"metrics_export_{timestamp}.csv")
                
                df.to_csv(export_path, index=False)
                st.success(f"Metrics exported to {export_path}")


if __name__ == "__main__":
    main()
