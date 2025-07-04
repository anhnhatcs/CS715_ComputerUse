
# Seminar CS715 Computer Use Evaluation Project

This project provides tools for analyzing and evaluating Claude Computer Use logs. The project is organized into two main components:

1. **Environment Setup** (parent folder): Contains environment setup, documentation, and project-level configuration based on the [trycua/cua](https://github.com/trycua/cua) framework
2. **Main Code** (`cs715_coding/`): Contains the custom code for log analysis and evaluation


## Demo by Anh-Nhat Nguyen


https://github.com/user-attachments/assets/14658c82-e3db-4686-8b4b-0b7dbec3e316


## Project Structure

```
CS715_ComputerUse/                     # Parent folder (Environment Setup)
├── cs715_coding/                      # Main code folder
│   ├── computeruse/                   # Main package
│   │   ├── analysis/                  # Analysis utilities
│   │   ├── ui/                        # UI components
│   │   └── utils/                     # Utility functions
│   ├── data/                          # Data folder
│   │   ├── logs/                      # Log files
│   │   ├── evaluations/               # Saved evaluations
│   │   └── screenshots/               # Screenshots
│   ├── cli/                           # Command line tools
│   └── experiments/                   # Experimental code
├── docs/                              # Documentation
├── examples/                          # Example scripts
├── libs/                              # External libraries
├── notebooks/                         # Jupyter notebooks
├── scripts/                           # Utility scripts
└── tests/                             # Test cases
```

## Installation

### Part 1: Computer Use System Setup

To set up the Computer Use system, please follow the instructions in the [trycua/cua repository](https://github.com/trycua/cua). This includes:

- Installing the Lume CLI for VM management
- Pulling macOS or Linux VM images
- Installing Python SDKs for Computer and Agent
- Setting up the MCP server if needed

The trycua/cua repository provides several options for installation, including Docker containers, Dev Containers, and direct PyPI installation.

### Part 2: CS715 Evaluation Tools

1. Clone this repository:
```bash
git clone https://github.com/your-username/CS715_ComputerUse.git
cd CS715_ComputerUse
```

2. Install the main package:
```bash
cd cs715_coding
pip install -e .
```

## Usage

### Part 1: Computer Use System

For using the Computer Use system, refer to the usage guides in the [trycua/cua repository](https://github.com/trycua/cua#-usage-guide).

### Part 2: CS715 Evaluation Tools

The CS715 evaluation tools can be used in several ways:

1. **Streamlit UI**: Run the Streamlit UI to visualize and analyze logs:
```bash
python -m cs715_coding.computeruse.main ui
```

2. **CLI Evaluation**: Evaluate a log file from the command line:
```bash
python -m cs715_coding.cli.eval_cli evaluate path/to/logfile.json
```

3. **Experiments**: Run experiments with different models and configurations:
```bash
python -m cs715_coding.experiments.experiments
```

See the README.md in the `cs715_coding/` folder for more detailed usage instructions.

## Documentation

- [Developer Guide](docs/Developer-Guide.md)
- [FAQ](docs/FAQ.md)
- [Telemetry](docs/Telemetry.md)
- [trycua/cua Documentation](https://github.com/trycua/cua#-usage-guide)

## Author

Anh-Nhat Nguyen: Mannheim Master in Data Science 

## Acknowledgements

- [trycua/cua](https://github.com/trycua/cua) for the Computer Use Agent framework
- The CS715 seminar for providing the research context
