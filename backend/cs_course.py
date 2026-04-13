# cs_course.py
# Single source of truth for your BSCS graph (nodes + edges + metadata + rules)

from __future__ import annotations
import networkx as nx


def get_rules() -> dict:
    """
    Generic rules interface that mav_advisor.py can consume for ANY major.

    locked:
      - category_locked: category that is blocked
      - requires_completed: category that must be fully completed to unlock it

    electives:
      - name: elective group name
      - slots: how many slots required
      - options: list of course IDs that can satisfy this elective (or None)
      - carryover: elective group name to carry into if this group is full (or None)
      - slot_prefix: optional helper for slot naming, like tech1..tech5
    """
    return {
        "locked": [
            {
                "category_locked": "professional",
                "requires_completed": "pre_professional",
            }
        ],
        "electives": [
            {
                "name": "security",
                "slots": 1,
                "options": ["cse4380", "cse4381", "cse4382"],
                "carryover": "tech",
                "slot_prefix": "security",
            },
            {
                "name": "tech",
                "slots": 5,
                "options": None,
                "carryover": None,
                "slot_prefix": "tech",
            },
            {
                "name": "gened_history",
                "slots": 2,
                "options": None,
                "carryover": None,
                "slot_prefix": "history",
            },
            {
                "name": "tech_options",
                "slots": 1,
                "options": ["cse4305", "cse4303","cse4360"],
                "carryover": "tech",
                "slot_prefix": "tech_options",
            },
            {
                "name": "gened_pols",
                "slots": 2,
                "options": ["pols2311", "pols2312"],
                "carryover": None,
                "slot_prefix": "pols",
            },
            {
                "name": "gened_social",
                "slots": 1,
                "options": None,
                "carryover": None,
                "slot_prefix": "social",
            },
            {
                "name": "gened_creative_arts",
                "slots": 1,
                "options": None,
                "carryover": None,
                "slot_prefix": "creative_arts",
            },
            {
                "name": "gened_culture",
                "slots": 1,
                "options": None,
                "carryover": None,
                "slot_prefix": "culture",
            },
        ],
    }

def get_certificates() -> dict:
    return {
        "cyber_security": {
            "name": "Cyber Security",
            "degree": "cse",
            "description": (
                "Educates students on identifying and mitigating cyber security risks, "
                "including cryptographic techniques, secure programming, and network security."
            ),
            "courses": [
                "cse4380",
                "cse4381",
                "cse4382",
                "cse4344",
                "cse4352",
            ],
            "keywords": [
                "security",
                "cryptography",
                "networking",
                "secure coding",
                "privacy",
            ],
        },

        "unmanned_vehicle_systems": {
            "name": "Unmanned Vehicle Systems (UVS)",
            "degree": "cse",
            "description": (
                "Educates students in the design, development, and operation of unmanned aircraft, "
                "ground, and maritime systems, emphasizing autonomy, sensors, and communications."
            ),
            "courses": [
                "cse4378",
                "cse4379",
                "cse4308",
                "cse4360",
                "cse4309",
                "cse4310",
                "cse4340",
            ],
            "keywords": [
                "robotics",
                "autonomy",
                "drones",
                "sensors",
                "navigation",
            ],
        },

        "fundamentals_of_ai": {
            "name": "Fundamentals of Artificial Intelligence",
            "degree": "cse",
            "description": (
                "Provides knowledge of AI techniques to solve real-world problems in robotics, "
                "vision, speech, health informatics, and social data."
            ),
            "courses": [
                "cse4308",
                "cse4309",
                "cse4310",
                "cse4311",
            ],
            "keywords": [
                "machine learning",
                "deep learning",
                "computer vision",
                "neural networks",
                "data",
            ],
        },
    }

def build_graph() -> nx.DiGraph:
    G = nx.DiGraph()

    # Add nodes with metadata
    G.add_node("coms2302", name="PROFESSIONAL AND TECHNICAL COMMUNICATION", credits=3, category="unknown")
    G.add_node("creative_arts", name="unknown", credits=3, category="general_education")
    G.add_node("cse1106", name="INTRO TO CSE", credits=1, category="pre_professional")
    G.add_node("cse1310", name="INTRO TO PROGRAMMING", credits=3, category="pre_professional")
    G.add_node("cse1320", name="INTERMEDIATE PROGRAMMING", credits=3, category="pre_professional")
    G.add_node("cse1325", name="OBJECT-ORIENTED PROGRAMMING", credits=3, category="pre_professional")
    G.add_node("cse2312", name="COMPUTER ORGANIZATION", credits=3, category="pre_professional")
    G.add_node("cse2315", name="DISCRETE STRUCTURES", credits=3, category="pre_professional")
    G.add_node("cse3302", name="PROGRAMMING LANGUAGES", credits=3, category="unknown")
    G.add_node("cse3310", name="INTRO TO SOFTWARE ENGINEERING", credits=3, category="unknown")
    G.add_node("cse3314", name="PROFESSIONAL PRACTICES", credits=3, category="unknown")
    G.add_node("cse3315", name="THEORETICAL CS", credits=3, category="unknown")
    G.add_node("cse3318", name="ALGORITHMS & DATA STRUCTURES", credits=3, category="pre_professional")
    G.add_node("cse3320", name="OPERATING SYSTEMS", credits=3, category="unknown")
    G.add_node("cse3330", name="DATABASES", credits=3, category="unknown")
    G.add_node("cse3380", name="LINEAR ALGEBRA", credits=3, category="unknown")
    G.add_node("cse4303", name="COMPUTER GRAPHICS", credits=3, category="professional")
    G.add_node("cse4305", name="COMPILERS", credits=3, category="professional")
    G.add_node("cse4308", name="ARTIFICIAL INTELLIGENCE", credits=3, category="professional")
    G.add_node("cse4316", name="SENIOR DESIGN I", credits=3, category="professional")
    G.add_node("cse4317", name="SENIOR DESIGN II", credits=3, category="professional")
    G.add_node("cse4344", name="COMPUTER NETWORKS", credits=3, category="professional")
    G.add_node("cse4360", name="ROBOTICS", credits=3, category="professional")
    G.add_node("cse4380", name="INFORMATION SECURITY", credits=3, category="professional")
    G.add_node("cse4381", name="INFORMATION SECURITY 2", credits=3, category="professional")
    G.add_node("cse4382", name="SECURE PROGRAMMING", credits=3, category="professional")
    G.add_node("engl1301", name="RHETORIC & COMPOSITION", credits=3, category="pre_professional")
    G.add_node("history1", name="unknown", credits=3, category="general_education")
    G.add_node("history2", name="unknown", credits=3, category="general_education")
    G.add_node("culture", name="unknown", credits=3, category="general_education")
    G.add_node("ie3301", name="ENGINEERING PROBABILITY AND STATISTICS", credits=3, category="unknown")
    G.add_node("math1426", name="CALCULUS I", credits=4, category="pre_professional")
    G.add_node("math2326", name="CALCULUS III", credits=3, category="unknown")
    G.add_node("math2425", name="CALCULUS II", credits=4, category="pre_professional")
    G.add_node("phys1443", name="TECHNICAL PHYSICS I", credits=4, category="pre_professional")
    G.add_node("phys1444", name="TECHNICAL PHYSICS II", credits=4, category="pre_professional")
    G.add_node("pols2311", name="unknown", credits=3, category="general_education")
    G.add_node("pols2312", name="unknown", credits=3, category="general_education")
    G.add_node("univ1131", name="STUDENT SUCCESS", credits=1, category="pre_professional")
    G.add_node("social", name="unknown", credits=3, category="general_education")

    # Tech elective placeholders (Phase 1)
    G.add_node("tech1", name="unknown", credits=3, category="professional")
    G.add_node("tech2", name="unknown", credits=3, category="professional")
    G.add_node("tech3", name="unknown", credits=3, category="professional")
    G.add_node("tech4", name="unknown", credits=3, category="professional")
    G.add_node("tech5", name="unknown", credits=3, category="professional")

    # Add edges (kind: prereq = prerequisite, coreq = corequisite)
    G.add_edge("phys1443", "phys1444", kind="prereq")
    G.add_edge("coms2302", "cse3314", kind="prereq")
    G.add_edge("cse1106", "cse2312", kind="prereq")
    G.add_edge("cse1310", "cse1106", kind="prereq")
    G.add_edge("cse1310", "cse1320", kind="prereq")
    G.add_edge("cse1310", "cse2315", kind="prereq")
    G.add_edge("cse1320", "cse1325", kind="prereq")
    G.add_edge("cse1320", "cse2312", kind="prereq")
    G.add_edge("cse1320", "cse3318", kind="prereq")
    G.add_edge("cse1325", "cse3302", kind="prereq")
    G.add_edge("cse1325", "cse3310", kind="prereq")
    G.add_edge("cse1325", "cse3330", kind="prereq")
    G.add_edge("cse2312", "cse3302", kind="prereq")
    G.add_edge("cse2312", "cse3320", kind="prereq")
    G.add_edge("cse2315", "cse3310", kind="prereq")
    G.add_edge("cse2315", "cse3315", kind="prereq")
    G.add_edge("cse2315", "cse3318", kind="prereq")
    G.add_edge("cse2315", "cse3380", kind="prereq")
    G.add_edge("cse3302", "cse4305", kind="prereq")
    G.add_edge("cse3310", "cse4316", kind="prereq")
    G.add_edge("cse3315", "cse4305", kind="prereq")
    G.add_edge("cse3318", "cse3302", kind="prereq")
    G.add_edge("math2425", "phys1444", kind="coreq")
    G.add_edge("cse3318", "cse3330", kind="prereq")
    G.add_edge("cse3320", "cse4316", kind="prereq")
    G.add_edge("cse3320", "cse4344", kind="prereq")
    G.add_edge("cse3320", "cse4360", kind="prereq")
    G.add_edge("cse3320", "cse4380", kind="prereq")
    G.add_edge("cse3320", "cse4381", kind="prereq")
    G.add_edge("cse3320", "cse4382", kind="prereq")
    G.add_edge("cse3380", "cse4303", kind="prereq")
    G.add_edge("cse3380", "cse4360", kind="prereq")
    G.add_edge("univ1131", "cse1310", kind="coreq")
    G.add_edge("cse4316", "cse4317", kind="prereq")
    G.add_edge("cse4344", "cse4381", kind="coreq")
    G.add_edge("engl1301", "coms2302", kind="prereq")
    G.add_edge("ie3301", "cse4308", kind="prereq")
    G.add_edge("math1426", "cse2315", kind="prereq")
    G.add_edge("math1426", "math2425", kind="prereq")
    G.add_edge("math1426", "phys1443", kind="prereq")
    G.add_edge("math2425", "ie3301", kind="prereq")
    G.add_edge("math2425", "math2326", kind="prereq")
    G.add_edge("cse3318", "cse3314", kind="prereq")
    G.add_edge("cse3314", "cse4316", kind="coreq")

    return G

def course_list() -> list[str]:
    return ['coms2302', 'creative_arts', 'cse1106', 'cse1310', 'cse1320', 'cse1325', 'cse2312', 'cse2315', 'cse3302', 'cse3310', 'cse3314', 'cse3315', 'cse3318', 'cse3320', 'cse3330', 'cse3380', 'cse4308', 'cse4316', 'cse4317', 'cse4344', 'engl1301', 'history1', 'history2', 'culture', 'ie3301', 'math1426', 'math2326', 'math2425', 'phys1443', 'phys1444', 'pols2311', 'pols2312', 'univ1131', 'social', 'tech1', 'tech2', 'tech3', 'tech4', 'tech5', 'security', 'tech_options']
def build_course_list_with_elective_placeholders() -> list[str]:
    """
    Build a list of all course/node ids, then collapse elective option groups.

    Rule:
    - If an elective has options != None
    - and slots < len(options)
    then:
      1. remove all option course ids from the full course list
      2. add the elective group name once

    Example:
    - security: slots=1, options=[cse4380, cse4381, cse4382]
      -> remove those 3 course ids
      -> add "security"
    """

    G = build_graph()
    rules = get_rules()

    # get all node ids only
    all_courses = [node_id for node_id, _ in G.nodes.items()]

    for elective in rules.get("electives", []):
        elective_name = elective.get("name")
        options = elective.get("options")
        slots = elective.get("slots", 0)

        if options is not None and slots < len(options):
            # remove each option course from the full course list
            all_courses = [course for course in all_courses if course not in options]

            # add the elective placeholder/group name once
            if elective_name not in all_courses:
                all_courses.append(elective_name)

    return all_courses

if __name__ == "__main__":
    G = build_graph()
    print("NODES:", G.number_of_nodes())
    print("EDGES:", G.number_of_edges())
    print("RULES:", get_rules())
    final_course_list = build_course_list_with_elective_placeholders()
    print(final_course_list)