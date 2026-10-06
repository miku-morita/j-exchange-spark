"""架空の予定とメンバーで、詳細表示・共有メモの権限を確認する。"""
import ast
import os
from pathlib import Path
import tempfile
import unittest
from datetime import date, datetime, timedelta, timezone

import pandas as pd
from streamlit.testing.v1 import AppTest


class CalendarTest(unittest.TestCase):
    def setUp(self):
        self.original = Path.cwd()
        self.source = (self.original / "app.py").read_text(encoding="utf-8")
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "app.py").write_text(self.source, encoding="utf-8")
        (self.root / "japan_holidays.csv").write_bytes((self.original / "japan_holidays.csv").read_bytes())
        os.chdir(self.root)
        self.label = "【学生交流会】 2099年1月10日(土) 13:00-15:00"
        pd.DataFrame([{"日程": self.label, "活動日": "2099-01-10", "回答期限": "2099-01-05"}]).to_csv("target_dates.csv", index=False)
        pd.DataFrame([
            {"名前": "参加者A", "メールアドレス": "a@example.invalid", "ホスト権限": False, "初回パスワード変更済み": True},
            {"名前": "運営B", "メールアドレス": "b@example.invalid", "ホスト権限": True, "初回パスワード変更済み": True},
        ]).to_csv("members_data.csv", index=False)
        pd.DataFrame([
            {"名前": "参加者A", self.label: "× (欠席)"},
            {"名前": "参加者A", self.label: "〇 (参加)"},
            {"名前": "運営B", self.label: "△ (未定)"},
            {"名前": "削除済みメンバー", self.label: "〇 (参加)"},
        ]).to_csv("schedule_data.csv", index=False)

    def tearDown(self):
        os.chdir(self.original)
        self.temp.cleanup()

    def app(self, super_admin=False, host=False):
        at = AppTest.from_file(str(self.root / "app.py"), default_timeout=20)
        for key, value in {
            "logged_in": True, "is_super": super_admin, "is_host": super_admin or host,
            "user_name": "統括管理者" if super_admin else ("運営B" if host else "参加者A"),
            "user_email": "b@example.invalid" if host else "a@example.invalid",
            "must_change_password": False, "page": "🏠 ホーム", "calendar_month": date(2099, 1, 1),
        }.items():
            at.session_state[key] = value
        at.run()
        self.assertFalse(at.exception)
        self.assertEqual(at.title[0].value, "活動カレンダー")
        self.assertEqual(at.button(key=f"calendar-event-{self.label}").label, "学生交流会")
        at.button(key=f"calendar-event-{self.label}").click().run()
        self.assertFalse(at.exception)
        return at

    def test_details_memo_persistence_and_read_only_roles(self):
        at = self.app(super_admin=True)
        self.assertTrue(any("参加予定者（1人）" == s.value for s in at.subheader))
        self.assertTrue(any(t.value == "参加者A" for t in at.text))
        self.assertTrue(any("13:00〜15:00" == c.value for c in at.caption))
        self.assertFalse(any(t.value == self.label for t in at.text))
        at.text_area(key=f"memo_{self.label}").set_value("集合：正門。学生証を持参。")
        next(b for b in at.button if b.label == "共有メモを保存する").click().run()
        self.assertFalse(at.exception)
        saved = pd.read_csv("target_dates.csv").iloc[0]
        self.assertEqual(saved["共有メモ"], "集合：正門。学生証を持参。")
        self.assertEqual(saved["活動日"], "2099-01-10")
        for host in (False, True):
            viewer = self.app(host=host)
            self.assertFalse(viewer.text_area)
            self.assertFalse(any(b.label == "共有メモを保存する" for b in viewer.button))
            self.assertTrue(any(t.value == "集合：正門。学生証を持参。" for t in viewer.text))

    def test_memo_save_rejects_non_super_admin(self):
        from types import SimpleNamespace
        node = next(n for n in ast.parse(self.source).body if isinstance(n, ast.FunctionDef) and n.name == "save_activity_memo")
        namespace = {"st": SimpleNamespace(session_state={"logged_in": True, "is_super": False})}
        exec(compile(ast.Module(body=[node], type_ignores=[]), "<permission-test>", "exec"), namespace)
        before = Path("target_dates.csv").read_bytes()
        with self.assertRaises(PermissionError):
            namespace["save_activity_memo"](self.label, "unauthorized")
        self.assertEqual(Path("target_dates.csv").read_bytes(), before)

    def test_weekend_and_official_holiday_colors(self):
        at = self.app(super_admin=True)
        at.session_state["selected_activity"] = None
        at.session_state["calendar_month"] = date(2026, 10, 1)
        at.run()
        self.assertFalse(at.exception)
        markup = "\n".join(m.value for m in at.markdown)
        self.assertIn('calendar-date calendar-blue">3</div>', markup)
        self.assertIn('calendar-date calendar-red">4</div>', markup)
        self.assertIn('calendar-date calendar-red">12・祝</div>', markup)
        at.session_state["calendar_month"] = date(2026, 5, 1)
        at.run()
        self.assertFalse(at.exception)
        markup = "\n".join(m.value for m in at.markdown)
        self.assertIn('calendar-date calendar-red">6・祝</div>', markup)

    def test_today_panel_is_independent_of_displayed_month(self):
        today = datetime.now(timezone(timedelta(hours=9))).date()
        label = "【今日の交流会】 10:00-11:00"
        df = pd.read_csv("target_dates.csv")
        df = pd.concat([df, pd.DataFrame([{"日程": label, "活動日": today.isoformat()}])], ignore_index=True)
        df.to_csv("target_dates.csv", index=False)
        at = self.app(super_admin=True)
        today_buttons = [b for b in at.button if b.key and b.key.startswith("today-event-")]
        self.assertEqual([b.label for b in today_buttons], ["今日の交流会"])
        at.button(key=f"today-event-{label}").click().run()
        self.assertFalse(at.exception)
        self.assertTrue(any(s.value == "今日の交流会" for s in at.subheader))
        self.assertTrue(any(c.value == "10:00〜11:00" for c in at.caption))


if __name__ == "__main__":
    unittest.main()
