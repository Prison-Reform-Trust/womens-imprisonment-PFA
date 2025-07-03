# ONS Estimates of the population for England, and Wales: data quality assurance

## Introduction

As part of the quality assurance of the data processing stages for the ONS mid-year population estimates, comparison with our earlier dataset has been undertaken. This has revealed that 94.9% of local authority records had a difference in their recorded population figure of ±5% between the previously published dataset (rolled-forward estimates) and the most recent official population estimates for England and Wales, based on Census 2021 data.

Further exploration of the reasons behind the differences have been undertaken through consultation with the accompanying dataset notes and the [ONS' own reconciliation](https://www.ons.gov.uk/peoplepopulationandcommunity/populationandmigration/populationestimates/articles/reconciliationofmidyearpopulationestimateswithcensus2021atlocalauthoritylevel/2023-03-02) of population estimates following the 2021 Census.

## So what did it say?

The ONS refers to two main mid-year estimates (MYE) of population.

1. **Census-based MYEs** are the official mid-2021 population estimates, these are based on the 2021 Census for England and Wales. These provide the most accurate estimate of the population and therefore the reliability of MYEs is very high immediately following a census.

2. **Rolled-forward MYEs** use the population estimate from the previous reference date as the starting point for estimating the population at the current reference date. The previous population estimate is aged on and data on births, deaths and migration are used to reflect population change during the reference period.

As part of their reconciliation the ONS compared the official 2021 Census-based MYE and the 2021 rolled-forward MYE at local authority level. They found that 89.12% of local authorities had a difference in their population of less than positive or negative 4.99% when comparing the two datasets.

At the local authority level, the rolled-forward MYE were more likely to overestimate males than females compared with the census-based mid-year estimates.

!!! abstract "Reconciliation of mid-year population estimates with Census 2021 at local authority level"
    "Differences between population estimates based on Census 2021 data and annual mid-year population estimates are expected."

Whist the ONS did not seek to attribute those differences to any specific cause, citing the complexity of determining the patterns of difference. It did highlight that those with the largest discrepancies "tend to be larger in areas of high population churn such as areas with significant student populations or large urban areas."

!!! abstract "Reconciliation of mid-year population estimates with Census 2021 at local authority level"
    Areas with the largest differences between estimates can generally be attributed to one of three groups:

    - LAs in London
    - LAs with a large student population
    - LAs with a special population (presence of military personnel, for example)

    Differences in these areas are likely to be partially attributed to high population churn. It is worth noting that similar areas do not show a unifying pattern, with LAs in London presenting large positive (Camden) and negative (Ealing) differences.


## Examining the discrepancies
As part of PRT's QA work, a similar exercise was undertaken to compare the population of adult women computed using 1. the older pre-2021 Census rolled-forward MYEs with 2. the latest available dataset. Both datasets were filtered to only include years of overlap, in this case 2011–2020.

The datasets were then merged to allow for comparison of the population values between the two datasets. Actual, absolute and percentage differences between the two were then calculated, and a computed boolean column was added to evaluate which records had an absolute difference of <=5%.

!!! info
    Of the 3,140 successfully merged records, 2,980 (94.90%) were within a ±5% variance.

Of the 314 Local Authorities represented in the merged dataframe, 42 showed at least one instance of variance over and above the 5% target (13% of all LAs in the data).

For comparison the ONS' reconciliation analysis found 36 Local Authorities with a percentage difference of larger than positive or negative 5% between the 2021 rolled-forward and 2021 Census-based mid-year estimates.

The ONS list of the 36 Local Authorities was compared against our 42, and 24 of them matched (66%).

Whilst this is an imperfect test, it does show a reasonably high level of correlation.

## Police Force Area populations
During the data processing pipeline, the ONS population data is matched with an ONS lookup file for Local Authority Districts and Police Force Areas in England and Wales. This merged dataset is then used to calculate the total number of adult women in each Police Force Area in each year.

Following the merge it became apparent that there were some discrepancies in the population of the Avon and Somerset PFA, and that a number of LAs present in the previous analysis appeared to be missing from the newly processed dataset. In addition, a new area of Somerset was included in the dataset which didn't appear to follow the alphanumeric pattern of the other LA codes.

To understand why there might be missing values, it was necessary to consult the ONS' [*A Beginner's Guide to UK Geography*](https://geoportal.statistics.gov.uk/datasets/d1f39e20edb940d58307a54d6e1045cd/about). The guide explains that in 2023 there was local government reorganisation affecting the Somerset area.

!!! abstract "A Beginner's Guide to UK Geography"
    "[In 2023] the four districts within the county of Somerset were merged to form Somerset UA [unitary authority]".

The guide also explains that **four** UAs were created:

  * Cumberland;
  * Westmorland;
  * North Yorkshire; and
  * Somerset

Two UAs were also created in 2021, which given the timing shouldn't impact on previous analysis, but will require further quality assurance checks:

  * North Northamptonshire UA
  * West Northamptonshire UA

Further checks will be conducted to examine how widespread the local authority and population discrepancies are, or whether it only affects the above new UAs.

Returning to the case of Somerset UA, the UK Geography guide explains that codes starting with E06 refer to unitary authorities and E07 refer to non-metropolitan districts, so it is logical that the four E07 district values have been dropped and a new E06 unitary authority value has appeared in this latest dataset.

``` title="A Beginner's Guide to UK Geography" hl_lines="7 9"
England (E92)
└── Regions (E12)
    ├── London
    │   ├── London Boroughs (E09)
    │   └── Electoral Wards (E05)
    ├── Counties (E10)
    │   ├── Non-Metropolitan Districts (E07)
    │   └── Electoral Wards (E05)
    ├── Unitary Authorities (E06)
    │   └── Electoral Wards (E05)
    ├── Metropolitan Counties (E11)
    │   ├── Metropolitan Districts (E08)
    │   └── Electoral Wards (E05)
    └── Parishes (E04)
```
Following consultation of the [*ONS' Geography Coding and Naming Policy for Official Statistics*](https://geoportal.statistics.gov.uk/documents/5a050dcaac8049dc9dc0aa7de0943378/about) it explains:

!!! abstract "ONS Geography Coding and Naming Policy for Official Statistics"
    "Instances must not be coded with, and/or be based on, inbuilt intelligence (for example, alphabetically or hierarchically). This is because any later change (like renaming) that may occur might upset this inbuilt intelligence."

Again, this makes it more understandable to see that there is no logical pattern to the last two numeric digits for the Somerset UA.


## So what does this mean?
Following the QA we can be confident that the level of variation is limited, and that similar differences have been observed by the ONS in its rebasing of the MYE following the 2021 Census. The next step will be to see whether this has a significant impact on previously published rates of imprisonment once Local Authority population data has been matched to Police Force Areas.

Further QA will be undertaken to investigate whether the local authority and population discrepancies are limited to the above new UAs.
