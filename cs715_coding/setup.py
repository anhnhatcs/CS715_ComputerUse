from setuptools import setup, find_packages

setup(
    name="cs715-computeruse",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "streamlit>=1.20.0",
        "pandas>=1.5.0",
        "plotly>=5.13.0",
        "numpy>=1.23.0",
        "pillow>=9.0.0"
    ],
    author="CS715 Team",
    author_email="example@example.com",
    description="Tools for analyzing Claude Computer Use logs",
    keywords="claude, evaluation, logs",
    python_requires=">=3.8",
)
