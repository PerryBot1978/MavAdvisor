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
                "name": "science",
                "slots": 1,
                "options": None,
                "carryover": None,
                "slot_prefix": "science",
            },
            {
                "name": "tech",
                "slots": 3,
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
        "embedded_systems": {
            "name": "Embedded Systems",
            "degree": "ce",
            "description": (
                "Educates students in the design and testing of embedded systems using "
                "microcontrollers, SoCs, FPGA devices, and real-time systems."
            ),
            "courses": [
                "cse4352",
                "cse4354",
                "cse4355",
                "cse4356",
                "cse3341",
                "cse4357",
                "cse4372",
                "cse4377",
            ],
            "keywords": [
                "embedded",
                "firmware",
                "microcontrollers",
                "fpga",
                "rtos",
            ],
        },

        "unmanned_vehicle_systems": {
            "name": "Unmanned Vehicle Systems (UVS)",
            "degree": "ce",
            "description": (
                "Educates students in the design, development, and operation of unmanned aircraft, "
                "ground, and maritime systems, emphasizing autonomy, sensors, and communications."
            ),
            "courses": [
                "cse4378",
                "cse4379",
                "cse3313",
                "cse3442",
                "cse4342",
                "cse4360",
                "cse4308",
            ],
            "keywords": [
                "robotics",
                "autonomy",
                "sensors",
                "controls",
                "vehicles",
            ],
        },
    }

def build_graph() -> nx.DiGraph:
    G = nx.DiGraph()

    # Add nodes with metadata
    G.add_node('cse1106', name='unknown', credits=1, category='pre_professional')
    G.add_node('univ1131', name='unknown', credits=1, category='pre_professional')
    G.add_node('cse2315', name='unknown', credits=3, category='pre_professional')
    G.add_node('cse1310', name='unknown', credits=3, category='pre_professional')
    G.add_node('cse1320', name='unknown', credits=3, category='pre_professional')
    G.add_node('cse2312', name='unknown', credits=3, category='pre_professional')
    G.add_node('cse1326', name='unknown', credits=3, category='pre_professional')
    G.add_node('cse2441', name='unknown', credits=4, category='pre_professional')
    G.add_node('cse3318', name='unknown', credits=3, category='pre_professional')
    G.add_node('cse3380', name='unknown', credits=3, category='unknown')
    G.add_node('math1426', name='unknown', credits=4, category='pre_professional')
    G.add_node('math2425', name='unknown', credits=4, category='pre_professional')
    G.add_node('phys1443', name='unknown', credits=4, category='pre_professional')
    G.add_node('engl1301', name='unknown', credits=3, category='pre_professional')
    G.add_node('phys1444', name='unknown', credits=4, category='pre_professional')
    G.add_node('cse2440', name='unknown', credits=4, category='pre_professional')
    G.add_node('math2326', name='unknown', credits=3, category='unknown')
    G.add_node('ie3301', name='unknown', credits=3, category='unknown')
    G.add_node('cse3320', name='unknown', credits=3, category='unknown')
    G.add_node('cse3341', name='unknown', credits=3, category='unknown')
    G.add_node('cse3442', name='unknown', credits=4, category='unknown')
    G.add_node('cse3313', name='unknown', credits=3, category='unknown')
    G.add_node('cse3323', name='unknown', credits=3, category='unknown')
    G.add_node('cse4342', name='unknown', credits=3, category='professional')
    G.add_node('coms2302', name='unknown', credits=3, category='unknown')
    G.add_node('cse3314', name='unknown', credits=3, category='unknown')
    G.add_node('cse4316', name='unknown', credits=3, category='professional')
    G.add_node('cse4323', name='unknown', credits=3, category='professional')
    G.add_node('cse4317', name='unknown', credits=3, category='professional')
    G.add_node('tech1', name='unknown', credits=3, category='professional')
    G.add_node('tech2', name='unknown', credits=3, category='professional')
    G.add_node('tech3', name='unknown', credits=3, category='professional')
    G.add_node('history1', name='unknown', credits=3, category='general_education')
    G.add_node('history2', name='unknown', credits=3, category='general_education')
    G.add_node('pols2311', name='unknown', credits=3, category='general_education')
    G.add_node('pols2312', name='unknown', credits=3, category='general_education')
    G.add_node('creative_arts', name='unknown', credits=3, category='general_education')
    G.add_node('social', name='unknown', credits=3, category='general_education')
    G.add_node('culture', name='unknown', credits=3, category='general_education')
    G.add_node('science', name='unknown', credits=4, category='unknown')

    # Add edges (kind: prereq = prerequisite, coreq = corequisite)
    G.add_edge('univ1131', 'cse1310', kind='coreq')
    G.add_edge('cse1310', 'cse2315', kind='prereq')
    G.add_edge('cse1310', 'cse1106', kind='prereq')
    G.add_edge('cse1310', 'cse1320', kind='prereq')
    G.add_edge('cse1106', 'cse2312', kind='prereq')
    G.add_edge('cse1320', 'cse3318', kind='prereq')
    G.add_edge('cse1320', 'cse1326', kind='prereq')
    G.add_edge('cse1320', 'cse2441', kind='prereq')
    G.add_edge('cse1320', 'cse2312', kind='prereq')
    G.add_edge('cse2315', 'cse2441', kind='prereq')
    G.add_edge('cse2315', 'cse3318', kind='prereq')
    G.add_edge('cse2315', 'cse3380', kind='prereq')
    G.add_edge('math1426', 'math2425', kind='prereq')
    G.add_edge('math1426', 'phys1443', kind='prereq')
    G.add_edge('math1426', 'cse2315', kind='prereq')
    G.add_edge('phys1443', 'phys1444', kind='prereq')
    G.add_edge('math2425', 'phys1444', kind='coreq')
    G.add_edge('phys1444', 'cse2440', kind='prereq')
    G.add_edge('math2425', 'math2326', kind='prereq')
    G.add_edge('math2425', 'ie3301', kind='prereq')
    G.add_edge('cse2312', 'cse3320', kind='prereq')
    G.add_edge('cse2441', 'cse3341', kind='prereq')
    G.add_edge('cse2312', 'cse3442', kind='prereq')
    G.add_edge('cse2441', 'cse3442', kind='prereq')
    G.add_edge('cse3318', 'cse3313', kind='prereq')
    G.add_edge('cse3380', 'cse3313', kind='prereq')
    G.add_edge('cse2440', 'cse3323', kind='prereq')
    G.add_edge('cse2440', 'cse3442', kind='prereq')
    G.add_edge('cse3323', 'cse4342', kind='prereq')
    G.add_edge('engl1301', 'coms2302', kind='prereq')
    G.add_edge('coms2302', 'cse3314', kind='prereq')
    G.add_edge('cse3442', 'cse4342', kind='prereq')
    G.add_edge('cse3442', 'cse4316', kind='prereq')
    G.add_edge('cse3313', 'cse4342', kind='prereq')
    G.add_edge('cse3320', 'cse4323', kind='prereq')
    G.add_edge('cse3320', 'cse4316', kind='prereq')
    G.add_edge('cse3318', 'cse3314', kind='prereq')
    G.add_edge('cse3314', 'cse4316', kind='coreq')
    G.add_edge('cse4316', 'cse4317', kind='prereq')
    return G

def course_list() -> list[str]:
    return ['cse1106', 'univ1131', 'cse2315', 'cse1310', 'cse1320', 'cse2312', 'cse1326', 'cse2441', 'cse3318', 'cse3380', 'math1426', 'math2425', 'phys1443', 'engl1301', 'phys1444', 'cse2440', 'math2326', 'ie3301', 'cse3320', 'cse3341', 'cse3442', 'cse3313', 'cse3323', 'cse4342', 'coms2302', 'cse3314', 'cse4316', 'cse4323', 'cse4317', 'tech1', 'tech2', 'tech3', 'history1', 'history2', 'pols2311', 'pols2312', 'creative_arts', 'social', 'culture', 'science']
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
