"""Acceptance tests traced to requirements that are easy to miss in unit tests."""

from __future__ import annotations

import ast
import contextlib
import io
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from main import Quiz, QuizGame


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class KanbanAcceptanceTests(unittest.TestCase):
    def make_game(self, path: Path, answers: list[str] | None = None) -> QuizGame:
        values = iter(answers or [])
        with contextlib.redirect_stdout(io.StringIO()):
            return QuizGame(path, lambda _prompt: next(values))

    def test_project_root_contains_required_deliverables(self) -> None:
        for name in ("main.py", "state.json", "README.md", ".gitignore"):
            with self.subTest(name=name):
                self.assertTrue((PROJECT_ROOT / name).is_file())

    def test_committed_state_file_has_five_valid_quizzes(self) -> None:
        raw = (PROJECT_ROOT / "state.json").read_text(encoding="utf-8")
        state = json.loads(raw)
        self.assertEqual(set(state), {"quizzes", "best_score"})
        self.assertGreaterEqual(len(state["quizzes"]), 5)
        for item in state["quizzes"]:
            with self.subTest(question=item.get("question")):
                quiz = Quiz.from_dict(item)
                self.assertEqual(len(quiz.choices), 4)
                self.assertIn(quiz.answer, range(1, 5))

    def test_main_module_uses_required_python_constructs(self) -> None:
        tree = ast.parse((PROJECT_ROOT / "main.py").read_text(encoding="utf-8"))
        classes = {node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)}
        node_types = {type(node) for node in ast.walk(tree)}
        self.assertTrue({"Quiz", "QuizGame"}.issubset(classes))
        for required in (ast.Assign, ast.Call, ast.If, ast.For, ast.While, ast.FunctionDef, ast.List, ast.Dict):
            with self.subTest(construct=required.__name__):
                self.assertIn(required, node_types)

    def test_quiz_game_exposes_separate_feature_methods(self) -> None:
        required_methods = (
            "read_number",
            "read_text",
            "display_menu",
            "play_quiz",
            "add_quiz",
            "list_quizzes",
            "show_best_score",
            "save_state",
            "load_state",
        )
        for method in required_methods:
            with self.subTest(method=method):
                self.assertTrue(callable(getattr(QuizGame, method, None)))

    def test_normal_menu_exit_saves_current_data(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "state.json"
            game = self.make_game(path, ["5"])
            game.quizzes.append(Quiz("종료 전 데이터", ["가", "나", "다", "라"], 1))
            with contextlib.redirect_stdout(io.StringIO()):
                game.run()
            restarted = self.make_game(path)
            self.assertEqual(restarted.quizzes[-1].question, "종료 전 데이터")

    def test_corrupt_state_reports_recovery_and_writes_valid_json(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "state.json"
            path.write_text("not-json", encoding="utf-8")
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                game = QuizGame(path, lambda _prompt: "5")
            self.assertIn("읽을 수 없습니다", output.getvalue())
            self.assertIn("복구", output.getvalue())
            self.assertGreaterEqual(len(game.quizzes), 5)
            json.loads(path.read_text(encoding="utf-8"))

    def test_score_is_calculated_for_arbitrary_quiz_count(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "state.json"
            game = self.make_game(path, ["1", "2", "1"])
            game.quizzes = [
                Quiz("q1", ["1", "2", "3", "4"], 1),
                Quiz("q2", ["1", "2", "3", "4"], 2),
                Quiz("q3", ["1", "2", "3", "4"], 4),
            ]
            with contextlib.redirect_stdout(io.StringIO()):
                game.play_quiz()
            self.assertEqual(game.best_score, {"score": 67, "correct": 2, "total": 3})

    def test_program_runs_as_a_real_terminal_process(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            sandbox = Path(directory)
            shutil.copy2(PROJECT_ROOT / "main.py", sandbox / "main.py")
            result = subprocess.run(
                [sys.executable, "main.py"],
                input="5\n",
                text=True,
                capture_output=True,
                cwd=sandbox,
                timeout=10,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("Python 기초 퀴즈 게임", result.stdout)
            self.assertIn("게임을 종료", result.stdout)
            self.assertTrue((sandbox / "state.json").is_file())


class DocumentationAcceptanceTests(unittest.TestCase):
    def test_readme_contains_every_required_section(self) -> None:
        readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8")
        required_topics = (
            "프로젝트 개요",
            "퀴즈 주제",
            "선정 이유",
            "실행 방법",
            "기능 목록",
            "파일 구조",
            "state.json",
        )
        for topic in required_topics:
            with self.subTest(topic=topic):
                self.assertIn(topic, readme)

    def test_learning_guide_covers_python_oop_json_and_git_cards(self) -> None:
        guide = (PROJECT_ROOT / "LEARNING_GUIDE.md").read_text(encoding="utf-8")
        required_terms = (
            "변수", "int", "str", "bool", "list", "dict",
            "if", "elif", "else", "for", "while", "함수", "매개변수", "return",
            "클래스", "객체", "__init__", "self", "attribute", "method",
            "파일", "with", "JSON", "try", "except",
            "Git", "GitHub", "git init", "git add", "git commit", "git push",
            "git pull", "git checkout", "git clone", "브랜치", "merge",
        )
        for term in required_terms:
            with self.subTest(term=term):
                self.assertIn(term, guide)


if __name__ == "__main__":
    unittest.main()
