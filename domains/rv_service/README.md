**All data in this folder is invented.** The codes, descriptions, hours, rules and findings were made up for this project. Nothing is copied from, or modelled on, any real flat-rate manual, estimating product or vendor code format, and the hours are not real labour times.

# rv_service

A made-up service catalog for a recreational-vehicle repair shop.

| File | What it is |
|---|---|
| `catalog.csv` | 69 line items in 14 sections. Code format `RVS-SSNN` (section number, item number) is this project's own. |
| `rules.yaml` | 11 completeness rules ("LP work needs a leak-down test", ...). |
| `synonyms.yaml` | Trade words that mean the same thing ("propane" / "LP", "fridge" / "refrigerator"). |
| `gold.csv` | 37 technician-style findings with the expected code and expected companion lines, used by the evaluation. |
