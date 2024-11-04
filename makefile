# Makefile to use Conda environment

# Variables
CONDA_ENV = "./conda-env"  # Replace with your environment name
PYTHON = conda run -p $(CONDA_ENV) python

#Target

run:
	$(PYTHON) script.py
	
activate:
	conda activate $(CONDA_ENV)
