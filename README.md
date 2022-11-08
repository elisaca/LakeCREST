# CCI Lakes Extractor (LakeCREST)
This repository contains a python-based tool to extract lake subsets from the global [ESA CCI Lakes](https://catalogue.ceda.ac.uk/uuid/a07deacaffb8453e93d57ee214676304) dataset based on the code from the [LakeCREST](https://climate.esa.int/en/esa-climate/esa-cci/Fellowships/esa-cci-research-fellowship-elisa-calamita/) project.

This tool allows the user to specify the necessary lakes, variables and time-range to extract. The extraction is then executed using the CCI lakes maskfile and will create a merged netCDF file per lake. The extraction can be either ran on a local copy of the Lakes CCI dataset or directly from the online source using OPeNDAP (slow!).

## Dependencies
To run the script the following packages are needed:
- netCDF4
- numpy
- pandas

## How to use
### Setup python environment
- Build a conda environment from the provided YAML file in `setup/environment.yaml`:<br/>
`conda create --name lakecrest_tools --file setup/environment.yaml`

- (or) Install the necessary packages to an existing conda environment:<br/>
`conda install netCDF4 numpy pandas`

- (or) Install the necessary packages listed in the dependencies using pip:<br/>
`pip install netCDF4 numpy pandas`

### Setup local dataset
To use the script efficiently it is necessary to move a local copy of the CCI Lakes dataset into the `data/raw/` folder. For example, if using the CCI Lakes v2.0.2 dataset create a copy of the dataset with the yearly folders located within `data/raw/v2.0.2/`.

### Configure the extraction settings
Before running the extraction from `main.py` the user can set the desired extraction parameters in the file. By changing the variable `VERSION` in `scripts/constants.py` it is possible to run the extraction for older CCI Lakes versions. Currently the necessary lakemask and data availability table are only provided for v2.0.2 and v2.0.1. If older CCI Lakes versions are needed the necessary files have to be provided by the user in `data/auxiliary/`.
