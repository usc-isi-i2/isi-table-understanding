# Table Understanding 
Python version: 3

### Setting up virtual environment
* Install conda for package management: [conda miniforge](https://github.com/conda-forge/miniforge)
* Platform specific environment files are present in `envs` directory
* Setup virtual env by running: `make setup-conda-env ENVIRONMENT=<platform name>`
* Destroy conda env by running: `make destroy-conda-env`

### Running table-understanding pipelines
* To run a pipeline: `make run PIPELINE=<pipeline name>`
* Pipelines are defined in `./pipelines` package
* Pipelines will use `./tmp` as working directory to download model/data or generate outputs
* Run `make clean` to clean `./tmp`

### Uploading code to the remote server
* Create `<destination directory>` on the remote machine
* Run `make upload USER=<username> HOST=<hostname> DIR=<destination directory>`
* Use `make setup-conda-env ENVIRONMENT=linux_x86_cuda10` for setting up virtual env


### To run using main.py
usage: main.py [-h] [--config CONFIG] [--files FILES] [--output OUTPUT]

Run table understanding on xls/xlsx/csv files

optional arguments:
  -h, --help       show this help message and exit
  
  --config CONFIG  config file to load (default=cfg/default.yaml)
  
  --files FILES    list of files to process in yaml format. Each file is in a
                   new line preceded by '- ' (default=cfg/files.yaml)
                   
  --output OUTPUT  Output directory for all output files (default=./)


### Configuration
Settings file: cfg/test.yaml

To write a colorized excel sheet with block information:
   colorize: true/false
   (Please note that colorize works *only with xlsx files* due to the limitations of the library we are using)

To write out dataframes from detected 'value' blocks:
   output_dataframe: true/false


### This project implements the table extraction pipeline
Table understanding is divided into 3 sequential steps.

Step 1: Classify all the cells in the table using a pre-trained CRF based model. [cell_classifier]

Step 2: Group all the classified cells into blocks. [block_extractor]

Step 3: Find the relationship between different blocks. [layout_detector]

### Extending the code
You can write your own extractors for the 3 steps in the corresponding folder, by inheriting from the corresponding base classes.

Base Class Files:
cell_classifier.py, block_extractor.py, layout_detector.py

Corresponding to each layer, we have implemented an example class derived from it's base class.
example_cell_classifier.py, example_block_extractor.py, example_layout_detector.py

### Requirements for PSL modules
To run the PSL modules, (e.g., if you would like to run `make run pipeline=psl` you need to
1. Download [this file](https://drive.google.com/file/d/1ndVTP3WSG8OLoDjYnePvuVZ5fxXBCyRz/view?usp=sharing) and extract the files in `data/`. (or perhaps ./tmp/)
2. Download the source code and the pre-trained models from [here](https://github.com/majidghgol/TabularCellTypeClassification), and follow the instructions to download the GLOVE model and InferSent source code. You can then write your own config files following the format of `cfg/psl_sample.yaml` (changing the paths to the pre-trained models and the source codes).
