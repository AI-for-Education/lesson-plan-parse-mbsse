FORMATS = [
    dict(
        sections=[
            "Lesson Title:",
            ["Theme:", "Unit:"],
            "Lesson Number:",
            ["Class/Level:", "Class:"],
            ("Time:", "\s*(\d+)"),
            "\n",
        ],
        sections_rename={"\n": "Body"},
    ),
    dict(
        sections=[
            "Lesson Title:",
            "Theme:",
            "Lesson Number:",
            ["Class/Level:", "Class:"],
            "Time:",
            "\n",
        ],
        sections_rename={"\n": "Body"},
    ),
    dict(
        sections=[
            "Lesson Title:",
            "Theme:",
            "Practice Activity:",
            ["Class/Level:", "Class:"],
            "\n",
        ],
        sections_rename={"\n": "Body", "Practice Activity:": "Lesson Number"},
    ),
    dict(
        sections=[
            "Lesson Title:",
            "Theme:",
            "Lesson Number:",
            ["Class/Level:", "Class:"],
            ("Time:", "\s*(\d\d)"),
            "\n",
        ],
        sections_rename={"\n": "Body"},
    ),
]


FORMATS_PT = [
    dict(
        sections=[
            ["Learning Outcomes", "Learning Outcome"],
            "Teaching Aids",
            "Preparation",
            "Opening",
            [
                "Introduction to the New Material",
                "Introduction to New Material",
                "Introduction of New Material",
                "Introduction to new material",
                "Introduction to New the Material",
            ],
            ["Guided Practice", "Guided practice"],
            ["Independent Practice", "Independent Practise", "Independent practice"],
            "Closing",
        ]
    ),
    dict(
        sections=[
            ["Learning Outcomes", "Learning Outcome"],
            "Preparation",
            "Opening",
            "Teaching and Learning",
            "Practice",
            "Closing",
        ]
    ),
    dict(
        sections=[
            ["Learning Outcomes", "Learning Outcome"],
            "Overview",
            "Solved Examples",
            "Practice",
        ]
    ),
    # dict(
    #     sections = [
    #         "Learning Outcomes",
    #         "Teaching Aids",
    #         "Preparation",
    #         "Opening",
    #         [
    #             "Introduction to the New Material",
    #             "Introduction to New Material",
    #             "Introduction of New Material"
    #         ],
    #     ]
    # ),
]

USEKEYS = {
    "Level": {
        "primary": "Primary",
        "jss": "Junior Secondary",
        "sss": "Senior Secondary",
    },
    "Subject": {
        "mathematics": "Mathematics",
        "english-language": "English Language",
        "language-arts": "Language Arts",
    },
    "Year": {},
    "Term": {},
    "Lesson Title": {},
    "Lesson Number": {},
}