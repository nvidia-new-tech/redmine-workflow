"""Create a weekly Redmine subtask under issue #36463."""

from __future__ import annotations

import argparse
import getpass
import os
import re
import sys
from dataclasses import dataclass
from datetime import date, timedelta
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


BASE_URL = "http://redmine.mirle.com.tw"
PROJECT_IDENTIFIER = "9bc_weeklyreport"
PARENT_ISSUE_ID = "36463"
TRACKER_ID = "6"
PROJECT_ID = "563"
ASSIGN_TO_ME_USER_ID = "318"


class RedmineError(RuntimeError):
    """Raised when Redmine cannot complete the requested action."""


@dataclass(frozen=True)
class WeeklySubtask:
    subject: str
    start_date: date
    due_date: date


def parse_week_code(week_code: str, year: int) -> WeeklySubtask:
    normalized = week_code.strip().upper()
    if not re.fullmatch(r"W\d{4}", normalized):
        raise ValueError("週別格式需為 WMMDD，例如 W0803")

    month = int(normalized[1:3])
    day = int(normalized[3:5])
    start_date = date(year, month, day)
    if start_date.weekday() != 0:
        raise ValueError(f"{start_date.isoformat()} 不是週一")

    return WeeklySubtask(
        subject=normalized,
        start_date=start_date,
        due_date=start_date + timedelta(days=4),
    )


def get_credentials() -> tuple[str, str]:
    username = os.environ.get("REDMINE_USERNAME") or input("Redmine username: ").strip()
    password = os.environ.get("REDMINE_PASSWORD") or getpass.getpass("Redmine password: ")
    if not username or not password:
        raise ValueError("Redmine username/password 不可為空")
    return username, password


def find_input_value(soup: BeautifulSoup, name: str) -> str:
    element = soup.find("input", {"name": name})
    if element is None:
        raise RedmineError(f"找不到表單欄位: {name}")
    value = element.get("value")
    if value is None:
        raise RedmineError(f"表單欄位沒有值: {name}")
    return value


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


def fetch_new_issue_form(session: requests.Session) -> tuple[str, str]:
    form_url = (
        f"/projects/{PROJECT_IDENTIFIER}/issues/new"
        f"?back_url=%2Fissues%2F{PARENT_ISSUE_ID}"
        f"&issue%5Bparent_issue_id%5D={PARENT_ISSUE_ID}"
        f"&issue%5Btracker_id%5D={TRACKER_ID}"
    )
    response = session.get(urljoin(BASE_URL, form_url), timeout=20)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    form = soup.find("form", {"id": "issue-form"})
    if form is None:
        raise RedmineError("找不到 Redmine issue 建立表單")

    token = find_input_value(BeautifulSoup(str(form), "html.parser"), "authenticity_token")
    action = form.get("action")
    if not action:
        raise RedmineError("Issue 建立表單缺少 action")
    return urljoin(BASE_URL, action), token


def subtask_exists(session: requests.Session, subject: str) -> bool:
    response = session.get(urljoin(BASE_URL, f"/issues/{PARENT_ISSUE_ID}"), timeout=20)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    for link in soup.find_all("a", href=re.compile(r"^/issues/\d+$")):
        text = " ".join(link.parent.get_text(" ", strip=True).split()) if link.parent else ""
        if f": {subject}" in text:
            return True
    return False


def create_subtask(
    session: requests.Session,
    subtask: WeeklySubtask,
    allow_duplicate: bool,
    dry_run: bool,
) -> str:
    if not allow_duplicate and subtask_exists(session, subtask.subject):
        raise RedmineError(f"子任務 {subtask.subject} 已存在，未重複建立")

    create_url, token = fetch_new_issue_form(session)
    payload = {
        "utf8": "✓",
        "authenticity_token": token,
        "form_update_triggered_by": "",
        "back_url": f"/issues/{PARENT_ISSUE_ID}",
        "issue[is_private]": "0",
        "issue[project_id]": PROJECT_ID,
        "issue[tracker_id]": TRACKER_ID,
        "issue[subject]": subtask.subject,
        "issue[description]": "",
        "issue[status_id]": "1",
        "was_default_status": "1",
        "issue[priority_id]": "2",
        "issue[assigned_to_id]": ASSIGN_TO_ME_USER_ID,
        "issue[parent_issue_id]": PARENT_ISSUE_ID,
        "issue[start_date]": subtask.start_date.isoformat(),
        "issue[due_date]": subtask.due_date.isoformat(),
        "issue[estimated_hours]": "",
        "issue[done_ratio]": "0",
        "issue[watcher_user_ids][]": "",
        "commit": "Create",
    }

    if dry_run:
        return (
            f"DRY RUN: would create {subtask.subject} "
            f"under #{PARENT_ISSUE_ID}, assigned to me, "
            f"start {subtask.start_date.isoformat()}, due {subtask.due_date.isoformat()}"
        )

    response = session.post(create_url, data=payload, timeout=20, allow_redirects=True)
    response.raise_for_status()
    if "/issues/new" in response.url or "errorExplanation" in response.text:
        soup = BeautifulSoup(response.text, "html.parser")
        errors = [item.get_text(" ", strip=True) for item in soup.select("#errorExplanation li")]
        raise RedmineError("建立子任務失敗: " + "; ".join(errors or ["Redmine 回到新增頁面"]))

    match = re.search(r"/issues/(\d+)", response.url)
    if match:
        return f"Created Task #{match.group(1)}: {subtask.subject}"
    return f"Created subtask: {subtask.subject} ({response.url})"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Create a weekly Redmine subtask under Task #36463.")
    parser.add_argument("week_code", help="週一日期代碼，例如 W0803")
    parser.add_argument("--year", type=int, default=date.today().year, help="年份，預設為今年")
    parser.add_argument("--dry-run", action="store_true", help="只登入並檢查，不實際建立子任務")
    parser.add_argument("--allow-duplicate", action="store_true", help="允許建立同名子任務")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    try:
        subtask = parse_week_code(args.week_code, args.year)
        username, password = get_credentials()
        with requests.Session() as session:
            login(session, username, password)
            result = create_subtask(session, subtask, args.allow_duplicate, args.dry_run)
        print(result)
    except (requests.RequestException, RedmineError, ValueError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())