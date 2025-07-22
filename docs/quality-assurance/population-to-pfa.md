# Matching ONS local authority populations to Police Force Areas: data quality assurance
## Introduction
During the data processing pipeline, the ONS population data is matched with an ONS lookup file for Local Authority Districts and Police Force Areas in England and Wales. This merged dataset is then used to calculate the total number of adult women in each Police Force Area in each year.

Following the merge it became apparent that there were some discrepancies in the population of the Avon and Somerset PFA, and that a number of LAs present in the previous analysis appeared to be missing from the newly processed dataset. In addition, a new area of Somerset was included in the dataset which didn't appear to follow the alphanumeric pattern of the other LA codes.

To understand why there might be missing values, it was necessary to consult the ONS' [*A Beginner's Guide to UK Geography*](https://geoportal.statistics.gov.uk/datasets/d1f39e20edb940d58307a54d6e1045cd/about). 


## So what did it say?
The guide explains that in 2023 there was local government reorganisation affecting the Somerset area.

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


## Examining the discrepancies
An examination of the data in `1.8-ah-pfa-population-qa.ipynb` shows that the newly created UAs included in the latest dataset have had a very modest impact on the overall population of the PFAs, and that the differences in population values are very small.

The chart below shows the percentage difference in population by PFA between the new and old datasets. The differences are all within a 2% margin of error, which is acceptable for this type of data.
<!-- Percentage Differences in Population by PFA (New vs Old Data) -->
<div style="text-align: center;">
    <hr class="heavy">
    <iframe width="100%" height="300" frameborder="0" scrolling="no" src="../../assets/pfa_population_comparison.html">
    </iframe>
    <hr class="light">
</div>

### Checking all PFAs
Checks were completed for all PFAs to identify which Police Force Areas had the largest differences in population between the new and old datasets. The following PFAs were identified as having the largest differences:

* Cambridgeshire
* Bedfordshire
* Thames Valley
* Metropolitan Police

The ONS' [Reconciliation of mid-year population estimates with Census 2021 at local authority level](https://www.ons.gov.uk/peoplepopulationandcommunity/populationandmigration/populationestimates/articles/reconciliationofmidyearpopulationestimateswithcensus2021atlocalauthoritylevel/2023-03-02#local-authorities-with-the-largest-differences) highlights those local authorities which saw the largest differences between the 2021 rolled-forward and 2021 Census-based mid-year estimates.

The ONS' analysis was checked against the data in `1.8-ah-pfa-population-qa.ipynb` to see which local authorities were represented in those PFAs with the largest differences. The following local authorities were identified:

| Police Force Area | Local Authority | ONS % difference |
| ----------------- | --------------- | ---------------- |
| Cambridgeshire    | Cambridge       | \-15.66          |
| Cambridgeshire    | Peterborough    | \-6.53           |
| Bedfordshire      | Luton           | \-5.69           |
| Thames Valley     | Reading         | \-9.57           |
| Thames Valley     | Slough          | \-6.53           |
| Thames Valley     | Oxford          | \-5.56           |

In addition, the ONS analysis highlights that LAs in London saw larger differences.


## So what does this mean?
The analysis shows that the changes to the ONS population data have had a minimal impact on the overall population of the PFAs, and that the differences in population values are very small. The newly created UAs have had a very modest impact on the overall population of the PFAs, and the differences in population values remain within an acceptable margin of error.