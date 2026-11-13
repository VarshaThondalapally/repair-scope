export default {
  "property_restoration": {
    "name": "property_restoration",
    "rows": 58,
    "sections": [
      "Antimicrobial & Cleaning",
      "Assessment & Documentation",
      "Containment & Safety",
      "Contents",
      "Demolition & Removal",
      "Drying Equipment",
      "Drywall & Finish Repair",
      "Fire & Smoke",
      "Flooring",
      "Mold Remediation",
      "Roof & Exterior Temporary",
      "Water Extraction"
    ],
    "rules": [
      {
        "name": "Wet demolition needs moisture readings first",
        "reason": "Wet material is only removed after meter readings show how far the water went, and those readings justify the cut line.",
        "when": {
          "codes": [],
          "sections": [
            "demolition & removal"
          ],
          "description_any": [
            [
              "wet"
            ]
          ],
          "description_none": []
        },
        "require": {
          "codes": [
            "PRS-0102"
          ],
          "sections": [],
          "description_any": [],
          "description_none": []
        }
      },
      {
        "name": "Extraction is followed by air movers",
        "reason": "Pulling the water out is only the first step; the structure still has to be dried with air movement.",
        "when": {
          "codes": [],
          "sections": [
            "water extraction"
          ],
          "description_any": [],
          "description_none": []
        },
        "require": {
          "codes": [
            "PRS-0301"
          ],
          "sections": [],
          "description_any": [],
          "description_none": []
        }
      },
      {
        "name": "Extraction is followed by a dehumidifier",
        "reason": "Air movers put the moisture into the air and a dehumidifier has to take it out again.",
        "when": {
          "codes": [],
          "sections": [
            "water extraction"
          ],
          "description_any": [],
          "description_none": []
        },
        "require": {
          "codes": [
            "PRS-0302"
          ],
          "sections": [],
          "description_any": [],
          "description_none": []
        }
      },
      {
        "name": "Drying equipment needs daily monitoring",
        "reason": "Equipment left running is checked every day, and the readings from those visits are what show the job is drying.",
        "when": {
          "codes": [],
          "sections": [
            "drying equipment"
          ],
          "description_any": [
            [
              "set",
              "up"
            ]
          ],
          "description_none": []
        },
        "require": {
          "codes": [
            "PRS-0104"
          ],
          "sections": [],
          "description_any": [],
          "description_none": []
        }
      },
      {
        "name": "Opened wall and ceiling cavities get antimicrobial",
        "reason": "Framing that sat behind wet drywall or insulation is treated before anything is closed up again.",
        "when": {
          "codes": [],
          "sections": [],
          "description_any": [
            [
              "wet",
              "drywall"
            ],
            [
              "wet",
              "insulation"
            ],
            [
              "wet",
              "ceil",
              "drywall"
            ]
          ],
          "description_none": []
        },
        "require": {
          "codes": [
            "PRS-0501"
          ],
          "sections": [],
          "description_any": [],
          "description_none": []
        }
      },
      {
        "name": "Removal produces debris to haul away",
        "reason": "Anything torn out has to be bagged and taken off site, and that is its own line.",
        "when": {
          "codes": [],
          "sections": [
            "demolition & removal"
          ],
          "description_any": [
            [
              "remov"
            ]
          ],
          "description_none": []
        },
        "require": {
          "codes": [
            "PRS-0408"
          ],
          "sections": [],
          "description_any": [],
          "description_none": []
        }
      },
      {
        "name": "Mold work needs containment",
        "reason": "Disturbing mold without a barrier spreads spores into the clean part of the building.",
        "when": {
          "codes": [],
          "sections": [
            "mold remediation"
          ],
          "description_any": [],
          "description_none": []
        },
        "require": {
          "codes": [
            "PRS-0701"
          ],
          "sections": [],
          "description_any": [],
          "description_none": []
        }
      },
      {
        "name": "Mold work needs negative air",
        "reason": "The contained area is kept under negative pressure with filtered exhaust for as long as mold is being disturbed.",
        "when": {
          "codes": [],
          "sections": [
            "mold remediation"
          ],
          "description_any": [],
          "description_none": []
        },
        "require": {
          "codes": [
            "PRS-0702"
          ],
          "sections": [],
          "description_any": [],
          "description_none": []
        }
      },
      {
        "name": "Mold removal ends with a clearance inspection",
        "reason": "Removal is not finished until someone has inspected and cleared the area.",
        "when": {
          "codes": [],
          "sections": [
            "mold remediation"
          ],
          "description_any": [
            [
              "remov"
            ],
            [
              "wire",
              "brush"
            ]
          ],
          "description_none": []
        },
        "require": {
          "codes": [
            "PRS-0105"
          ],
          "sections": [],
          "description_any": [],
          "description_none": []
        }
      },
      {
        "name": "Sewage work needs protective equipment",
        "reason": "Contaminated water is never handled without protective equipment.",
        "when": {
          "codes": [],
          "sections": [],
          "description_any": [
            [
              "sewag"
            ]
          ],
          "description_none": []
        },
        "require": {
          "codes": [
            "PRS-0704"
          ],
          "sections": [],
          "description_any": [],
          "description_none": []
        }
      },
      {
        "name": "Sewage work needs disinfecting afterwards",
        "reason": "Surfaces touched by sewage are cleaned and disinfected once the water is out.",
        "when": {
          "codes": [],
          "sections": [],
          "description_any": [
            [
              "sewag"
            ]
          ],
          "description_none": []
        },
        "require": {
          "codes": [
            "PRS-0502"
          ],
          "sections": [],
          "description_any": [],
          "description_none": []
        }
      },
      {
        "name": "New drywall must be taped and finished",
        "reason": "Hanging board without finishing the joints is not a completed wall.",
        "when": {
          "codes": [],
          "sections": [],
          "description_any": [
            [
              "hang",
              "replacement",
              "drywall"
            ]
          ],
          "description_none": []
        },
        "require": {
          "codes": [
            "PRS-1002"
          ],
          "sections": [],
          "description_any": [],
          "description_none": []
        }
      },
      {
        "name": "Smoke stains are cleaned before they are sealed",
        "reason": "Primer over loose soot fails, so the surface is cleaned first.",
        "when": {
          "codes": [],
          "sections": [],
          "description_any": [
            [
              "odor",
              "block",
              "primer"
            ]
          ],
          "description_none": []
        },
        "require": {
          "codes": [],
          "sections": [
            "fire & smoke"
          ],
          "description_any": [
            [
              "dry",
              "spong",
              "soot"
            ],
            [
              "wet",
              "clean",
              "smok",
              "residu"
            ]
          ],
          "description_none": []
        }
      }
    ],
    "has_rules_file": true,
    "catalog_id": "8d3b206b95045095",
    "sample_data": true,
    "approval_required": true,
    "version": "sample-v2",
    "catalog": [
      {
        "code": "PRS-0101",
        "section": "Assessment & Documentation",
        "description": "Initial loss inspection and photo documentation",
        "hours": 1.0
      },
      {
        "code": "PRS-0102",
        "section": "Assessment & Documentation",
        "description": "Moisture mapping with meter readings",
        "hours": 0.8
      },
      {
        "code": "PRS-0103",
        "section": "Assessment & Documentation",
        "description": "Thermal imaging scan for hidden moisture",
        "hours": 0.6
      },
      {
        "code": "PRS-0104",
        "section": "Assessment & Documentation",
        "description": "Daily drying monitoring visit",
        "hours": 0.5
      },
      {
        "code": "PRS-0105",
        "section": "Assessment & Documentation",
        "description": "Post-remediation clearance inspection",
        "hours": 1.0
      },
      {
        "code": "PRS-0106",
        "section": "Assessment & Documentation",
        "description": "Final dry standard verification readings",
        "hours": 0.5
      },
      {
        "code": "PRS-0201",
        "section": "Water Extraction",
        "description": "Extract standing water from hard floor",
        "hours": 0.6
      },
      {
        "code": "PRS-0202",
        "section": "Water Extraction",
        "description": "Extract water from carpet and pad",
        "hours": 0.9
      },
      {
        "code": "PRS-0203",
        "section": "Water Extraction",
        "description": "Pump out flooded basement or crawlspace",
        "hours": 1.5
      },
      {
        "code": "PRS-0204",
        "section": "Water Extraction",
        "description": "Extract sewage contaminated water",
        "hours": 1.4
      },
      {
        "code": "PRS-0301",
        "section": "Drying Equipment",
        "description": "Set up air movers",
        "hours": 0.3
      },
      {
        "code": "PRS-0302",
        "section": "Drying Equipment",
        "description": "Set up dehumidifier",
        "hours": 0.4
      },
      {
        "code": "PRS-0303",
        "section": "Drying Equipment",
        "description": "Set up wall cavity injection drying",
        "hours": 1.0
      },
      {
        "code": "PRS-0304",
        "section": "Drying Equipment",
        "description": "Set up hardwood floor drying mats",
        "hours": 1.2
      },
      {
        "code": "PRS-0305",
        "section": "Drying Equipment",
        "description": "Take down and load out drying equipment",
        "hours": 0.5
      },
      {
        "code": "PRS-0401",
        "section": "Demolition & Removal",
        "description": "Remove wet drywall (flood cut)",
        "hours": 1.2
      },
      {
        "code": "PRS-0402",
        "section": "Demolition & Removal",
        "description": "Remove wet insulation",
        "hours": 0.8
      },
      {
        "code": "PRS-0403",
        "section": "Demolition & Removal",
        "description": "Remove baseboard",
        "hours": 0.4
      },
      {
        "code": "PRS-0404",
        "section": "Demolition & Removal",
        "description": "Remove wet carpet pad",
        "hours": 0.7
      },
      {
        "code": "PRS-0405",
        "section": "Demolition & Removal",
        "description": "Remove non-salvageable carpet",
        "hours": 0.9
      },
      {
        "code": "PRS-0406",
        "section": "Demolition & Removal",
        "description": "Remove damaged laminate or vinyl flooring",
        "hours": 1.1
      },
      {
        "code": "PRS-0407",
        "section": "Demolition & Removal",
        "description": "Remove wet ceiling drywall",
        "hours": 1.4
      },
      {
        "code": "PRS-0408",
        "section": "Demolition & Removal",
        "description": "Bag and haul away debris",
        "hours": 0.7
      },
      {
        "code": "PRS-0409",
        "section": "Demolition & Removal",
        "description": "Detach and reset toilet",
        "hours": 0.8
      },
      {
        "code": "PRS-0410",
        "section": "Demolition & Removal",
        "description": "Remove base cabinet toe kick",
        "hours": 0.4
      },
      {
        "code": "PRS-0501",
        "section": "Antimicrobial & Cleaning",
        "description": "Apply antimicrobial to exposed framing",
        "hours": 0.5
      },
      {
        "code": "PRS-0502",
        "section": "Antimicrobial & Cleaning",
        "description": "Clean and disinfect hard surfaces",
        "hours": 0.8
      },
      {
        "code": "PRS-0503",
        "section": "Antimicrobial & Cleaning",
        "description": "Hot water extraction cleaning of carpet",
        "hours": 1.0
      },
      {
        "code": "PRS-0601",
        "section": "Mold Remediation",
        "description": "Remove mold affected drywall",
        "hours": 1.6
      },
      {
        "code": "PRS-0602",
        "section": "Mold Remediation",
        "description": "HEPA vacuum affected surfaces",
        "hours": 0.8
      },
      {
        "code": "PRS-0603",
        "section": "Mold Remediation",
        "description": "Wire brush and sand mold from framing",
        "hours": 1.5
      },
      {
        "code": "PRS-0604",
        "section": "Mold Remediation",
        "description": "Apply encapsulant sealer to treated framing",
        "hours": 0.7
      },
      {
        "code": "PRS-0701",
        "section": "Containment & Safety",
        "description": "Build plastic containment barrier",
        "hours": 1.2
      },
      {
        "code": "PRS-0702",
        "section": "Containment & Safety",
        "description": "Set up negative air machine with HEPA filter",
        "hours": 0.5
      },
      {
        "code": "PRS-0703",
        "section": "Containment & Safety",
        "description": "Protect floors and contents with covering",
        "hours": 0.5
      },
      {
        "code": "PRS-0704",
        "section": "Containment & Safety",
        "description": "Personal protective equipment for contaminated work",
        "hours": 0.2
      },
      {
        "code": "PRS-0801",
        "section": "Fire & Smoke",
        "description": "Dry sponge soot from walls and ceiling",
        "hours": 1.5
      },
      {
        "code": "PRS-0802",
        "section": "Fire & Smoke",
        "description": "Wet clean smoke residue from hard surfaces",
        "hours": 1.3
      },
      {
        "code": "PRS-0803",
        "section": "Fire & Smoke",
        "description": "Thermal fog deodorization",
        "hours": 0.8
      },
      {
        "code": "PRS-0804",
        "section": "Fire & Smoke",
        "description": "Seal smoke stained surfaces with odor blocking primer",
        "hours": 1.4
      },
      {
        "code": "PRS-0805",
        "section": "Fire & Smoke",
        "description": "Remove charred framing member",
        "hours": 1.8
      },
      {
        "code": "PRS-0806",
        "section": "Fire & Smoke",
        "description": "Clean ductwork of smoke residue",
        "hours": 2.5
      },
      {
        "code": "PRS-0901",
        "section": "Contents",
        "description": "Pack out and inventory contents",
        "hours": 2.0
      },
      {
        "code": "PRS-0902",
        "section": "Contents",
        "description": "Move furniture and block up on risers",
        "hours": 0.6
      },
      {
        "code": "PRS-0903",
        "section": "Contents",
        "description": "Clean and deodorize salvageable contents",
        "hours": 1.5
      },
      {
        "code": "PRS-1001",
        "section": "Drywall & Finish Repair",
        "description": "Hang replacement drywall",
        "hours": 1.5
      },
      {
        "code": "PRS-1002",
        "section": "Drywall & Finish Repair",
        "description": "Tape and finish drywall joints",
        "hours": 1.8
      },
      {
        "code": "PRS-1003",
        "section": "Drywall & Finish Repair",
        "description": "Prime and paint repaired wall",
        "hours": 1.5
      },
      {
        "code": "PRS-1004",
        "section": "Drywall & Finish Repair",
        "description": "Install replacement insulation",
        "hours": 0.7
      },
      {
        "code": "PRS-1005",
        "section": "Drywall & Finish Repair",
        "description": "Install replacement baseboard",
        "hours": 0.6
      },
      {
        "code": "PRS-1006",
        "section": "Drywall & Finish Repair",
        "description": "Retexture ceiling to match",
        "hours": 1.4
      },
      {
        "code": "PRS-1101",
        "section": "Flooring",
        "description": "Install replacement carpet pad",
        "hours": 0.8
      },
      {
        "code": "PRS-1102",
        "section": "Flooring",
        "description": "Reinstall and stretch carpet",
        "hours": 1.0
      },
      {
        "code": "PRS-1103",
        "section": "Flooring",
        "description": "Install replacement laminate flooring",
        "hours": 2.2
      },
      {
        "code": "PRS-1104",
        "section": "Flooring",
        "description": "Sand and refinish hardwood floor",
        "hours": 4.0
      },
      {
        "code": "PRS-1201",
        "section": "Roof & Exterior Temporary",
        "description": "Install emergency roof tarp",
        "hours": 1.5
      },
      {
        "code": "PRS-1202",
        "section": "Roof & Exterior Temporary",
        "description": "Board up broken window or door opening",
        "hours": 1.0
      },
      {
        "code": "PRS-1203",
        "section": "Roof & Exterior Temporary",
        "description": "Remove fallen tree limb from structure",
        "hours": 2.0
      }
    ],
    "synonyms": [
      [
        "drywall",
        "sheetrock",
        "gypsum board",
        "wallboard"
      ],
      [
        "baseboard",
        "base trim",
        "base molding"
      ],
      [
        "wet",
        "saturated",
        "soaked",
        "damp",
        "waterlogged"
      ],
      [
        "extract",
        "water removal",
        "suck up"
      ],
      [
        "standing water",
        "pooled water",
        "puddle"
      ],
      [
        "sewage",
        "black water",
        "category 3",
        "cat 3",
        "sewer backup"
      ],
      [
        "air mover",
        "fan",
        "blower"
      ],
      [
        "dehumidifier",
        "dehu"
      ],
      [
        "mold",
        "mould",
        "mildew",
        "microbial growth"
      ],
      [
        "soot",
        "smoke residue",
        "smoke film"
      ],
      [
        "odor",
        "smell",
        "deodorization",
        "deodorize"
      ],
      [
        "pad",
        "underlay",
        "padding",
        "cushion"
      ],
      [
        "laminate",
        "floating floor",
        "vinyl plank"
      ],
      [
        "hardwood",
        "wood floor",
        "oak"
      ],
      [
        "insulation",
        "batt",
        "fiberglass"
      ],
      [
        "tarp",
        "temporary cover"
      ],
      [
        "board up",
        "secure opening"
      ],
      [
        "containment",
        "poly barrier",
        "plastic sheeting"
      ],
      [
        "contents",
        "belongings",
        "personal property"
      ],
      [
        "debris",
        "trash",
        "rubble"
      ],
      [
        "charred",
        "burnt",
        "burned",
        "scorched"
      ],
      [
        "framing",
        "stud",
        "joist",
        "rafter"
      ],
      [
        "basement",
        "cellar"
      ],
      [
        "crawlspace",
        "crawl space"
      ],
      [
        "meter readings",
        "moisture readings"
      ],
      [
        "antimicrobial",
        "biocide"
      ],
      [
        "disinfect",
        "sanitize"
      ],
      [
        "retexture",
        "texture",
        "popcorn",
        "knockdown"
      ],
      [
        "limb",
        "branch"
      ],
      [
        "toe kick",
        "kick plate"
      ],
      [
        "ductwork",
        "duct",
        "register"
      ],
      [
        "remove",
        "tear out",
        "rip out",
        "demo",
        "cut out"
      ],
      [
        "install",
        "put back"
      ],
      [
        "toilet",
        "commode"
      ],
      [
        "thermal imaging",
        "infrared",
        "thermal camera"
      ]
    ]
  },
  "rv_service": {
    "name": "rv_service",
    "rows": 69,
    "sections": [
      "Air Conditioning",
      "Awning",
      "Chassis & Running Gear",
      "Diagnosis & Inspection",
      "Electrical",
      "Fresh Water & Plumbing",
      "Furnace & Heating",
      "Interior & Body",
      "LP Gas System",
      "Refrigerator",
      "Roof & Sealants",
      "Slide-Out",
      "Waste System",
      "Water Heater"
    ],
    "rules": [
      {
        "name": "LP work needs a leak-down test",
        "reason": "Whenever an LP line or fitting has been opened, the system is leak tested before the unit goes back to the customer.",
        "when": {
          "codes": [],
          "sections": [
            "lp gas system"
          ],
          "description_any": [
            [
              "replac"
            ]
          ],
          "description_none": [
            [
              "alarm"
            ]
          ]
        },
        "require": {
          "codes": [
            "RVS-0201"
          ],
          "sections": [],
          "description_any": [],
          "description_none": []
        }
      },
      {
        "name": "Gas-side appliance parts need a leak-down test",
        "reason": "Burners and gas valves sit on the LP side of an appliance, so replacing or cleaning them opens the gas path.",
        "when": {
          "codes": [],
          "sections": [],
          "description_any": [
            [
              "gas",
              "valv"
            ],
            [
              "burner"
            ]
          ],
          "description_none": []
        },
        "require": {
          "codes": [
            "RVS-0201"
          ],
          "sections": [],
          "description_any": [],
          "description_none": []
        }
      },
      {
        "name": "Appliance electronics need a diagnosis line",
        "reason": "An igniter, board or sail switch is only replaced after the fault has been traced to it, and that tracing time is billed as its own line.",
        "when": {
          "codes": [],
          "sections": [
            "water heater",
            "furnace & heating",
            "refrigerator"
          ],
          "description_any": [
            [
              "control",
              "board"
            ],
            [
              "igniter"
            ],
            [
              "sail",
              "switch"
            ]
          ],
          "description_none": []
        },
        "require": {
          "codes": [
            "RVS-0101"
          ],
          "sections": [],
          "description_any": [],
          "description_none": []
        }
      },
      {
        "name": "Roof and seam sealing needs a pressurized leak test",
        "reason": "New sealant is proven with a pressurized leak test, otherwise the same leak comes back as a second visit.",
        "when": {
          "codes": [],
          "sections": [
            "roof & sealants"
          ],
          "description_any": [
            [
              "reseal"
            ],
            [
              "patch"
            ]
          ],
          "description_none": []
        },
        "require": {
          "codes": [
            "RVS-0906"
          ],
          "sections": [],
          "description_any": [],
          "description_none": []
        }
      },
      {
        "name": "Water damage repair needs the leak source found",
        "reason": "Replacing wet material without locating where the water got in repairs the symptom and not the cause.",
        "when": {
          "codes": [],
          "sections": [],
          "description_any": [
            [
              "water",
              "damag"
            ],
            [
              "soft",
              "subfloor"
            ],
            [
              "delaminat"
            ]
          ],
          "description_none": []
        },
        "require": {
          "codes": [
            "RVS-0104"
          ],
          "sections": [],
          "description_any": [],
          "description_none": []
        }
      },
      {
        "name": "Opened water lines need a pressure test",
        "reason": "Any fresh water part that was disconnected is pressure tested before the cabinets are closed up.",
        "when": {
          "codes": [],
          "sections": [
            "fresh water & plumbing"
          ],
          "description_any": [
            [
              "pump"
            ],
            [
              "fit"
            ],
            [
              "faucet"
            ],
            [
              "check",
              "valv"
            ]
          ],
          "description_none": []
        },
        "require": {
          "codes": [],
          "sections": [
            "fresh water & plumbing"
          ],
          "description_any": [
            [
              "pressur",
              "test"
            ]
          ],
          "description_none": []
        }
      },
      {
        "name": "Wheels off means lug nuts torqued and recorded",
        "reason": "Bearing and brake work takes the wheels off, and the torque value has to be written down when they go back on.",
        "when": {
          "codes": [],
          "sections": [],
          "description_any": [
            [
              "wheel",
              "bear"
            ],
            [
              "brak",
              "assembly"
            ]
          ],
          "description_none": []
        },
        "require": {
          "codes": [
            "RVS-1305"
          ],
          "sections": [],
          "description_any": [],
          "description_none": []
        }
      },
      {
        "name": "Slide-out drive parts need the travel re-synchronized",
        "reason": "A new drive motor leaves the room out of time with the other side until the travel is adjusted.",
        "when": {
          "codes": [],
          "sections": [
            "slide-out"
          ],
          "description_any": [
            [
              "driv",
              "motor"
            ]
          ],
          "description_none": []
        },
        "require": {
          "codes": [],
          "sections": [],
          "description_any": [
            [
              "synchroniz"
            ]
          ],
          "description_none": []
        }
      },
      {
        "name": "AC electrical parts need a cooling diagnosis",
        "reason": "A capacitor or fan motor is replaced only after the cooling fault has been traced to it.",
        "when": {
          "codes": [],
          "sections": [
            "air conditioning"
          ],
          "description_any": [
            [
              "capacitor"
            ],
            [
              "fan",
              "motor"
            ]
          ],
          "description_none": []
        },
        "require": {
          "codes": [
            "RVS-0106"
          ],
          "sections": [],
          "description_any": [],
          "description_none": []
        }
      },
      {
        "name": "AC electrical parts need a performance test",
        "reason": "After the part is replaced the temperature split is measured to show the unit actually cools.",
        "when": {
          "codes": [],
          "sections": [
            "air conditioning"
          ],
          "description_any": [
            [
              "capacitor"
            ],
            [
              "fan",
              "motor"
            ]
          ],
          "description_none": []
        },
        "require": {
          "codes": [
            "RVS-0505"
          ],
          "sections": [],
          "description_any": [],
          "description_none": []
        }
      },
      {
        "name": "Converter replacement needs a 12 volt diagnosis",
        "reason": "Charging faults are often wiring or battery faults, so the converter is replaced only after the 12 volt side is diagnosed.",
        "when": {
          "codes": [],
          "sections": [
            "electrical"
          ],
          "description_any": [
            [
              "converter"
            ]
          ],
          "description_none": []
        },
        "require": {
          "codes": [
            "RVS-0102"
          ],
          "sections": [],
          "description_any": [],
          "description_none": []
        }
      }
    ],
    "has_rules_file": true,
    "catalog_id": "2816b0722121a759",
    "sample_data": true,
    "approval_required": true,
    "version": "sample-v2",
    "catalog": [
      {
        "code": "RVS-0101",
        "section": "Diagnosis & Inspection",
        "description": "Diagnose LP appliance fault",
        "hours": 0.5
      },
      {
        "code": "RVS-0102",
        "section": "Diagnosis & Inspection",
        "description": "Diagnose 12 volt electrical fault",
        "hours": 0.8
      },
      {
        "code": "RVS-0103",
        "section": "Diagnosis & Inspection",
        "description": "Diagnose 120 volt shore power fault",
        "hours": 0.8
      },
      {
        "code": "RVS-0104",
        "section": "Diagnosis & Inspection",
        "description": "Locate source of water intrusion",
        "hours": 1.0
      },
      {
        "code": "RVS-0105",
        "section": "Diagnosis & Inspection",
        "description": "Diagnose slide-out operation fault",
        "hours": 0.7
      },
      {
        "code": "RVS-0106",
        "section": "Diagnosis & Inspection",
        "description": "Diagnose air conditioner cooling fault",
        "hours": 0.6
      },
      {
        "code": "RVS-0201",
        "section": "LP Gas System",
        "description": "LP system leak-down test with manometer",
        "hours": 0.4
      },
      {
        "code": "RVS-0202",
        "section": "LP Gas System",
        "description": "Replace LP regulator",
        "hours": 0.5
      },
      {
        "code": "RVS-0203",
        "section": "LP Gas System",
        "description": "Replace LP supply hose (pigtail)",
        "hours": 0.3
      },
      {
        "code": "RVS-0204",
        "section": "LP Gas System",
        "description": "Replace LP leak detector alarm",
        "hours": 0.4
      },
      {
        "code": "RVS-0205",
        "section": "LP Gas System",
        "description": "Replace range burner valve",
        "hours": 0.7
      },
      {
        "code": "RVS-0301",
        "section": "Water Heater",
        "description": "Replace water heater igniter electrode",
        "hours": 0.5
      },
      {
        "code": "RVS-0302",
        "section": "Water Heater",
        "description": "Replace water heater control board",
        "hours": 0.6
      },
      {
        "code": "RVS-0303",
        "section": "Water Heater",
        "description": "Replace water heater gas valve",
        "hours": 0.8
      },
      {
        "code": "RVS-0304",
        "section": "Water Heater",
        "description": "Replace water heater electric heating element",
        "hours": 0.7
      },
      {
        "code": "RVS-0305",
        "section": "Water Heater",
        "description": "Flush water heater tank and replace anode rod",
        "hours": 0.6
      },
      {
        "code": "RVS-0306",
        "section": "Water Heater",
        "description": "Clean water heater burner tube and orifice",
        "hours": 0.5
      },
      {
        "code": "RVS-0401",
        "section": "Furnace & Heating",
        "description": "Replace furnace igniter",
        "hours": 0.8
      },
      {
        "code": "RVS-0402",
        "section": "Furnace & Heating",
        "description": "Replace furnace sail switch",
        "hours": 0.9
      },
      {
        "code": "RVS-0403",
        "section": "Furnace & Heating",
        "description": "Replace furnace blower motor",
        "hours": 1.5
      },
      {
        "code": "RVS-0404",
        "section": "Furnace & Heating",
        "description": "Replace furnace control board",
        "hours": 0.7
      },
      {
        "code": "RVS-0405",
        "section": "Furnace & Heating",
        "description": "Replace wall thermostat",
        "hours": 0.4
      },
      {
        "code": "RVS-0501",
        "section": "Air Conditioning",
        "description": "Replace roof air conditioner start capacitor",
        "hours": 0.5
      },
      {
        "code": "RVS-0502",
        "section": "Air Conditioning",
        "description": "Replace roof air conditioner fan motor",
        "hours": 1.6
      },
      {
        "code": "RVS-0503",
        "section": "Air Conditioning",
        "description": "Clean air conditioner evaporator and condenser coils",
        "hours": 0.8
      },
      {
        "code": "RVS-0504",
        "section": "Air Conditioning",
        "description": "Replace roof air conditioner mounting gasket",
        "hours": 1.0
      },
      {
        "code": "RVS-0505",
        "section": "Air Conditioning",
        "description": "Air conditioner temperature split performance test",
        "hours": 0.3
      },
      {
        "code": "RVS-0601",
        "section": "Refrigerator",
        "description": "Replace refrigerator burner assembly",
        "hours": 0.9
      },
      {
        "code": "RVS-0602",
        "section": "Refrigerator",
        "description": "Replace refrigerator control board",
        "hours": 0.7
      },
      {
        "code": "RVS-0603",
        "section": "Refrigerator",
        "description": "Replace refrigerator door seal",
        "hours": 0.6
      },
      {
        "code": "RVS-0604",
        "section": "Refrigerator",
        "description": "Replace refrigerator cooling unit",
        "hours": 4.5
      },
      {
        "code": "RVS-0701",
        "section": "Fresh Water & Plumbing",
        "description": "Replace fresh water pump",
        "hours": 0.7
      },
      {
        "code": "RVS-0702",
        "section": "Fresh Water & Plumbing",
        "description": "Replace water line fitting",
        "hours": 0.4
      },
      {
        "code": "RVS-0703",
        "section": "Fresh Water & Plumbing",
        "description": "Replace faucet",
        "hours": 0.6
      },
      {
        "code": "RVS-0704",
        "section": "Fresh Water & Plumbing",
        "description": "Replace city water inlet check valve",
        "hours": 0.5
      },
      {
        "code": "RVS-0705",
        "section": "Fresh Water & Plumbing",
        "description": "Pressure test fresh water system",
        "hours": 0.4
      },
      {
        "code": "RVS-0706",
        "section": "Fresh Water & Plumbing",
        "description": "Replace toilet floor flange seal",
        "hours": 0.9
      },
      {
        "code": "RVS-0801",
        "section": "Waste System",
        "description": "Replace waste tank dump valve",
        "hours": 1.0
      },
      {
        "code": "RVS-0802",
        "section": "Waste System",
        "description": "Replace holding tank level sensor",
        "hours": 0.8
      },
      {
        "code": "RVS-0803",
        "section": "Waste System",
        "description": "Clear blocked waste tank drain",
        "hours": 1.2
      },
      {
        "code": "RVS-0901",
        "section": "Roof & Sealants",
        "description": "Reseal roof vent flange",
        "hours": 0.8
      },
      {
        "code": "RVS-0902",
        "section": "Roof & Sealants",
        "description": "Reseal roof front or rear seam",
        "hours": 1.5
      },
      {
        "code": "RVS-0903",
        "section": "Roof & Sealants",
        "description": "Patch roof membrane tear",
        "hours": 0.9
      },
      {
        "code": "RVS-0904",
        "section": "Roof & Sealants",
        "description": "Replace roof vent lid",
        "hours": 0.4
      },
      {
        "code": "RVS-0905",
        "section": "Roof & Sealants",
        "description": "Reseal window frame",
        "hours": 0.9
      },
      {
        "code": "RVS-0906",
        "section": "Roof & Sealants",
        "description": "Pressurized leak test of roof and body seams",
        "hours": 1.0
      },
      {
        "code": "RVS-1001",
        "section": "Slide-Out",
        "description": "Replace slide-out drive motor",
        "hours": 1.8
      },
      {
        "code": "RVS-1002",
        "section": "Slide-Out",
        "description": "Adjust and synchronize slide-out travel",
        "hours": 1.0
      },
      {
        "code": "RVS-1003",
        "section": "Slide-Out",
        "description": "Replace slide-out wiper seal",
        "hours": 1.4
      },
      {
        "code": "RVS-1101",
        "section": "Electrical",
        "description": "Replace house battery",
        "hours": 0.4
      },
      {
        "code": "RVS-1102",
        "section": "Electrical",
        "description": "Replace power converter charger",
        "hours": 1.0
      },
      {
        "code": "RVS-1103",
        "section": "Electrical",
        "description": "Replace blown fuse and inspect circuit",
        "hours": 0.3
      },
      {
        "code": "RVS-1104",
        "section": "Electrical",
        "description": "Replace GFCI outlet",
        "hours": 0.4
      },
      {
        "code": "RVS-1105",
        "section": "Electrical",
        "description": "Replace shore power inlet",
        "hours": 0.8
      },
      {
        "code": "RVS-1106",
        "section": "Electrical",
        "description": "Replace interior light fixture",
        "hours": 0.3
      },
      {
        "code": "RVS-1201",
        "section": "Awning",
        "description": "Replace awning fabric",
        "hours": 2.0
      },
      {
        "code": "RVS-1202",
        "section": "Awning",
        "description": "Replace awning arm",
        "hours": 1.2
      },
      {
        "code": "RVS-1203",
        "section": "Awning",
        "description": "Replace awning motor",
        "hours": 1.3
      },
      {
        "code": "RVS-1301",
        "section": "Chassis & Running Gear",
        "description": "Repack wheel bearings (per axle)",
        "hours": 1.5
      },
      {
        "code": "RVS-1302",
        "section": "Chassis & Running Gear",
        "description": "Replace electric brake assembly",
        "hours": 1.0
      },
      {
        "code": "RVS-1303",
        "section": "Chassis & Running Gear",
        "description": "Adjust electric brakes",
        "hours": 0.5
      },
      {
        "code": "RVS-1304",
        "section": "Chassis & Running Gear",
        "description": "Replace leaf spring shackle",
        "hours": 1.1
      },
      {
        "code": "RVS-1305",
        "section": "Chassis & Running Gear",
        "description": "Torque wheel lug nuts and record",
        "hours": 0.2
      },
      {
        "code": "RVS-1306",
        "section": "Chassis & Running Gear",
        "description": "Replace breakaway switch",
        "hours": 0.4
      },
      {
        "code": "RVS-1401",
        "section": "Interior & Body",
        "description": "Replace water damaged ceiling panel",
        "hours": 2.5
      },
      {
        "code": "RVS-1402",
        "section": "Interior & Body",
        "description": "Replace soft subfloor section",
        "hours": 3.5
      },
      {
        "code": "RVS-1403",
        "section": "Interior & Body",
        "description": "Repair delaminated sidewall section",
        "hours": 4.0
      },
      {
        "code": "RVS-1404",
        "section": "Interior & Body",
        "description": "Replace cabinet door hinge",
        "hours": 0.3
      },
      {
        "code": "RVS-1405",
        "section": "Interior & Body",
        "description": "Replace entry door latch",
        "hours": 0.5
      }
    ],
    "synonyms": [
      [
        "faucet",
        "tap"
      ],
      [
        "propane",
        "lp",
        "lpg",
        "gas"
      ],
      [
        "won't ignite",
        "no ignition",
        "won't light",
        "not lighting",
        "no spark",
        "igniter"
      ],
      [
        "ac",
        "air conditioner",
        "air conditioning"
      ],
      [
        "wh",
        "water heater"
      ],
      [
        "fridge",
        "refrigerator",
        "reefer"
      ],
      [
        "leak",
        "drip",
        "seep",
        "water coming in",
        "intrusion"
      ],
      [
        "caulk",
        "sealant",
        "reseal"
      ],
      [
        "slideout",
        "slide out",
        "slide room"
      ],
      [
        "converter",
        "charger"
      ],
      [
        "toilet",
        "commode"
      ],
      [
        "dump valve",
        "gate valve",
        "termination valve"
      ],
      [
        "membrane",
        "rubber roof",
        "tpo",
        "epdm"
      ],
      [
        "delaminated",
        "delam",
        "delamination",
        "bubble"
      ],
      [
        "soft",
        "spongy",
        "rotten",
        "rotted"
      ],
      [
        "subfloor",
        "floor decking"
      ],
      [
        "ceiling",
        "headliner"
      ],
      [
        "stain",
        "water damaged",
        "water damage",
        "water mark"
      ],
      [
        "capacitor",
        "start cap",
        "run cap"
      ],
      [
        "fan",
        "blower"
      ],
      [
        "thermostat",
        "tstat",
        "t stat"
      ],
      [
        "outlet",
        "receptacle"
      ],
      [
        "shore power",
        "shore cord",
        "30 amp",
        "50 amp"
      ],
      [
        "tear",
        "rip",
        "puncture",
        "hole"
      ],
      [
        "fabric",
        "canvas"
      ],
      [
        "sensor",
        "probe",
        "sender"
      ],
      [
        "blocked",
        "clogged",
        "plugged",
        "backed up"
      ],
      [
        "pigtail",
        "hose"
      ],
      [
        "alarm",
        "detector"
      ],
      [
        "lid",
        "cover",
        "dome"
      ],
      [
        "latch",
        "lock",
        "handle"
      ],
      [
        "fixture",
        "lamp"
      ]
    ]
  }
};
