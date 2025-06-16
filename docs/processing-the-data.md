# Processing the data

In this section we examine how to process the raw data ready for analysis. The full processing part of this pipeline is encapsulated in the `process_data.py` module.

## Criminal Justice System Statistics

!!! warning "Data revision"

    The Ministry of Justice published [revised outcomes by offence data](https://www.gov.uk/government/statistics/criminal-justice-system-statistics-quarterly-december-2022) for 2022 in January 2024. This means that there are discrepancies observed in PRT's previously published Police Force Area factsheets and the data produced in this edition. Our 2022 edition reports fewer women sentenced to a community sentence; suspended sentence; or immediate custody than in this edition. This was not an error in our data analysis, but the result of the limitations with the raw dataset explained in the Ministry of Justice's [technical appendix](https://assets.publishing.service.gov.uk/media/65a7e5feb2f3c60013e5d44b/criminal-justice-statistics-technical-appendix-june-2023.pdf#page=20). Go to [Criminal Justice System statistics: Police Force Area data quality assurance](CJS_PFA_QA.md) for more information about the revision and internal QA checks that have been made for the datasets produced in this pipeline.

### Processing steps of the data pipeline
``` mermaid
graph TD

  A[filter_sentence_type.py] --> B[group_pfa_sentence_outcome.py];
  A --> C[filter_sentence_length.py];
  A --> D[filter_custody_offences.py];
  B -->  E[\Viz data: Sentence type\];
  C -->  F[\Viz data: Custodial sentences by length\];
  C -->  G[make_custody_tables.py];
  D -->  H[\Viz data: Custodial sentences, by offence\];
  G --> I@{ shape: docs, label: "Custodial sentence tables (all and by length)" };
```

### Cleaning

We start of the processing with some initial cleaning and filtering of the dataset in `filter_sentence_type.py`.

The script reads the values stored in `outcomes_by_offence_filter` within `config.yaml`. By default this includes sentence types such as 'Immediate custody', 'Community sentence', and 'Suspended sentence', and excludes the 'Not known' police force area, it also excludes children.

Once the filtering has been applied, the script then renames and reorders the DataFrame columns; applies regex replacements and saves the processed DataFrame to a CSV file in the `intFilePath` directory as set in `config.yaml` (`data/interim` by default).

!!! success "Data produced"
    This produces our interim dataset, ready for further processing. This interim dataset forms the basis for producing the datasets necessary for all three of our visualisations which we use in our individual Police Force Area fact sheets.

### Sentence outcomes

`group_pfa_sentence_outcome.py` takes the cleaned and filtered interim dataset and aggregates it to produce summary statistics on sentencing outcomes for women in each Police Force Area (PFA).

Specifically, it groups the data by PFA and sentence outcome (such as community sentence, suspended sentence, or immediate custody), and calculates the total number of women receiving each type of sentence by year.

The resulting dataset provides a clear overview of sentencing patterns across different areas and is used as the basis for visualisations and fact sheets in the project.

!!! success "Data produced"

    The number of women in each Police Force Area who received a:
    
    - Community sentence
    - Suspended sentence
    - Sentence of immediate custody


### Sentence lengths

`filter_sentence_length.py`processes the interim dataset to analyse the lengths of immediate custodial sentences given to women in each PFA. 

It categorises sentences into groups such as less than six months; six to less than twelve months; and twelve months or more. The script then calculates the number of women in each PFA who received sentences in each category for each year over the whole time series.

The final dataset this produces is used to create the sentence length categories visualisation.

!!! success "Data produced"

    The number of women in each Police Force Area who received an immediate custodial sentence of:

    - Less than six months
    - Six to less than 12 months
    - 12 months or more


### Offences

`filter_custody_offences.py` processes the interim dataset to analyse the specific offences for which women received immediate custodial sentences in each PFA.

The script filters the data to include only immediate custody cases and then groups the results by PFA and offence type. It calculates the number of women sentenced for each offence in the latest available year.

This output provides a detailed breakdown of the types of offences leading to immediate custody and is used to produce visualisations to be included in the fact sheets in the project.

!!! success "Data produced"

    The number of women in each Police Force Area who received an immediate custodial sentence in the latest available year, by offence.


### Custodial sentence PFA tables

`make_custody_tables.py`


!!! success "Data produced"

    Three datasets showing the number of women sentenced to immediate custody in England and Wales by Police Force Area, timeseries and percentage change, for:
    
    * All custodial sentences
    * Custodial sentences of less than six months
    * Custodial sentences of less than 12 months