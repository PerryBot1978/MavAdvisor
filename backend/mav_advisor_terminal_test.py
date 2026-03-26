# mav_advisor_terminal_test.py
# Terminal-only test flow: login/create account, then advisor flow with certificate suggestions.
# Reuses mav_advisor.py and course modules. Student data stored in users/*.json.
# Run: python mav_advisor_terminal_test.py

from __future__ import annotations

import json
import os
import re
from datetime import datetime

import calculate_score_certificate as cert_help
import mav_advisor as advisor

USERS_DIR = "users"


def _ensure_users_dir() -> None:
    if not os.path.isdir(USERS_DIR):
        os.makedirs(USERS_DIR)


def _uta_id_valid(uta_id: str) -> bool:
    s = (uta_id or "").strip()
    return bool(s and re.match(r"^[a-zA-Z0-9_]+$", s))


def _user_path(uta_id: str) -> str:
    return os.path.join(USERS_DIR, f"{uta_id.strip().lower()}.json")


def _load_user(uta_id: str) -> dict | None:
    path = _user_path(uta_id)
    if not os.path.isfile(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return None


def _save_user(data: dict) -> None:
    uta_id = (data.get("uta_id") or "").strip().lower()
    if not uta_id:
        return
    _ensure_users_dir()
    path = _user_path(uta_id)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def _plan_module_for_degree(degree: str) -> str:
    return "cs_course" if degree.strip().lower() == "cs" else "ce_course"


def _load_certificates_for_degree(degree: str) -> dict:
    mod_name = _plan_module_for_degree(degree)
    mod = advisor.load_plan_module(mod_name)
    return getattr(mod, "get_certificates", lambda: {})()


def _normalize_user_data(user: dict) -> dict:
    user.setdefault("selected_keywords", [])
    user.setdefault("certificate_scores", {})
    user.setdefault("top_certificates", [])
    user.setdefault("completed_courses", [])
    user.setdefault("in_progress_courses", [])
    user.setdefault("electives_met", {})
    user.setdefault("updates", [])

    user["selected_keywords"] = list(dict.fromkeys(user.get("selected_keywords", [])))
    user["completed_courses"] = list(dict.fromkeys(user.get("completed_courses", [])))
    user["in_progress_courses"] = list(dict.fromkeys(user.get("in_progress_courses", [])))
    return user


def _timestamp() -> str:
    return datetime.now().isoformat(timespec="seconds")


def _add_update(user: dict, action: str, details: dict | None = None) -> None:
    entry = {
        "timestamp": _timestamp(),
        "action": action,
        "details": details or {},
    }
    user.setdefault("updates", [])
    user["updates"].append(entry)


def _print_course_list(title: str, courses: list[str], G) -> None:
    print(f"\n{title}")
    if not courses:
        print("  None")
        return

    for c in courses:
        if c in G.nodes:
            name = G.nodes[c].get("name", "UNKNOWN")
            cr = int(G.nodes[c].get("credits", 3))
            print(f"  - {c.upper():<12} | {cr} cr | {name}")
        else:
            print(f"  - {c.upper()}")


def _select_some_courses_from_in_progress(in_progress_courses: list[str], G) -> tuple[list[str], list[str]]:
    if not in_progress_courses:
        return [], []

    print("\nYour current in-progress courses:")
    for i, c in enumerate(in_progress_courses, 1):
        if c in G.nodes:
            name = G.nodes[c].get("name", "UNKNOWN")
            print(f"  {i}) {c.upper()} - {name}")
        else:
            print(f"  {i}) {c.upper()}")

    print("Enter the numbers of the courses you completed, separated by spaces.")
    print("Example: 1 3")
    raw = input("> ").strip()

    selected: list[str] = []
    if raw:
        for part in raw.split():
            try:
                idx = int(part)
                if 1 <= idx <= len(in_progress_courses):
                    selected.append(in_progress_courses[idx - 1])
            except ValueError:
                pass

    selected = list(dict.fromkeys(selected))
    remaining = [c for c in in_progress_courses if c not in selected]
    return selected, remaining


def _resolve_saved_progress(user: dict, G) -> None:
    in_progress = list(dict.fromkeys(user.get("in_progress_courses", [])))
    completed = set(user.get("completed_courses", []))

    if not in_progress:
        return

    _print_course_list("Courses currently in progress", in_progress, G)
    raw = input("\nHave you completed all of these courses? (y/n): ").strip().lower()

    if raw == "y":
        for c in in_progress:
            completed.add(c)
        user["completed_courses"] = sorted(completed)
        user["in_progress_courses"] = []
        _add_update(
            user,
            "in_progress_moved_to_completed",
            {"courses": in_progress, "mode": "all"},
        )
        _save_user(user)
        print("Moved all in-progress courses to completed.")
        return

    partial = input("Did you complete some of them? (y/n): ").strip().lower()
    if partial == "y":
        selected_done, remaining = _select_some_courses_from_in_progress(in_progress, G)
        for c in selected_done:
            completed.add(c)

        user["completed_courses"] = sorted(completed)
        user["in_progress_courses"] = remaining
        _add_update(
            user,
            "in_progress_moved_to_completed",
            {"courses": selected_done, "mode": "partial", "remaining": remaining},
        )
        _save_user(user)

        if selected_done:
            print("Updated completed and in-progress courses.")
        else:
            print("No courses were marked completed.")
    else:
        print("Keeping existing in-progress courses as-is.")


def _get_completed_from_saved_or_prompt(user: dict, G, rules: dict) -> set[str]:
    saved_completed = set(user.get("completed_courses", []))

    if saved_completed:
        _print_course_list("Saved completed courses", sorted(saved_completed), G)
        use_saved = input("\nUse saved completed courses? (y/n): ").strip().lower()
        if use_saved == "y":
            return saved_completed

    who = input("\nAre you a NEW student or an OLD student? (new/old): ").strip().lower()
    if who not in {"new", "old"}:
        who = "new"

    if who == "new":
        return set()

    parsed_completed = advisor.build_completed_for_old_student(G, rules)
    combined = set(saved_completed) | set(parsed_completed)

    user["completed_courses"] = sorted(combined)
    _add_update(
        user,
        "completed_courses_updated_from_input",
        {"courses": sorted(parsed_completed)},
    )
    _save_user(user)
    return combined


def _ordered_plan_labels(plans: dict[str, dict]) -> list[str]:
    preferred_order = [
        "NO_GEN_ED",
        "ONE_GEN_ED_RECOMMENDED",
        "TWO_GEN_ED",
        "FALLBACK",
        "ALL_REMAINING",
    ]
    labels = [label for label in preferred_order if label in plans]
    for label in plans.keys():
        if label not in labels:
            labels.append(label)
    return labels


def _friendly_label(label: str) -> str:
    mapping = {
        "NO_GEN_ED": "Option 1: No General Education",
        "ONE_GEN_ED_RECOMMENDED": "Option 2: One General Education (Recommended)",
        "TWO_GEN_ED": "Option 3: Two General Education",
        "FALLBACK": "Fallback Option",
        "ALL_REMAINING": "All Remaining Eligible Courses",
    }
    return mapping.get(label, label.replace("_", " ").title())


def _prompt_select_plan_option(plans: dict[str, dict], G) -> tuple[str | None, dict | None]:
    labels = _ordered_plan_labels(plans)
    if not labels:
        return None, None

    print("\nSelect which course option you want to take.")
    for i, label in enumerate(labels, 1):
        plan_obj = plans[label]
        pretty = _friendly_label(label)
        total = int(plan_obj.get("total_credits", 0))
        print(f"  {i}) {pretty} [{total} credits]")
        for entry in plan_obj.get("entries", []):
            if entry["kind"] == "course":
                c = entry["courses"][0]
                name = G.nodes[c].get("name", "UNKNOWN") if c in G.nodes else "UNKNOWN"
                print(f"     - {c.upper()} | {name}")
            else:
                print(f'     - {entry["display"]} | choose one')

    raw = input("\nEnter the option number to add those courses to in-progress, or press Enter to skip: ").strip()
    if not raw:
        return None, None

    try:
        idx = int(raw)
    except ValueError:
        return None, None

    if not (1 <= idx <= len(labels)):
        return None, None

    chosen_label = labels[idx - 1]
    return chosen_label, plans[chosen_label]


def _resolve_choice_groups_for_selected_plan(plan_obj: dict, G) -> list[str]:
    resolved_courses: list[str] = []

    for entry in plan_obj.get("entries", []):
        if entry["kind"] == "course":
            resolved_courses.extend(entry["courses"])
            continue

        options = entry.get("options", [])
        if not options:
            continue

        print(f'\nChoose one for: {entry["display"]}')
        for i, c in enumerate(options, 1):
            name = G.nodes[c].get("name", "UNKNOWN") if c in G.nodes else "UNKNOWN"
            print(f"  {i}) {c.upper()} | {name}")

        raw = input("Enter choice number: ").strip()
        try:
            idx = int(raw)
        except ValueError:
            idx = 1

        if not (1 <= idx <= len(options)):
            idx = 1

        resolved_courses.append(options[idx - 1])

    return list(dict.fromkeys(resolved_courses))


def _save_selected_plan_to_in_progress(user: dict, label: str, courses: list[str]) -> None:
    existing_in_progress = list(dict.fromkeys(user.get("in_progress_courses", [])))
    for c in courses:
        if c not in existing_in_progress:
            existing_in_progress.append(c)

    completed = set(user.get("completed_courses", []))
    existing_in_progress = [c for c in existing_in_progress if c not in completed]

    user["in_progress_courses"] = existing_in_progress
    _add_update(
        user,
        "plan_selected",
        {"option": label, "courses": courses},
    )
    _save_user(user)


def _get_certificate_progress(
    certificates: dict,
    cert_names: list[str],
    completed: set[str],
    in_progress: set[str],
) -> dict:
    progress: dict = {}

    for cert_key in cert_names:
        cert = certificates.get(cert_key)
        if not cert:
            continue

        cert_courses = [str(c).strip().lower() for c in cert.get("courses", []) if str(c).strip()]
        completed_list = [c for c in cert_courses if c in completed]
        in_progress_list = [c for c in cert_courses if c in in_progress]
        remaining_list = [c for c in cert_courses if c not in completed and c not in in_progress]

        progress[cert_key] = {
            "name": cert.get("name", cert_key),
            "completed": completed_list,
            "in_progress": in_progress_list,
            "remaining": remaining_list,
        }

    return progress


def _print_certificate_summary(certificate_progress: dict, G) -> None:
    if not certificate_progress:
        return

    print("\nCertificate suggestions based on your interests:")
    for _, info in certificate_progress.items():
        print(f"\n{info['name']}")

        if info["completed"]:
            print("  Completed:")
            for c in info["completed"]:
                name = G.nodes[c].get("name", "UNKNOWN") if c in G.nodes else "UNKNOWN"
                print(f"   - {c.upper()} | {name}")

        if info["in_progress"]:
            print("  In progress:")
            for c in info["in_progress"]:
                name = G.nodes[c].get("name", "UNKNOWN") if c in G.nodes else "UNKNOWN"
                print(f"   - {c.upper()} | {name}")

        if info["remaining"]:
            print("  Electives you still need to take:")
            for c in info["remaining"]:
                name = G.nodes[c].get("name", "UNKNOWN") if c in G.nodes else "UNKNOWN"
                print(f"   - {c.upper()} | {name}")
        else:
            print("  All certificate courses are complete or already in progress.")


def main() -> None:
    _ensure_users_dir()

    choice = input("(1) Create account  (2) Login\nEnter 1 or 2: ").strip()
    if choice not in {"1", "2"}:
        choice = "2"

    uta_id = input("Enter your UTA ID (e.g. sxv3105): ").strip()
    if not _uta_id_valid(uta_id):
        print("Invalid UTA ID. Use letters, numbers, underscores only.")
        return
    uta_id_lower = uta_id.lower()

    user = _load_user(uta_id_lower)
    if choice == "2" and user is None:
        print("No account found for that UTA ID. Creating account instead.")
        choice = "1"

    if choice == "1" and user is None:
        degree_choice = input("Select degree plan: (1) cs  (2) ce\nEnter 1 or 2: ").strip()
        degree = "cs" if degree_choice == "1" else "ce"

        certificates = _load_certificates_for_degree(degree)
        all_keywords = cert_help.get_unique_certificate_keywords(certificates)

        selected_keywords: list[str] = []
        if all_keywords:
            print("\nInterest keywords for your degree:")
            for i, kw in enumerate(all_keywords, 1):
                print(f"  {i}) {kw}")
            print("Enter numbers to select (e.g. 1 3 5), or press Enter to skip:")
            raw = input("> ").strip()
            if raw:
                for part in raw.split():
                    try:
                        idx = int(part)
                        if 1 <= idx <= len(all_keywords):
                            selected_keywords.append(all_keywords[idx - 1])
                    except ValueError:
                        pass
            selected_keywords = list(dict.fromkeys(selected_keywords))

        certificate_scores = cert_help.score_certificates(certificates, selected_keywords)
        top_certificates = cert_help.get_top_certificates(certificate_scores)

        user = {
            "uta_id": uta_id_lower,
            "degree": degree,
            "selected_keywords": selected_keywords,
            "certificate_scores": certificate_scores,
            "top_certificates": top_certificates,
            "completed_courses": [],
            "in_progress_courses": [],
            "electives_met": {},
            "updates": [],
        }
        _add_update(
            user,
            "account_created",
            {
                "degree": degree,
                "selected_keywords": selected_keywords,
                "top_certificates": top_certificates,
            },
        )
        _save_user(user)
        print("Account created and saved.")

    if user is None:
        return

    user = _normalize_user_data(user)
    degree = user.get("degree") or "cs"
    plan_module_name = _plan_module_for_degree(degree)
    plan_mod = advisor.load_plan_module(plan_module_name)
    G = plan_mod.build_graph()
    rules = plan_mod.get_rules()
    certificates = _load_certificates_for_degree(degree)

    _resolve_saved_progress(user, G)

    completed = _get_completed_from_saved_or_prompt(user, G, rules)
    saved_in_progress = set(dict.fromkeys(user.get("in_progress_courses", [])))

    if saved_in_progress:
        _print_course_list("Still in-progress courses", sorted(saved_in_progress), G)

    user["electives_met"] = advisor.compute_electives_met(G, completed, saved_in_progress, rules)
    user["completed_courses"] = sorted(set(completed))
    _save_user(user)

    certificate_progress = _get_certificate_progress(
        certificates,
        user.get("top_certificates", []),
        set(completed),
        saved_in_progress,
    )
    _print_certificate_summary(certificate_progress, G)

    target = advisor.prompt_target_credits()

    plans = advisor.recommend_three_options(
        G,
        completed,
        target,
        rules,
        current_in_progress=saved_in_progress,
    )
    if not plans:
        print("\nNo eligible courses found based on your completed courses.")
        return

    advisor.print_plan_options(G, plans)

    chosen_label, chosen_plan_obj = _prompt_select_plan_option(plans, G)
    if chosen_label and chosen_plan_obj:
        resolved_courses = _resolve_choice_groups_for_selected_plan(chosen_plan_obj, G)
        _save_selected_plan_to_in_progress(user, chosen_label, resolved_courses)
        print("\nSelected courses have been added to your in-progress list.")
        _print_course_list("Updated in-progress courses", user.get("in_progress_courses", []), G)
    else:
        print("\nNo plan option selected. Nothing was added to in-progress.")

    final_completed = set(user.get("completed_courses", []))
    final_in_progress = set(user.get("in_progress_courses", []))
    user["electives_met"] = advisor.compute_electives_met(G, final_completed, final_in_progress, rules)
    user["completed_courses"] = sorted(final_completed)
    user["in_progress_courses"] = sorted(final_in_progress)
    _save_user(user)


if __name__ == "__main__":
    main()