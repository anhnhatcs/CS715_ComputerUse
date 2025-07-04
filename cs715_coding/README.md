# CS715 Computer Use Evaluation System

This package provides tools for analyzing and evaluating Claude Computer Use logs. It builds upon the Computer Use Agent (CUA) framework from [trycua/cua](https://github.com/trycua/cua) to provide custom evaluation metrics and analysis tools for the CS715 seminar.

## Project Structure

```
cs715_coding/
├── computeruse/             # Main package
│   ├── analysis/            # Analysis utilities
│   │   ├── metrics.py       # Metrics calculation
│   │   └── log_analyzer.py  # Log parsing and analysis
│   ├── ui/                  # UI components
│   │   ├── streamlit_app.py # Main Streamlit app
│   │   └── run_eval.py      # Evaluation UI
│   └── utils/               # Utility functions
│       └── utils.py         # Common utilities
├── data/                    # Data folder
│   ├── logs/                # Log files
│   ├── evaluations/         # Saved evaluations
│   └── screenshots/         # Screenshots
├── cli/                     # Command line tools
│   └── eval_cli.py          # CLI tool for batch evaluation
└── experiments/             # Experimental code
```

## Installation

```bash
# Install the package in development mode
pip install -e .
```

> **Note**: This package requires the Computer Use Agent framework to be installed. Please refer to the [trycua/cua repository](https://github.com/trycua/cua) for instructions on setting up the Computer Use environment.

## Usage

### Streamlit UI

Run the Streamlit evaluation UI:

```bash
python -m computeruse.main ui
```

### CLI

Run evaluation on a single log file:

```bash
python -m cli.eval_cli evaluate path/to/logfile.json
```

Run evaluation on all log files in a directory:

```bash
python -m cli.eval_cli evaluate-dir path/to/logs/directory
```

List all evaluations:

```bash
python -m cli.eval_cli list
```

### Experiments

Run experiments with different models:

```bash
python -m experiments.experiments
```

## Metrics

The system calculates the following metrics:

- **Task Success Rate (TSR)**: 1.0 if all steps are successful, 0.0 otherwise
- **Step Success Rate (SSR)**: Proportion of successful steps
- **Average Efficiency (AE)**: Average efficiency across all successful steps
- **Completion Time**: Total time taken to complete the task
- **Action Count**: Number of actions performed during the task
- **Error Rate**: Percentage of actions resulting in errors
- **Tool Usage Distribution**: Distribution of different tool types used

## Data Format

The evaluation tools work with log files in JSON format produced by the Computer Use Agent. See the [trycua/cua documentation](https://github.com/trycua/cua) for details on the log format.

## Contributing

See the CONTRIBUTING.md file in the parent directory for details.

## Acknowledgements

- [trycua/cua](https://github.com/trycua/cua) for the Computer Use Agent framework
- The CS715 seminar for providing the research context
