# Evaluation

Produced by this command, not edited by hand:

    python -m finding_coder.evaluate

Confident rule in force: at least 2 matched words and a score at least 1.2x the runner-up.

| Measure | property_restoration | rv_service |
|---|---|---|
| Gold findings | 38 | 37 |
| Top-1 hit (top pick is the expected code) | 23/38 (61%) | 28/37 (76%) |
| Top-3 hit (expected code in first three) | 30/38 (79%) | 35/37 (95%) |
| Routed to 'needs a person' | 14/38 (37%) | 13/37 (35%) |
| Called confident | 24/38 (63%) | 24/37 (65%) |
| Confident and correct (of those called confident) | 18/24 (75%) | 22/24 (92%) |
| Routed to a person although top pick was correct | 5/14 (36%) | 6/13 (46%) |
| Incomplete sets caught, given the correct code | 18/21 (86%) | 23/24 (96%) |
| Incomplete sets caught, starting from the matcher's top pick | 13/21 (62%) | 19/24 (79%) |
| Rule fired where gold expects no companion | 0/17 (0%) | 0/13 (0%) |

How to read it: the gold findings, the catalog, the synonyms and the rules were all written by the same author, and the data is invented. The numbers show how this matcher behaves on these files. They are not evidence of accuracy on a real shop's data.

'Incomplete sets caught' counts a gold finding only if the rules ask for every companion line the gold file lists.

## property_restoration: 5 worst misses

- "everything in the family room needs boxing up and moving to storage with a list" (expected PRS-0901). The expected row shares no word or listed synonym with the finding; top pick was PRS-0302 'Set up dehumidifier' on [up].
- "shingles blown off the back slope, rain coming into the attic, needs covering tonight" (expected PRS-1201). The expected row shares no word or listed synonym with the finding; top pick was PRS-0703 'Protect floors and contents with covering' on [covering].
- "drying gear has been running 4 days, readings at goal, pick up the fans and dehus" (expected PRS-0305). Expected row ranked #8, matching only [drying]; top pick was PRS-0301 'Set up air movers' on [drying, up, air (synonym of 'fan'), mover (synonym of 'fan')].
- "sheetrock wet up to 14 inches along the north wall, wicking" (expected PRS-0401). Expected row ranked #5, matching only [wet, drywall (synonym of 'sheetrock')]; top pick was PRS-0303 'Set up wall cavity injection drying' on [up, wall].
- "base trim swollen and pulling off the wall in the hallway" (expected PRS-0403). Expected row ranked #5, matching only [baseboard (synonym of 'base trim')]; top pick was PRS-0410 'Remove base cabinet toe kick' on [base].

Total top-1 misses in this domain: 15.

## rv_service: 5 worst misses

- "puddle under kitchen sink, pex elbow split from freezing" (expected RVS-0702). The expected row shares no word or listed synonym with the finding; top pick was RVS-0505 'Air conditioner temperature split performance test' on [split].
- "bathroom tap drips constantly, handle stripped" (expected RVS-0703). Expected row ranked #16, matching only [water (synonym of 'drip')]; top pick was RVS-0104 'Locate source of water intrusion' on [water (synonym of 'drip'), intrusion (synonym of 'drip')].
- "fridge not cooling on LP, flame yellow and sooty, burner rusted out" (expected RVS-0601). Expected row ranked #3, matching only [burner, refrigerator (synonym of 'fridge')]; top pick was RVS-0205 'Replace range burner valve' on [lp, burner, gas (synonym of 'lp')].
- "trailer brakes weak, magnets worn through on left front" (expected RVS-1302). Expected row ranked #3, matching only [brakes]; top pick was RVS-0902 'Reseal roof front or rear seam' on [front].
- "furnace fan runs but no heat, clicks 3 times then locks out, bad ignitor" (expected RVS-0401). Expected row ranked #2, matching only [furnace, heat]; top pick was RVS-0403 'Replace furnace blower motor' on [furnace, heat, blower (synonym of 'fan')].

Total top-1 misses in this domain: 9.
