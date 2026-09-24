"""Create Redmine child issues and checklist tasks from JSON section plan."""

from __future__ import annotations

import argparse
import getpass
import json
import os
import re
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup, Tag


BASE_URL = "http://redmine.mirle.com.tw"
PROJECT_IDENTIFIER = "9bc"
DEFAULT_TRACKER_NAME = "Feature"


class RedmineError(RuntimeError):
    """Raised when Redmine cannot complete the requested action."""


@dataclass(frozen=True)
class IssuePlan:
    subject: str
    section_heading: str
    checklist_items: list[str]


@dataclass(frozen=True)
class RedmineFormDefaults:
    action_url: str
    authenticity_token: str
    project_id: str
    tracker_id: str
    status_id: str
    priority_id: str
    assigned_to_id: str


@dataclass(frozen=True)
class CreatedTaskRecord:
    issue_id: str
    subject: str


@dataclass(frozen=True)
class CreatedSectionRecord:
    issue_id: str
    subject: str
    tasks: list[CreatedTaskRecord]


def normalize_text(value: str) -> str:
    return " ".join(value.split())


def strip_markdown_checkbox(line: str) -> str:
    return re.sub(r"^-\s*\[[ xX]\]\s*", "", line.strip()).strip()


def truncate_subject(subject: str, limit: int = 120) -> str:
    normalized = normalize_text(subject)
    if len(normalized) <= limit:
        return normalized
    return normalized[: limit - 1].rstrip() + "…"


def load_section_plan_from_json(path: Path) -> tuple[str, list[tuple[str, str]]]:
    """Load section plan from JSON file.
    
    Expected JSON format:
    {
        "parent_issue_id": "41627",
        "tracker": "Feature",  # optional, can be overridden via CLI
        "sections": [
            {"subject": "...", "section_heading": "..."},
            ...
        ]
    }
    
    Returns:
        Tuple of (parent_issue_id, [(subject, section_heading), ...])
    """
    if not path.exists():
        raise FileNotFoundError(f"找不到 JSON 配置檔案: {path}")

    try:
        content = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise ValueError(f"JSON 解析失敗: {error}")

    # Validate required fields
    if "parent_issue_id" not in content:
        raise ValueError("JSON 缺少必要欄位: parent_issue_id")
    if "sections" not in content:
        raise ValueError("JSON 缺少必要欄位: sections")

    parent_issue_id = str(content["parent_issue_id"]).strip()
    if not parent_issue_id:
        raise ValueError("parent_issue_id 不可為空")

    if not isinstance(content["sections"], list):
        raise ValueError("sections 必須是陣列")

    sections = []
    for index, section in enumerate(content["sections"]):
        if not isinstance(section, dict):
            raise ValueError(f"sections[{index}] 必須是物件")
        if "subject" not in section:
            raise ValueError(f"sections[{index}] 缺少 subject")
        if "section_heading" not in section:
            raise ValueError(f"sections[{index}] 缺少 section_heading")

        subject = str(section["subject"]).strip()
        section_heading = str(section["section_heading"]).strip()

        if not subject or not section_heading:
            raise ValueError(f"sections[{index}] 的 subject 和 section_heading 不可為空")

        sections.append((subject, section_heading))

    if not sections:
        raise ValueError("sections 不能為空陣列")

    return parent_issue_id, sections


def parse_markdown_with_section_plan(
    path: Path,
    section_plan: list[tuple[str, str]],
) -> list[IssuePlan]:
    """Parse Markdown file using provided section plan mapping.
    
    Args:
        path: Path to Markdown file
        section_plan: List of (subject, section_heading) tuples
    
    Returns:
        List of IssuePlan objects with checklist items
    """
    if not path.exists():
        raise FileNotFoundError(f"找不到 Markdown 檔案: {path}")

    lines = path.read_text(encoding="utf-8").splitlines()
    plans: list[IssuePlan] = []

    for subject, section_heading in section_plan:
        section_start = next(
            (index for index, line in enumerate(lines) if line.strip() == f"## {section_heading}"),
            None,
        )
        if section_start is None:
            raise ValueError(f"找不到章節: ## {section_heading}")

        section_end = next(
            (
                index
                for index in range(section_start + 1, len(lines))
                if lines[index].startswith("## ")
            ),
            len(lines),
        )
        section_lines = lines[section_start:section_end]

        checklist_start = next(
            (index for index, line in enumerate(section_lines) if line.strip() == "### Checklist"),
            None,
        )
        if checklist_start is None:
            raise ValueError(f"章節沒有 Checklist: ## {section_heading}")

        checklist_items: list[str] = []
        for line in section_lines[checklist_start + 1 :]:
            stripped = line.strip()
            if stripped.startswith("### "):
                break
            if re.match(r"^-\s*\[[ xX]\]", stripped):
                checklist_items.append(strip_markdown_checkbox(stripped))

        if not checklist_items:
            raise ValueError(f"章節 Checklist 沒有項目: ## {section_heading}")

        plans.append(
            IssuePlan(
                subject=subject,
                section_heading=section_heading,
                checklist_items=checklist_items,
            )
        )

    return plans


def get_credentials() -> tuple[str, str]:
    username = os.environ.get("REDMINE_USERNAME") or input("Redmine username: ").strip()
    password = os.environ.get("REDMINE_PASSWORD") or getpass.getpass("Redmine password: ")
    if not username or not password:
        raise ValueError("Redmine username/password 不可為空")
    return username, password


def find_input_value(soup: BeautifulSoup | Tag, name: str) -> str:
    element = soup.find("input", {"name": name})
    if element is None:
        raise RedmineError(f"找不到表單欄位: {name}")
    value = element.get("value")
    if value is None:
        raise RedmineError(f"表單欄位沒有值: {name}")
    return str(value)


def login(session: requests.Session, username: str, password: str) -> None:
    login_url = urljoin(BASE_URL, "/login")
    response = session.get(login_url, timeout=20)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    token = find_input_value(soup, "authenticity_token")
    payload = {
        "utf8": "✓",
        "authenticity_token": token,
        "username": username,
        "password": password,
        "login": "Login",
    }

    response = session.post(login_url, data=payload, timeout=20, allow_redirects=True)
    response.raise_for_status()
    if "/login" in response.url or "id=\"login-form\"" in response.text:
        raise RedmineError("Redmine 登入失敗，請確認帳號密碼或網路權限")


def select_value_by_label(form: Tag, name: str, label: str) -> str:
    select = form.find("select", {"name": name})
    if select is None:
        raise RedmineError(f"找不到下拉欄位: {name}")

    expected = normalize_text(label).lower()
    options = select.find_all("option")
    for option in options:
        text = normalize_text(option.get_text(" ", strip=True)).lower()
        if text == expected:
            value = option.get("value")
            if value:
                return str(value)

    available = ", ".join(normalize_text(option.get_text(" ", strip=True)) for option in options)
    raise RedmineError(f"{name} 找不到選項 {label!r}，可用選項: {available}")


def selected_or_first_value(form: Tag, name: str) -> str:
    select = form.find("select", {"name": name})
    if select is not None:
        selected = select.find("option", selected=True)
        option = selected or select.find("option", value=True)
        if option is not None and option.get("value") is not None:
            return str(option.get("value"))

    input_element = form.find("input", {"name": name})
    if input_element is not None and input_element.get("value") is not None:
        return str(input_element.get("value"))

    raise RedmineError(f"找不到可用欄位值: {name}")


def assignee_to_me_value(form: Tag) -> str:
    select = form.find("select", {"name": "issue[assigned_to_id]"})
    if select is None:
        raise RedmineError("找不到 Assignee 下拉欄位")

    options = select.find_all("option")
    for option in options:
        text = normalize_text(option.get_text(" ", strip=True)).lower()
        if text in {"<< me >>", "<<me>>"}:
            value = option.get("value")
            if value:
                return str(value)

    available = ", ".join(normalize_text(option.get_text(" ", strip=True)) for option in options)
    raise RedmineError(f"Assignee 找不到 << me >>，可用選項: {available}")


def fetch_issue_form(
    session: requests.Session,
    parent_issue_id: str,
    tracker_name: str,
) -> RedmineFormDefaults:
    form_url = (
        f"/projects/{PROJECT_IDENTIFIER}/issues/new"
        f"?back_url=%2Fissues%2F{parent_issue_id}"
        f"&issue%5Bparent_issue_id%5D={parent_issue_id}"
    )
    response = session.get(urljoin(BASE_URL, form_url), timeout=20)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    form = soup.find("form", {"id": "issue-form"})
    if form is None:
        raise RedmineError("找不到 Redmine issue 建立表單，可能尚未登入或沒有此專案權限")

    action = form.get("action")
    if not action:
        raise RedmineError("Issue 建立表單缺少 action")

    return RedmineFormDefaults(
        action_url=urljoin(BASE_URL, str(action)),
        authenticity_token=find_input_value(form, "authenticity_token"),
        project_id=selected_or_first_value(form, "issue[project_id]"),
        tracker_id=select_value_by_label(form, "issue[tracker_id]", tracker_name),
        status_id=selected_or_first_value(form, "issue[status_id]"),
        priority_id=selected_or_first_value(form, "issue[priority_id]"),
        assigned_to_id=assignee_to_me_value(form),
    )


def issue_child_exists(session: requests.Session, parent_issue_id: str, subject: str) -> str | None:
    response = session.get(urljoin(BASE_URL, f"/issues/{parent_issue_id}"), timeout=20)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    expected = normalize_text(subject)
    matches: list[int] = []

    for row in soup.select("tr.issue"):
        row_text = normalize_text(row.get_text(" ", strip=True))
        for link in row.find_all("a", href=re.compile(r"^/issues/\d+$")):
            link_text = normalize_text(link.get_text(" ", strip=True))
            if link_text != expected and expected not in row_text:
                continue

            match = re.search(r"/issues/(\d+)", str(link.get("href")))
            if match and match.group(1) != parent_issue_id:
                matches.append(int(match.group(1)))

    if matches:
        return str(max(matches))

    return None


def build_payload(
    defaults: RedmineFormDefaults,
    parent_issue_id: str,
    subject: str,
    description: str,
) -> dict[str, str]:
    return {
        "utf8": "✓",
        "authenticity_token": defaults.authenticity_token,
        "form_update_triggered_by": "",
        "back_url": f"/issues/{parent_issue_id}",
        "issue[is_private]": "0",
        "issue[project_id]": defaults.project_id,
        "issue[tracker_id]": defaults.tracker_id,
        "issue[subject]": subject,
        "issue[description]": description,
        "issue[status_id]": defaults.status_id,
        "was_default_status": defaults.status_id,
        "issue[priority_id]": defaults.priority_id,
        "issue[assigned_to_id]": defaults.assigned_to_id,
        "issue[parent_issue_id]": parent_issue_id,
        "issue[start_date]": "",
        "issue[due_date]": "",
        "issue[estimated_hours]": "",
        "issue[done_ratio]": "0",
        "issue[watcher_user_ids][]": "",
        "commit": "Create",
    }


def create_issue(
    session: requests.Session,
    parent_issue_id: str,
    subject: str,
    description: str,
    tracker_name: str,
    allow_duplicate: bool,
    dry_run: bool,
) -> str:
    if dry_run:
        raise RuntimeError("dry-run must not call create_issue")

    if not allow_duplicate:
        existing_issue_id = issue_child_exists(session, parent_issue_id, subject)
        if existing_issue_id is not None:
            print(f"Skip existing #{existing_issue_id}: {subject}")
            return existing_issue_id

    defaults = fetch_issue_form(session, parent_issue_id, tracker_name)
    payload = build_payload(defaults, parent_issue_id, subject, description)

    response = session.post(defaults.action_url, data=payload, timeout=20, allow_redirects=True)
    response.raise_for_status()
    if "/issues/new" in response.url or "errorExplanation" in response.text:
        soup = BeautifulSoup(response.text, "html.parser")
        errors = [item.get_text(" ", strip=True) for item in soup.select("#errorExplanation li")]
        raise RedmineError("建立議題失敗: " + "; ".join(errors or ["Redmine 回到新增頁面"]))

    issue_id = issue_child_exists(session, parent_issue_id, subject)
    if issue_id is None:
        raise RedmineError(f"建立成功但無法在父議題 #{parent_issue_id} 下找到子議題: {subject}")

    print(f"Created {tracker_name} #{issue_id}: {subject}")
    return issue_id


def build_section_description(plan: IssuePlan, markdown_path: Path, config_path: Path) -> str:
    checklist = "\n".join(f"- [ ] {item}" for item in plan.checklist_items)
    return (
        f"來源 Markdown: {markdown_path.as_posix()}\n"
        f"來源配置: {config_path.as_posix()}\n"
        f"來源章節: ## {plan.section_heading}\n\n"
        "此議題用來追蹤該階段驗證；下層 task 會依 Checklist 逐項建立。\n\n"
        "Checklist:\n"
        f"{checklist}"
    )


def build_task_description(plan: IssuePlan, item: str, markdown_path: Path, config_path: Path) -> str:
    return (
        f"父項目: {plan.subject}\n"
        f"來源 Markdown: {markdown_path.as_posix()}\n"
        f"來源配置: {config_path.as_posix()}\n"
        f"來源章節: ## {plan.section_heading} / ### Checklist\n\n"
        f"確認事項:\n- [ ] {item}"
    )


def create_issues_from_plan(
    session: requests.Session,
    plans: list[IssuePlan],
    parent_issue_id: str,
    tracker_name: str,
    markdown_path: Path,
    config_path: Path,
    allow_duplicate: bool,
    dry_run: bool,
) -> list[CreatedSectionRecord]:
    if dry_run:
        raise RuntimeError("dry-run must not call create_issues_from_plan")

    records: list[CreatedSectionRecord] = []
    for plan in plans:
        child_issue_id = create_issue(
            session=session,
            parent_issue_id=parent_issue_id,
            subject=plan.subject,
            description=build_section_description(plan, markdown_path, config_path),
            tracker_name=tracker_name,
            allow_duplicate=allow_duplicate,
            dry_run=dry_run,
        )

        task_records: list[CreatedTaskRecord] = []
        for index, item in enumerate(plan.checklist_items, start=1):
            task_subject = truncate_subject(f"{index:02d}. {item}")
            task_issue_id = create_issue(
                session=session,
                parent_issue_id=child_issue_id,
                subject=task_subject,
                description=build_task_description(plan, item, markdown_path, config_path),
                tracker_name=tracker_name,
                allow_duplicate=allow_duplicate,
                dry_run=dry_run,
            )
            task_records.append(CreatedTaskRecord(issue_id=task_issue_id, subject=task_subject))

        records.append(
            CreatedSectionRecord(
                issue_id=child_issue_id,
                subject=plan.subject,
                tasks=task_records,
            )
        )

    return records


def write_id_record(
    records: list[CreatedSectionRecord],
    parent_issue_id: str,
    markdown_path: Path,
    config_path: Path,
    output_path: Path,
) -> None:
    lines = [
        "# Redmine Task ID Record",
        "",
        f"Date: {date.today().isoformat()}",
        f"Parent issue: #{parent_issue_id}",
        f"Source markdown: {markdown_path.as_posix()}",
        f"Source config: {config_path.as_posix()}",
        "",
        "## Structure",
        "",
    ]

    for section in records:
        lines.extend(
            [
                f"### #{section.issue_id} {section.subject}",
                "",
                f"- Redmine: {BASE_URL}/issues/{section.issue_id}",
                "- Tasks:",
            ]
        )
        for task in section.tasks:
            lines.append(f"  - #{task.issue_id} {task.subject}")
        lines.append("")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote Redmine ID record: {output_path}")


def print_plan(plans: list[IssuePlan], parent_issue_id: str) -> None:
    print(f"Parent issue: #{parent_issue_id}")
    for plan in plans:
        print(f"- {plan.subject}: {len(plan.checklist_items)} tasks")


def print_dry_run_plan(plans: list[IssuePlan], parent_issue_id: str) -> None:
    print("DRY RUN: local preview only; no Redmine login, lookup, or create request will be sent.")
    print(f"Parent issue: #{parent_issue_id}")
    for plan in plans:
        print(f"- Section: {plan.subject}")
        for index, item in enumerate(plan.checklist_items, start=1):
            print(f"  - Task: {truncate_subject(f'{index:02d}. {item}')}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Create Redmine child issues and tasks from JSON section plan."
    )
    parser.add_argument(
        "--ID",
        dest="issue_id",
        required=True,
        help="父議題 ID（必須）",
    )
    parser.add_argument(
        "--SECTION_PLAN",
        type=Path,
        required=True,
        help="JSON 配置檔案路徑（必須）",
    )
    parser.add_argument(
        "--markdown",
        type=Path,
        help="Markdown 來源檔案路徑（不指定則使用 JSON 設定）",
    )
    parser.add_argument(
        "--id-record",
        type=Path,
        help="建立/略過議題後輸出的 Redmine ID 對照 md",
    )
    parser.add_argument(
        "--tracker",
        default=DEFAULT_TRACKER_NAME,
        help=f"Tracker 名稱，預設 {DEFAULT_TRACKER_NAME}",
    )
    parser.add_argument("--no-id-record", action="store_true", help="實際建立後不輸出 ID 對照 md")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="只做本地預覽，不登入 Redmine，也不建立議題",
    )
    parser.add_argument(
        "--plan-only",
        action="store_true",
        help="只解析 Markdown 並列出將建立的項目，不登入 Redmine",
    )
    parser.add_argument(
        "--allow-duplicate",
        action="store_true",
        help="允許建立同名子議題/task",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    try:
        # Load JSON config
        config_path = args.SECTION_PLAN.resolve()
        parent_issue_id, section_plan = load_section_plan_from_json(config_path)

        # CLI --ID takes precedence over JSON config
        if args.issue_id:
            parent_issue_id = args.issue_id

        # Determine Markdown path
        if args.markdown:
            markdown_path = args.markdown.resolve()
        else:
            # Default to current directory + robot_v1/robot_v1.md
            markdown_path = Path(__file__).resolve().parent / "robot_v1" / "robot_v1.md"

        # Parse Markdown with section plan
        plans = parse_markdown_with_section_plan(markdown_path, section_plan)

        if args.dry_run:
            print_dry_run_plan(plans, parent_issue_id)
            return 0

        print_plan(plans, parent_issue_id)

        if args.plan_only:
            return 0

        # Determine ID record output path
        if not args.no_id_record:
            if args.id_record:
                id_record_path = args.id_record.resolve()
            else:
                id_record_path = Path(__file__).resolve().parent / "redmine_task_ids.md"

        # Create issues via Redmine
        username, password = get_credentials()
        with requests.Session() as session:
            login(session, username, password)
            records = create_issues_from_plan(
                session=session,
                plans=plans,
                parent_issue_id=parent_issue_id,
                tracker_name=args.tracker,
                markdown_path=markdown_path,
                config_path=config_path,
                allow_duplicate=args.allow_duplicate,
                dry_run=args.dry_run,
            )
            if not args.no_id_record:
                write_id_record(records, parent_issue_id, markdown_path, config_path, id_record_path)

    except (OSError, requests.RequestException, RedmineError, ValueError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
