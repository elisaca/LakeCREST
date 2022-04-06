
# LakeCREST environment setup

To setup the python environment with the necessary dependencies you can use the environment.yml provided.

## Setup using Anaconda Prompt 
Start your anaconda prompt and create the LakeCrest conda environment with the command:

`conda env create --name lakecrest --file "[...]\environment.yml"`

## Setup using Anaconda Navigator
Alternatively you can also create the LakeCrest conda environment over the Anaconda Navigator by selecting the Environments/import tab and choose the environment.yml as specification file.

## Updating an existing LakeCREST environment using Anaconda Prompt 
It is possible to update an outdated existing environment with the command:

`conda env update -f "[...]\environment.yml" --prune`

This will make make necessary updates to the packages and delete no more used packages.
