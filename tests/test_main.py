import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from main import Quiz, QuizGame, create_default_quizzes


class QuizTests(unittest.TestCase):
    def test_quiz_validates_and_checks_answer(self) -> None:
        quiz = Quiz(" 문제 ", [" 하나 ", "둘", "셋", "넷"], 2)
        self.assertEqual(quiz.question, "문제")
        self.assertEqual(quiz.choices[0], "하나")
        self.assertTrue(quiz.is_correct(2))
        self.assertFalse(quiz.is_correct(1))

    def test_quiz_rejects_invalid_data(self) -> None:
        with self.assertRaises(ValueError):
            Quiz("", ["1", "2", "3", "4"], 1)
        with self.assertRaises(ValueError):
            Quiz("문제", ["1", "2"], 1)
        with self.assertRaises(ValueError):
            Quiz("문제", ["1", "2", "3", "4"], 5)

    def test_default_quizzes_meet_requirements(self) -> None:
        quizzes = create_default_quizzes()
        self.assertGreaterEqual(len(quizzes), 5)
        self.assertTrue(all(len(quiz.choices) == 4 for quiz in quizzes))


class QuizGameTests(unittest.TestCase):
    def make_game(self, path: Path, answers: list[str] | None = None) -> QuizGame:
        values = iter(answers or [])
        with contextlib.redirect_stdout(io.StringIO()):
            return QuizGame(path, lambda _prompt: next(values))

    def test_missing_file_uses_defaults_and_round_trips(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "state.json"
            game = self.make_game(path)
            self.assertEqual(len(game.quizzes), 5)
            game.best_score = {"score": 80, "correct": 4, "total": 5}
            self.assertTrue(game.save_state())

            loaded = self.make_game(path)
            self.assertEqual(len(loaded.quizzes), 5)
            self.assertEqual(loaded.best_score["score"], 80)

    def test_corrupt_file_recovers_and_rewrites_state(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "state.json"
            path.write_text("{not json", encoding="utf-8")
            game = self.make_game(path)
            self.assertEqual(len(game.quizzes), 5)
            saved = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(len(saved["quizzes"]), 5)

    def test_invalid_quiz_schema_recovers(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "state.json"
            path.write_text(
                json.dumps(
                    {
                        "quizzes": [
                            {"question": 123, "choices": ["1", "2", "3", "4"], "answer": 1}
                        ],
                        "best_score": None,
                    }
                ),
                encoding="utf-8",
            )
            game = self.make_game(path)
            self.assertEqual(len(game.quizzes), 5)

    def test_number_input_retries_empty_text_and_range_errors(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            answers = iter([" ", "abc", "9", " 3 "])
            game = self.make_game(
                Path(directory) / "state.json", list(answers)
            )
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                result = game.read_number("선택: ", 1, 5)
            self.assertEqual(result, 3)
            self.assertIn("값을 입력하세요", output.getvalue())
            self.assertIn("숫자를 입력하세요", output.getvalue())
            self.assertIn("1-5 사이", output.getvalue())

    def test_add_quiz_saves_it(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "state.json"
            game = self.make_game(path, ["새 문제", "가", "나", "다", "라", "2"])
            with contextlib.redirect_stdout(io.StringIO()):
                game.add_quiz()
            loaded = self.make_game(path)
            self.assertEqual(len(loaded.quizzes), 6)
            self.assertEqual(loaded.quizzes[-1].answer, 2)

    def test_play_updates_best_score(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "state.json"
            game = self.make_game(path, ["1", "3", "2", "3", "3"])
            with contextlib.redirect_stdout(io.StringIO()):
                game.play_quiz()
            self.assertEqual(game.best_score, {"score": 100, "correct": 5, "total": 5})
            self.assertTrue(path.exists())

    def test_empty_quiz_collection_is_handled(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            game = self.make_game(Path(directory) / "state.json")
            game.quizzes = []
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                game.play_quiz()
                game.list_quizzes()
            self.assertEqual(output.getvalue().count("등록된 퀴즈가 없습니다"), 2)

    def test_eof_during_run_saves_and_exits(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "state.json"

            def raise_eof(_prompt: str) -> str:
                raise EOFError

            game = self.make_game(path)
            game.input = raise_eof
            with contextlib.redirect_stdout(io.StringIO()):
                game.run()
            self.assertTrue(path.exists())


if __name__ == "__main__":
    unittest.main()
