"""
Main Streamlit application for Computer Use Evaluation.
"""

import streamlit as st
import os
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image
from datetime import datetime
from computeruse.utils.utils import get_default_log_path, get_default_eval_path, get_default_screenshot_path
from computeruse.analysis.metrics import aggregate_metrics, format_metrics_report, format_aggregate_report
import base64

# Set page config
st.set_page_config(
    page_title="Claude Computer Use Evaluation Dashboard",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom styling
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
    .metric-card {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f0f2f6;
        margin-bottom: 1rem;
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

# Initialize session state for storing metrics and results
if 'metrics' not in st.session_state:
    st.session_state.metrics = None
if 'tasks' not in st.session_state:
    st.session_state.tasks = {}
if 'selected_task' not in st.session_state:
    st.session_state.selected_task = None
if 'aggregate_metrics' not in st.session_state:
    st.session_state.aggregate_metrics = None
if 'evaluator_name' not in st.session_state:
    st.session_state.evaluator_name = ""


def load_evaluations(eval_path):
    """Load all evaluation files from the specified directory."""
    evaluations = []
    
    if not os.path.exists(eval_path):
        return evaluations
    
    for filename in os.listdir(eval_path):
        if filename.endswith('.json'):
            try:
                with open(os.path.join(eval_path, filename), 'r') as f:
                    eval_data = json.load(f)
                    evaluations.append(eval_data)
            except Exception as e:
                st.error(f"Error loading {filename}: {e}")
    
    return evaluations


def get_task_list(evaluations):
    """Extract a list of tasks from evaluations."""
    tasks = {}
    
    for eval_data in evaluations:
        for metric in eval_data.get('metrics', []):
            task_id = metric.get('task_id', '')
            if task_id:
                category = task_id.split('_')[1] if len(task_id.split('_')) > 1 else "Unknown"
                test_id = task_id.split('_')[0] if len(task_id.split('_')) > 0 else "Unknown"
                display_name = f"{test_id} - {category}"
                tasks[task_id] = {
                    'display_name': display_name,
                    'metrics': metric,
                    'timestamp': eval_data.get('timestamp', ''),
                    'evaluator': eval_data.get('evaluator', 'Unknown')
                }
    
    return tasks


def compute_aggregate_metrics(tasks):
    """Compute aggregate metrics from all tasks."""
    if not tasks:
        return None
    
    metrics_list = [task['metrics'] for task in tasks.values()]
    return aggregate_metrics(metrics_list)


def display_metrics_dashboard(tasks, agg_metrics):
    """Display metrics dashboard."""
    if not tasks or not agg_metrics:
        st.warning("No metrics available for display.")
        return
    
    # Overview metrics
    st.markdown('<div class="sub-header">Overview Metrics</div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Task Success Rate", 
            f"{agg_metrics['avg_task_success_rate']*100:.1f}%",
            delta=None
        )
    
    with col2:
        st.metric(
            "Step Success Rate", 
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
    
    # Detailed metrics
    st.markdown('<div class="sub-header">Task Details</div>', unsafe_allow_html=True)
    
    metrics_data = []
    for task_id, task_info in tasks.items():
        metrics = task_info['metrics']
        metrics_data.append({
            'Task ID': task_info['display_name'],
            'TSR': f"{metrics['task_success_rate']*100:.1f}%",
            'SSR': f"{metrics['step_success_rate']*100:.1f}%",
            'Efficiency': f"{metrics['average_efficiency']:.2f}",
            'Total Steps': metrics['total_steps'],
            'Success Steps': metrics['successful_steps'],
            'Failed Steps': metrics['failed_steps'],
            'Evaluator': task_info['evaluator'],
            'Notes': metrics.get('notes', '')
        })
    
    df = pd.DataFrame(metrics_data)
    st.dataframe(df, use_container_width=True)
    
    # Visualizations
    st.markdown('<div class="sub-header">Visualizations</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Task Success Rate by Task
        task_success = {task_info['display_name']: task_info['metrics']['task_success_rate'] 
                      for task_id, task_info in tasks.items()}
        
        fig = px.bar(
            x=list(task_success.keys()),
            y=list(task_success.values()),
            labels={'x': 'Task', 'y': 'Task Success Rate'},
            title='Task Success Rate by Task'
        )
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Step Success Rate by Task
        step_success = {task_info['display_name']: task_info['metrics']['step_success_rate'] 
                      for task_id, task_info in tasks.items()}
        
        fig = px.bar(
            x=list(step_success.keys()),
            y=list(step_success.values()),
            labels={'x': 'Task', 'y': 'Step Success Rate'},
            title='Step Success Rate by Task'
        )
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
    
    # Download metrics as CSV
    metrics_df = pd.DataFrame(metrics_data)
    csv = metrics_df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="metrics_export.csv">Download Metrics as CSV</a>'
    st.markdown(href, unsafe_allow_html=True)


def main():
    """Main function for the Streamlit app."""
    st.markdown('<div class="main-header">Claude Computer Use Evaluation Dashboard</div>', unsafe_allow_html=True)
    
    # Sidebar
    st.sidebar.title("Controls")
    
    eval_path = get_default_eval_path()
    
    # Load evaluations
    evaluations = load_evaluations(eval_path)
    
    if not evaluations:
        st.warning(f"No evaluation files found in {eval_path}. Please run evaluations first.")
        return
    
    # Extract task list and compute aggregate metrics
    st.session_state.tasks = get_task_list(evaluations)
    st.session_state.aggregate_metrics = compute_aggregate_metrics(st.session_state.tasks)
    
    # Display metrics dashboard
    display_metrics_dashboard(st.session_state.tasks, st.session_state.aggregate_metrics)
    
    # Display full report
    with st.expander("View Full Metrics Report"):
        if st.session_state.aggregate_metrics:
            st.code(format_aggregate_report(st.session_state.aggregate_metrics))


if __name__ == "__main__":
    main()
