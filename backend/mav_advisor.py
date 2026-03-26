# mav_advisor.py
# Usage:
#   python mav_advisor.py
#
# Requirements:
#   pip install networkx
#
# Also requires:
#   cs_course.py in the same folder with build_graph() + get_rules()
#   pdf_extract.py in the same folder with parse_transcript_pdf(pdf_path) -> list[str]
#
# Notes:
# - This version is major-agnostic: it reads lock rules + elective rules from the plan module.
# - Defaults to cs_course, but you can pass another module name:
#     python mav_advisor.py --plan ce_course

from __future__ import annotations

import argparse
import importlib
from typing import Optional

import networkx as nx

from pdf_extract import parse_transcript_pdf


# ----------------------------
# PLAN LOADING
# ----------------------------
def load_plan_module(module_name: str):
    """
    Loads a plan module by import name (preferred) or by filename.
    Accepts:
      - cs_course
      - cs_course.py
    """
    module_name = module_name.strip()
    if module_name.endswith(".py"):
        module_name = module_name[:-3]

    mod = importlib.import_module(module_name)

    if not hasattr(mod, "build_graph"):
        raise AttributeError(f"{module_name} must define build_graph() -> nx.DiGraph")
    if not hasattr(mod, "get_rules"):
        raise AttributeError(f"{module_name} must define get_rules() -> dict")
    return mod


# ----------------------------
# EDGE-TYPE HELPERS
# ----------------------------
def incoming_by_kind(G: nx.DiGraph, course: str, kind: str) -> set[str]:
    out: set[str] = set()
    for u, v, data in G.in_edges(course, data=True):
        if data.get("kind", "prereq") == kind:
            out.add(u)
    return out


def prereqs_of(G: nx.DiGraph, course: str) -> set[str]:
    return incoming_by_kind(G, course, "prereq")


def coreqs_of(G: nx.DiGraph, course: str) -> set[str]:
    return incoming_by_kind(G, course, "coreq")


# ----------------------------
# RULES HELPERS
# ----------------------------
def rules_locked_pairs(rules: dict) -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    for item in rules.get("locked", []):
        cl = str(item.get("category_locked", "")).strip()
        rc = str(item.get("requires_completed", "")).strip()
        if cl and rc:
            out.append((cl, rc))
    return out


def all_in_category(G: nx.DiGraph, category: str) -> set[str]:
    return {n for n, d in G.nodes(data=True) if d.get("category") == category}


def is_locked_by_rules(G: nx.DiGraph, course: str, completed: set[str], rules: dict) -> bool:
    course_cat = G.nodes[course].get("category", "unknown")
    for locked_cat, required_cat in rules_locked_pairs(rules):
        if course_cat == locked_cat:
            required_set = all_in_category(G, required_cat)
            if required_set and not required_set.issubset(completed):
                return True
    return False


def electives_by_name(rules: dict) -> dict:
    out: dict = {}
    for e in rules.get("electives", []):
        name = str(e.get("name", "")).strip()
        if name:
            out[name] = e
    return out


def make_slot_names(elective: dict) -> list[str]:
    slots = int(elective.get("slots", 0) or 0)
    prefix = str(elective.get("slot_prefix", elective.get("name", "slot"))).strip()
    return [f"{prefix}{i}" for i in range(1, slots + 1)]


def elective_options(elective: dict) -> Optional[list[str]]:
    opts = elective.get("options", None)
    if opts is None:
        return None
    if isinstance(opts, list):
        return [str(x).strip().lower() for x in opts if str(x).strip()]
    return None


def elective_slot_nodes_present(G: nx.DiGraph, elective: dict) -> list[str]:
    prefix = str(elective.get("slot_prefix", elective.get("name", "slot"))).strip()
    slots = int(elective.get("slots", 0) or 0)
    candidates = [f"{prefix}{i}" for i in range(1, slots + 1)]
    return [c for c in candidates if c in G.nodes]


def next_open_slot_node(G: nx.DiGraph, completed: set[str], elective: dict) -> Optional[str]:
    nodes = elective_slot_nodes_present(G, elective)
    if nodes:
        for n in nodes:
            if n not in completed:
                return n
        return None

    for n in make_slot_names(elective):
        if n not in completed:
            return n
    return None


def _state_set(completed: set[str], in_progress: set[str]) -> set[str]:
    return set(completed) | set(in_progress)


def _slot_units_taken(G: nx.DiGraph, elective: dict, completed: set[str], in_progress: set[str]) -> int:
    state = _state_set(completed, in_progress)
    count = 0

    for slot in make_slot_names(elective):
        if slot in state:
            count += 1

    if count > 0:
        return count

    prefix = str(elective.get("slot_prefix", elective.get("name", "slot"))).strip()
    if int(elective.get("slots", 0) or 0) == 1 and prefix in state:
        return 1

    return 0


def _direct_option_units_taken(elective: dict, completed: set[str], in_progress: set[str]) -> int:
    opts = set(elective_options(elective) or [])
    if not opts:
        return 0
    state = _state_set(completed, in_progress)
    actual_taken = len(opts & state)
    slot_taken = len({slot for slot in make_slot_names(elective) if slot in state})
    return max(actual_taken, slot_taken)


def elective_group_progress(
    G: nx.DiGraph,
    completed: set[str],
    in_progress: set[str],
    rules: dict,
    elective_name: str,
) -> dict:
    e_map = electives_by_name(rules)
    elective = e_map[elective_name]
    slots = int(elective.get("slots", 0) or 0)
    opts = elective_options(elective)

    if opts:
        taken_count = _direct_option_units_taken(elective, completed, in_progress)
        slots_filled = min(taken_count, slots)
        overflow = max(0, taken_count - slots)
        remaining = max(0, slots - slots_filled)
        return {
            "name": elective_name,
            "slots": slots,
            "options": opts,
            "taken_count": taken_count,
            "slots_filled": slots_filled,
            "remaining": remaining,
            "overflow": overflow,
            "met": remaining == 0,
        }

    direct_fills = _slot_units_taken(G, elective, completed, in_progress)

    incoming_overflow = 0
    for other_name, other_elective in e_map.items():
        other_opts = elective_options(other_elective)
        if not other_opts:
            continue
        carry = str(other_elective.get("carryover", "")).strip()
        if carry != elective_name:
            continue
        other_progress = elective_group_progress(G, completed, in_progress, rules, other_name)
        incoming_overflow += int(other_progress["overflow"])

    total_fills = min(slots, direct_fills + incoming_overflow)
    remaining = max(0, slots - total_fills)

    return {
        "name": elective_name,
        "slots": slots,
        "options": None,
        "direct_fills": direct_fills,
        "incoming_overflow": incoming_overflow,
        "slots_filled": total_fills,
        "remaining": remaining,
        "overflow": 0,
        "met": remaining == 0,
    }


def compute_electives_met(
    G: nx.DiGraph,
    completed: set[str],
    in_progress: set[str],
    rules: dict,
) -> dict[str, bool]:
    out: dict[str, bool] = {}
    for name in electives_by_name(rules).keys():
        progress = elective_group_progress(G, completed, in_progress, rules, name)
        out[name] = bool(progress["met"])
    return out


def build_do_not_recommend(
    G: nx.DiGraph,
    completed: set[str],
    in_progress: set[str],
    rules: dict,
    chosen_option_groups: Optional[set[str]] = None,
) -> set[str]:
    """
    Recommender-only block list for untaken sibling options in option-based groups.
    A group is blocked if:
      - it is already met from prior state, or
      - it has already been represented as a slash-group in the current plan build
    """
    blocked: set[str] = set()
    state = _state_set(completed, in_progress)
    chosen_option_groups = set(chosen_option_groups or set())

    for name, elective in electives_by_name(rules).items():
        opts = elective_options(elective)
        if not opts:
            continue

        progress = elective_group_progress(G, completed, in_progress, rules, name)
        group_is_full = bool(progress["met"]) or (name in chosen_option_groups)

        if group_is_full:
            for c in opts:
                if c not in state:
                    blocked.add(c)

    return blocked


# ----------------------------
# ELIGIBILITY
# ----------------------------
def can_take(G: nx.DiGraph, course: str, completed: set[str], in_progress: set[str], rules: dict) -> bool:
    if course in completed or course in in_progress:
        return False

    if is_locked_by_rules(G, course, completed, rules):
        return False

    prereqs = prereqs_of(G, course)
    coreqs = coreqs_of(G, course)

    prereq_ok = prereqs.issubset(completed)
    coreq_ok = coreqs.issubset(completed | in_progress)

    return prereq_ok and coreq_ok


def eligible_courses(G: nx.DiGraph, completed: set[str], in_progress: set[str], rules: dict) -> list[str]:
    return [c for c in G.nodes if can_take(G, c, completed, in_progress, rules)]


# ----------------------------
# SCORING
# ----------------------------
CATEGORY_BONUS = {
    "pre_professional": 60,
    "professional": 35,
    "general_education": 30,
    "unknown": 45,
}


def unlock_score(G: nx.DiGraph, course: str, completed: set[str]) -> int:
    return sum(1 for d in nx.descendants(G, course) if d not in completed)


def credit_fit_bonus(course_credits: int, current: int, target: int) -> int:
    if current + course_credits > target:
        return -10_000
    remaining = target - (current + course_credits)
    return 20 - remaining


def score_course(
    G: nx.DiGraph,
    course: str,
    completed: set[str],
    in_progress: set[str],
    current_credits: int,
    target_credits: int,
    rules: dict,
) -> int:
    cat = G.nodes[course].get("category", "unknown")
    credits = int(G.nodes[course].get("credits", 3))

    s = 0
    s += 5 * unlock_score(G, course, completed)
    s += CATEGORY_BONUS.get(cat, 20)
    s += credit_fit_bonus(credits, current_credits, target_credits)
    return s


# ----------------------------
# PLAN ENTRY HELPERS
# ----------------------------
def _group_credit_value(G: nx.DiGraph, options: list[str]) -> int:
    if not options:
        return 0
    return int(G.nodes[options[0]].get("credits", 3))


def _group_display_text(options: list[str]) -> str:
    return " / ".join(c.upper() for c in options)


def _build_group_candidates(
    G: nx.DiGraph,
    completed: set[str],
    active_in_progress: set[str],
    rules: dict,
    current_credits: int,
    target_credits: int,
    chosen_option_groups: set[str],
) -> list[dict]:
    """
    Build slash-group candidates for option-based electives.
    A slash-group is created only if:
      - group still has remaining slots
      - multiple options from that group are currently eligible
      - all eligible options in that slash-group have the same credit count
    """
    elig = eligible_courses(G, completed, active_in_progress, rules)
    blocked = build_do_not_recommend(
        G,
        completed,
        active_in_progress,
        rules,
        chosen_option_groups=chosen_option_groups,
    )
    elig = [c for c in elig if c not in blocked]

    group_candidates: list[dict] = []
    e_map = electives_by_name(rules)

    for name, elective in e_map.items():
        opts = elective_options(elective)
        if not opts:
            continue

        progress = elective_group_progress(G, completed, active_in_progress, rules, name)
        if int(progress["remaining"]) <= 0:
            continue
        if name in chosen_option_groups:
            continue

        eligible_opts = [c for c in opts if c in elig]
        if len(eligible_opts) < 2:
            continue

        credit_values = {int(G.nodes[c].get("credits", 3)) for c in eligible_opts}
        if len(credit_values) != 1:
            continue

        group_credit = next(iter(credit_values))
        if current_credits + group_credit > target_credits:
            continue

        option_scores = [
            score_course(G, c, completed, active_in_progress, current_credits, target_credits, rules)
            for c in eligible_opts
        ]
        best_score = max(option_scores)

        group_candidates.append(
            {
                "kind": "choice_group",
                "group_name": name,
                "options": eligible_opts,
                "credits": group_credit,
                "display": _group_display_text(eligible_opts),
                "score": best_score,
                "category": G.nodes[eligible_opts[0]].get("category", "unknown"),
            }
        )

    return group_candidates


# ----------------------------
# PLANNER
# ----------------------------
def recommend_semester_with_gened_range(
    G: nx.DiGraph,
    completed: set[str],
    target_credits: int,
    gened_min: int,
    gened_max: int,
    rules: dict,
    *,
    base_in_progress: Optional[set[str]] = None,
) -> dict:
    """
    Builds one semester plan.

    Returns:
      {
        "entries": [ ... ],
        "total_credits": int
      }

    entries contain:
      - fixed course entry
      - slash-choice group entry
    """
    active_in_progress: set[str] = set(base_in_progress or set())
    chosen_option_groups: set[str] = set()
    entries: list[dict] = []
    credits_now = 0
    gened_taken = 0

    while True:
        elig = eligible_courses(G, completed, active_in_progress, rules)
        if not elig:
            break

        blocked = build_do_not_recommend(
            G,
            completed,
            active_in_progress,
            rules,
            chosen_option_groups=chosen_option_groups,
        )
        elig = [c for c in elig if c not in blocked]
        if not elig:
            break

        group_candidates = _build_group_candidates(
            G,
            completed,
            active_in_progress,
            rules,
            credits_now,
            target_credits,
            chosen_option_groups,
        )

        grouped_option_courses: set[str] = set()
        for group_item in group_candidates:
            for opt in group_item["options"]:
                grouped_option_courses.add(opt)

        individual_candidates: list[dict] = []
        for c in elig:
            if c in grouped_option_courses:
                continue

            cr = int(G.nodes[c].get("credits", 3))
            individual_candidates.append(
                {
                    "kind": "course",
                    "course": c,
                    "credits": cr,
                    "display": c.upper(),
                    "score": score_course(G, c, completed, active_in_progress, credits_now, target_credits, rules),
                    "category": G.nodes[c].get("category", "unknown"),
                }
            )

        candidates = individual_candidates + group_candidates
        if not candidates:
            break

        if gened_taken < gened_min:
            gened_only = [x for x in candidates if x["category"] == "general_education"]
            filtered = gened_only if gened_only else candidates
        elif gened_taken >= gened_max:
            non_gened = [x for x in candidates if x["category"] != "general_education"]
            if non_gened:
                filtered = non_gened
            else:
                break
        else:
            filtered = candidates

        ranked = sorted(filtered, key=lambda x: x["score"], reverse=True)

        picked = None
        for item in ranked:
            if credits_now + int(item["credits"]) <= target_credits:
                picked = item
                break

        if picked is None:
            break

        if picked["kind"] == "course":
            course = picked["course"]
            entry = {
                "kind": "course",
                "display": course.upper(),
                "credits": int(picked["credits"]),
                "courses": [course],
            }
            entries.append(entry)
            active_in_progress.add(course)
            credits_now += int(picked["credits"])

            option_group_name = None
            for name, elective in electives_by_name(rules).items():
                opts = set(elective_options(elective) or [])
                if course in opts:
                    option_group_name = name
                    break
            if option_group_name:
                chosen_option_groups.add(option_group_name)

        else:
            entry = {
                "kind": "choice_group",
                "group_name": picked["group_name"],
                "display": picked["display"],
                "credits": int(picked["credits"]),
                "options": list(picked["options"]),
            }
            entries.append(entry)
            credits_now += int(picked["credits"])
            chosen_option_groups.add(picked["group_name"])

        if picked["category"] == "general_education":
            gened_taken += 1

        if credits_now >= target_credits:
            break

    return {
        "entries": entries,
        "total_credits": credits_now,
    }


def recommend_three_options(
    G: nx.DiGraph,
    completed: set[str],
    target_credits: int,
    rules: dict,
    current_in_progress: Optional[set[str]] = None,
) -> dict[str, dict] | None:
    """
    Generates standard semester variants.
    Slash-group choices are embedded inside each plan instead of exploding into
    many alternative full schedules.
    """
    base_in_progress = set(current_in_progress or set())
    all_elig = eligible_courses(G, completed, base_in_progress, rules)
    base_blocked = build_do_not_recommend(G, completed, base_in_progress, rules)
    all_elig = [c for c in all_elig if c not in base_blocked]

    if len(all_elig) <= 4:
        ranked = sorted(
            all_elig,
            key=lambda c: score_course(G, c, completed, base_in_progress, 0, 10**9, rules),
            reverse=True,
        )
        entries = [
            {
                "kind": "course",
                "display": c.upper(),
                "credits": int(G.nodes[c].get("credits", 3)),
                "courses": [c],
            }
            for c in ranked
        ]
        total = sum(int(G.nodes[c].get("credits", 3)) for c in ranked)
        return {"ALL_REMAINING": {"entries": entries, "total_credits": total}}

    eligible_geneds = [c for c in all_elig if G.nodes[c].get("category") == "general_education"]
    num_eligible_geneds = len(eligible_geneds)

    plans: dict[str, dict] = {}
    seen: list[set[str]] = []

    def _entry_signature(entry: dict) -> str:
        if entry["kind"] == "course":
            return entry["courses"][0]
        return f'GROUP:{entry["group_name"]}:{"|".join(entry["options"])}'

    def _add_plan(label: str, plan_obj: dict) -> None:
        entries = plan_obj.get("entries", [])
        if not entries:
            return
        sig = {_entry_signature(e) for e in entries}
        if any(sig == old for old in seen):
            return
        plans[label] = plan_obj
        seen.append(sig)

    _add_plan(
        "NO_GEN_ED",
        recommend_semester_with_gened_range(
            G,
            completed,
            target_credits,
            0,
            0,
            rules,
            base_in_progress=base_in_progress,
        ),
    )

    if num_eligible_geneds >= 1:
        _add_plan(
            "ONE_GEN_ED_RECOMMENDED",
            recommend_semester_with_gened_range(
                G,
                completed,
                target_credits,
                1,
                1,
                rules,
                base_in_progress=base_in_progress,
            ),
        )

    if num_eligible_geneds >= 2:
        _add_plan(
            "TWO_GEN_ED",
            recommend_semester_with_gened_range(
                G,
                completed,
                target_credits,
                2,
                2,
                rules,
                base_in_progress=base_in_progress,
            ),
        )

    if not plans:
        _add_plan(
            "FALLBACK",
            recommend_semester_with_gened_range(
                G,
                completed,
                target_credits,
                0,
                99,
                rules,
                base_in_progress=base_in_progress,
            ),
        )

    return plans if plans else None


def print_single_plan(G: nx.DiGraph, label: str, plan_obj: dict) -> None:
    print(f"\n{label}")
    displays = [entry["display"].lower() for entry in plan_obj.get("entries", [])]
    print(", ".join(displays))
    print(f'Total credits: {plan_obj.get("total_credits", 0)}')


def print_plan_options(G: nx.DiGraph, plans: dict[str, dict]) -> None:
    if "ALL_REMAINING" in plans:
        print_single_plan(G, "ONLY A FEW CLASSES LEFT, HERE ARE ALL REMAINING ELIGIBLE", plans["ALL_REMAINING"])
        return

    if "NO_GEN_ED" in plans:
        print_single_plan(G, "OPTION 1: NO GENERAL EDUCATION", plans["NO_GEN_ED"])

    if "ONE_GEN_ED_RECOMMENDED" in plans:
        print_single_plan(G, "OPTION 2: ONE GENERAL EDUCATION (RECOMMENDED)", plans["ONE_GEN_ED_RECOMMENDED"])

    if "TWO_GEN_ED" in plans:
        print_single_plan(G, "OPTION 3: TWO GENERAL EDUCATION", plans["TWO_GEN_ED"])

    if "FALLBACK" in plans:
        print_single_plan(G, "FALLBACK OPTION", plans["FALLBACK"])


# ----------------------------
# ELECTIVE SLOT FILLING
# ----------------------------
def mark_elective_satisfied(
    G: nx.DiGraph,
    completed: set[str],
    rules: dict,
    elective_name: str,
) -> str:
    e_map = electives_by_name(rules)
    if elective_name not in e_map:
        return f"Unknown elective group: {elective_name}"

    cur = elective_name
    chain_guard = 0

    while True:
        chain_guard += 1
        if chain_guard > 10:
            return "Carryover loop detected. Marked as EXTRA."

        elective = e_map[cur]
        slot = next_open_slot_node(G, completed, elective)
        if slot is not None:
            completed.add(slot)
            prefix = str(elective.get("slot_prefix", elective.get("name", "slot"))).strip()
            if slot not in G.nodes and prefix in G.nodes:
                completed.add(prefix)
            return f"Counted toward {cur.upper()} as {slot.upper()}."

        carry = elective.get("carryover", None)
        if not carry:
            return f"{cur.upper()} already filled, counted as EXTRA."
        cur = str(carry).strip()


def elective_options_hit(rules: dict, course_id: str) -> Optional[str]:
    e_map = electives_by_name(rules)
    cid = course_id.lower().strip()
    for name, e in e_map.items():
        opts = elective_options(e)
        if opts and cid in opts:
            return name
    return None


# ----------------------------
# UNKNOWN COURSE CLASSIFICATION
# ----------------------------
def build_unknown_menu(rules: dict) -> list[tuple[str, str]]:
    e_map = electives_by_name(rules)
    items: list[tuple[str, str]] = []
    for name in e_map.keys():
        items.append((name, name))
    items.append(("extra", "extra"))
    return items


def print_unknown_menu(rules: dict) -> None:
    e_map = electives_by_name(rules)
    print("Pick what this should count as:")
    idx = 1
    for name, e in e_map.items():
        slots = int(e.get("slots", 0) or 0)
        opts = elective_options(e)
        opts_txt = ""
        if opts:
            opts_txt = f" options: {', '.join([x.upper() for x in opts])}"
        carry = e.get("carryover")
        carry_txt = f", carryover -> {str(carry).upper()}" if carry else ""
        print(f"  {idx}) {name.upper()} (slots={slots}{carry_txt}){opts_txt}")
        idx += 1
    print(f"  {idx}) EXTRA (ignore)")


def fill_unknown_course(G: nx.DiGraph, completed: set[str], unknown_course_label: str, rules: dict) -> None:
    print(f"\nUnrecognized course found: {unknown_course_label.upper()}")
    print_unknown_menu(rules)

    e_map = list(electives_by_name(rules).keys())
    max_choice = len(e_map) + 1

    raw = input(f"Enter 1-{max_choice}: ").strip()
    try:
        choice = int(raw)
    except ValueError:
        choice = max_choice

    if choice == max_choice:
        print("Counted as EXTRA.")
        return

    elective_name = e_map[choice - 1]
    msg = mark_elective_satisfied(G, completed, rules, elective_name)
    print(msg)


# ----------------------------
# PROMPTS
# ----------------------------
def prompt_target_credits() -> int:
    raw = input("\nHow many credits do you want to take next semester? (e.g., 12, 15, 17): ").strip()
    try:
        target = int(raw)
    except ValueError:
        target = 15
    if target <= 0:
        target = 15
    return target


def normalize_manual_course_token(tok: str) -> str:
    return tok.strip().lower().replace(" ", "").replace("-", "").replace("_", "")


def print_parsed_courses(courses: list[str]) -> None:
    if not courses:
        print("\nNo courses detected.")
        return
    print("\nCourses parsed:")
    for c in courses:
        print(f" - {c}")


def build_completed_for_old_student(G: nx.DiGraph, rules: dict) -> set[str]:
    mode = input("\nOld student: (1) upload transcript PDF or (2) paste course list? (1/2): ").strip()
    courses: list[str] = []

    if mode == "1":
        pdf_path = input("Enter transcript PDF path (selectable text PDF): ").strip()
        try:
            courses = parse_transcript_pdf(pdf_path)
        except Exception as e:
            print(f"Could not read PDF: {e}")
            courses = []
    else:
        print("\nPaste completed courses (space or comma separated). Examples:")
        print("  cse1310, math1426, engl1301")
        raw = input("> ").strip()
        courses = [normalize_manual_course_token(x) for x in raw.replace(",", " ").split() if x.strip()]

    print_parsed_courses(courses)

    completed: set[str] = set()
    unknown: list[str] = []

    for c in courses:
        if c in G.nodes:
            completed.add(c)
        else:
            unknown.append(c)

    if unknown:
        print("\nUnrecognized courses detected:")
        for u in unknown:
            print(f" - {u}")

    for unk in unknown:
        fill_unknown_course(G, completed, unk, rules)

    return completed


# ----------------------------
# MAIN
# ----------------------------
def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--plan", default="cs_course", help="plan module name, eg: cs_course or ce_course")
    args = parser.parse_args()

    plan_mod = load_plan_module(args.plan)
    G: nx.DiGraph = plan_mod.build_graph()
    rules: dict = plan_mod.get_rules()

    who = input("Are you a NEW student or an OLD student? (new/old): ").strip().lower()
    if who not in {"new", "old"}:
        who = "new"

    if who == "new":
        completed: set[str] = set()
    else:
        completed = build_completed_for_old_student(G, rules)

    target = prompt_target_credits()

    plans = recommend_three_options(G, completed, target, rules, current_in_progress=set())
    if not plans:
        print("\nNo eligible courses found based on your completed courses.")
        return

    print_plan_options(G, plans)


if __name__ == "__main__":
    main()