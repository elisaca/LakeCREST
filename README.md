# LakeCREST (CCI Lakes Extractor)
This repository contains a python-based tool to extract lake subsets from the [ESA CCI Lakes](https://catalogue.ceda.ac.uk/uuid/a07deacaffb8453e93d57ee214676304) dataset based on the code from the [LakeCREST](https://climate.esa.int/es/esa-climate/esa-cci/Fellowships/esa-cci-research-fellowship-elisa-calamita/) project.

This tool script allows the user to specific the necessary variables and time-range to extract. The extraction is executed using the CCI lakes maskfile and creates a merged netCDF file per lake. The extraction can be either ran on a local copy of the Lakes CCI dataset or directly from the online source using OPeNDAP (slow!).

# Dependencies
- netCDF4
- numpy
- pandas

## How to use
## #Setup python environment
Build a conda environment from the provided YAML file in `setup/environment.yaml`:<br/>
`conda create --name lakecrest_tools --file setup/environment.yaml`

Install the necessary packages to an existing conda environment:<br/>
`conda install netCDF4 numpy pandas`

Install the necessary packages listed in the dependencies using pip:<br/>
`pip install netCDF4 numpy pandas`

### Setup local dataset
To use the script efficiently it is necessary to move a local copy of the CCI Lakes dataset into the `data/raw/` folder. For example if using the CCI Lakes v2.0.2 dataset create a copy of the dataset with the yearly folders in `data/raw/v2.0.2/`.

### Configure the extraction settings
Before running the extraction from `main.py` the user can change the the desired parameters in the file. By changing the variable `VERSION` in `scripts/constants.py` it is possible to run the extraction for older CCI Lakes versions.
