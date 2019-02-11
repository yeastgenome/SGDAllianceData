# SGDAllianceData

## Setup (Required)

- Install Node if you don't have it installed already 
- Make sure you're running the scripts in a virtual environment
- Makefile has all the commands you need to run the scripts to produce the data files.

- To install required packages run the this command:
    ` Make setup `

- To build file dependencies for phenotype data run the command:
    ` Make build-panther

## Disease Association file

    ` Make build-disease `

## Phenotype File

    ` Make run-phenotype `

## Expression File

    ` Make run-expression `

## Basic Gene Information File

    ` Make rub-bgi `

## File structure

- This is where the modules that get necessary data are

```

|-- src
|   |-- basic_gene_information
|   |   |-- basic_gene_information.py
|   |-- data_assets
|   |   |-- disease_association.txt
|   |   |-- panther_search_results.txt
|   |-- data_dump
|   |   |-- json data files are deposited here
|   |-- data_helpers
|   |   |-- data_helpers.py   
|   |-- expression
|   |   |-- expression.py
|   |-- phenotype
|   |   |-- phenotype.py  
|   |-- models
|   |   |-- models.py

```
