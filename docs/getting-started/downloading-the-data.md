# Downloading the data

In this section we examine how to download the raw data used in this analysis ready for processing.

## Data sources
* [Ministry of Justice — Criminal Justice System statistics quarterly: December 2024](https://www.gov.uk/government/collections/criminal-justice-statistics-quarterly)
* [Office for National Statistics — Population estimates for England and Wales: mid-2023](https://www.ons.gov.uk/peoplepopulationandcommunity/populationandmigration/populationestimates/bulletins/populationestimatesforenglandandwales/mid2023)
* [Office for National Statistics — LAD to Community Safety Partnership to PFA: December 2024](https://geoportal.statistics.gov.uk/datasets/ons::lad-to-community-safety-partnership-to-pfa-december-2024-lookup-in-ew/about)

### Criminal Justice System Statistics
This dataset includes outcomes by offence csv files to enable analysis of sentencing outcomes by sex, offence type and police force area.

### Population estimates
This dataset includes national and subnational mid-year population estimates for England and Wales by administrative area, age and sex. This is used to enable the calculation of rates of imprisonment by police force area.

### LAD to Community Safety Partnership to PFA
This dataset allows users to lookup Local Authority codes and names against Police Force Area codes and names. This is used to match up the PFAs to local authorities for the calculation of rates of imprisonment.

## Step-by-step
All of the necessary scripts to download the raw data files are contained within the `src/data/raw` folder of the project.

!!! tip "tl;dr"

    Run the `download_data.py` script to automagically download the required raw datasets to `data/raw`

### File structure
```
.
└── src/
    └── data/
        └── raw/
            ├── data_filters.py  # filter functions to locate data files
            ├── download_data.py # main download script
            └── ons_api.py       # ONS API interaction
```

| Script | Function |
|---|---|
| data_filters.py | This script provides the necessary filter functions which are used on the returned JSON objects from the APIs and ensure that the correct datasets are downloaded |
| download_data.py | This is the main script and provides functions to fetch the API JSON objects using `requests` and download the raw datasets using `data_filters.py` |
| ons_api.py | This script retrieves available ONS datasets, locates population estimates and returns the latest edition's API JSON for filtering and downloading |

