# Configuring an analysis

The analysis pipeline uses YAML configuration files to keep release-specific settings together and to select them by analysis year. This lets the same download, processing and visualisation code run with different data sources, date ranges, filters and output locations.

## Configuration files

Configuration is split between shared defaults and a configuration for each analysis:

| File | Purpose |
|---|---|
| `config/defaults.yaml` | Defines settings shared across analyses, including the standard output directory pattern and default visualisation adjustments. |
| `config/analyses/<year>.yaml` | Defines the settings for one analysis release, such as its identifier, date range, data sources, filenames, filters, cleaning rules and visualisation options. |

For example, `config/analyses/2025.yaml` holds settings for the 2025 analysis, while `config/analyses/2026.yaml` follows the same section and key structure as a template for 2026. The 2026 file currently contains dummy or placeholder values for release-specific parameters, including source URLs, and is not ready to run in its current form. Replace these with values verified for the 2026 release before using it. Treat the 2025 file as a guide to the configuration structure, not as a source for unverified 2026 values.

When the pipeline loads a year, it merges that year's file with `defaults.yaml`. Values in the year-specific file take precedence over shared defaults, while unspecified default values remain available. The `analysis.id` in the year file must match the year being loaded.

## What the settings control

The year-specific configuration describes the parameters the pipeline needs, rather than implementing the analysis itself. Depending on the setting, it controls:

- **Analysis metadata and time period:** the analysis ID, publication details, methodology version, and minimum and maximum years.
- **Input data:** source URLs and identifiers, plus expected input filenames.
- **Selection and cleaning:** configured include/exclude filters and cleaning rules for the data.
- **Files and locations:** names for intermediate and processed outputs, and directories for raw, interim, processed, figures and test data.
- **Visualisation:** output format, figure paths and any release-specific layout adjustments.

The pipeline code reads these values and performs the download, transformation and plotting steps. Configuration can change the parameters those steps use, but does not replace or modify the processing logic defined in the code.

Output paths can use the analysis ID to keep releases separate. For example, the shared defaults define paths such as `data/raw/${analysis.id}` and `data/processed/${analysis.id}`; when the 2025 configuration is loaded, `${analysis.id}` resolves to `2025`.

## Selecting an analysis

Run the pipeline entry point with the year you want to process:

```bash
python -m src.run_analysis --year 2025
```

Use `--year 2026` to select the 2026 configuration. The entry point loads the matching file from `config/analyses/`, merges it with the defaults, then passes the resulting configuration to the download, processing and visualisation stages. Only years supported by the entry point and with a matching configuration file can be selected.

When preparing a new analysis year, use the existing year configuration as a structural guide, add a corresponding `config/analyses/<year>.yaml` file with verified release-specific settings, and ensure that its `analysis.id` matches the year. The entry point's supported year choices must also include that year.
