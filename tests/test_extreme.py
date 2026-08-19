"""Kanban requirements exercised with boundary, recovery, and end-to-end tests."""

from __future__ import annotations

import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from main import Quiz, QuizGame, create_default_quizzes


class ExtremeTestCase(unittest.TestCase):
    def make_game(self, path: Path, answers: list[str] | None = None) -> QuizGame:
        values = iter(answers or [])
        with contextlib.redirect_stdout(io.StringIO()):
            return QuizGame(path, lambda _prompt: next(values))

    def capture(self, function, *args) -> str:
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            function(*args)
        return output.getvalue()


class QuizExtremeTests(ExtremeTestCase):
    def test_every_invalid_answer_type_and_boundary_is_rejected(self) -> None:
        for answer in (-100, -1, 0, 5, 100, True, False, 1.0, "1", None):
            with self.subTest(answer=answer), self.assertRaises(ValueError):
                Quiz("question", ["a", "b", "c", "d"], answer)

    def test_blank_questions_and_choices_are_rejected(self) -> None:
        for question in ("", " ", "\t\n"):
            with self.subTest(question=repr(question)), self.assertRaises(ValueError):
                Quiz(question, ["a", "b", "c", "d"], 1)
        for position in range(4):
            choices = ["a", "b", "c", "d"]
            choices[position] = "  "
            with self.subTest(position=position), self.assertRaises(ValueError):
                Quiz("question", choices, 1)

    def test_choice_count_must_be_exactly_four(self) -> None:
        for choices in ([], ["a"], ["a", "b", "c"], ["a", "b", "c", "d", "e"]):
            with self.subTest(count=len(choices)), self.assertRaises(ValueError):
                Quiz("question", choices, 1)

    def test_question_and_choices_require_declared_container_types(self) -> None:
        for question in (None, 123, [], {}):
            with self.subTest(question=question), self.assertRaises(ValueError):
                Quiz(question, ["a", "b", "c", "d"], 1)
        for choices in (None, "abcd", ("a", "b", "c", "d"), {"a", "b", "c", "d"}):
            with self.subTest(choices=choices), self.assertRaises(ValueError):
                Quiz("question", choices, 1)

    def test_all_valid_answer_boundaries_work(self) -> None:
        for answer in range(1, 5):
            quiz = Quiz("question", ["a", "b", "c", "d"], answer)
            for guess in range(1, 5):
                self.assertEqual(quiz.is_correct(guess), guess == answer)

    def test_serialization_round_trip_preserves_unicode(self) -> None:
        original = Quiz("한글 문제 🐍", ["가", "나", "다", "라"], 4)
        restored = Quiz.from_dict(original.to_dict())
        self.assertEqual(restored.question, original.question)
        self.assertEqual(restored.choices, original.choices)
        self.assertEqual(restored.answer, original.answer)

    def test_from_dict_rejects_non_mapping_and_missing_fields(self) -> None:
        for value in (None, [], "quiz", 1):
            with self.subTest(value=value), self.assertRaises(ValueError):
                Quiz.from_dict(value)
        for missing in ("question", "choices", "answer"):
            data = {"question": "q", "choices": ["1", "2", "3", "4"], "answer": 1}
            del data[missing]
            with self.subTest(missing=missing), self.assertRaises(KeyError):
                Quiz.from_dict(data)

    def test_display_prints_number_question_and_all_four_choices(self) -> None:
        quiz = Quiz("question", ["alpha", "beta", "gamma", "delta"], 1)
        numbered = self.capture(quiz.display, 7)
        self.assertIn("[문제 7] question", numbered)
        for index, choice in enumerate(quiz.choices, 1):
            self.assertIn(f"{index}. {choice}", numbered)
        self.assertIn("[문제] question", self.capture(quiz.display))

    def test_default_dataset_is_independent_and_fully_valid(self) -> None:
        first = create_default_quizzes()
        second = create_default_quizzes()
        self.assertGreaterEqual(len(first), 5)
        self.assertEqual(len({quiz.question for quiz in first}), len(first))
        self.assertTrue(all(1 <= quiz.answer <= 4 for quiz in first))
        self.assertTrue(all(len(quiz.choices) == 4 for quiz in first))
        self.assertIsNot(first[0], second[0])


class InputExtremeTests(ExtremeTestCase):
    def test_number_input_retries_every_kanban_error_then_accepts_boundary(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            game = self.make_game(
                Path(directory) / "state.json",
                ["", "   ", "abc", "1.0", "-1", "0", "5", " 4 "],
            )
            output = self.capture(game.read_number, "answer: ", 1, 4)
            self.assertGreaterEqual(output.count("값을 입력하세요"), 2)
            self.assertGreaterEqual(output.count("숫자를 입력하세요"), 2)
            self.assertGreaterEqual(output.count("1-4 사이"), 3)

    def test_number_input_accepts_both_inclusive_boundaries(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            low = self.make_game(Path(directory) / "a.json", ["1"])
            high = self.make_game(Path(directory) / "b.json", ["5"])
            self.assertEqual(low.read_number("", 1, 5), 1)
            self.assertEqual(high.read_number("", 1, 5), 5)

    def test_text_input_retries_whitespace_and_strips_result(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            game = self.make_game(Path(directory) / "state.json", ["", " \t ", "  content  "])
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                result = game.read_text("text: ")
            self.assertEqual(result, "content")
            self.assertEqual(output.getvalue().count("내용을 입력하세요"), 2)


class PersistenceExtremeTests(ExtremeTestCase):
    def test_saved_json_is_utf8_has_required_schema_and_no_temp_file(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "nested" / "state.json"
            game = self.make_game(path)
            game.quizzes = [Quiz("한글 🐍", ["가", "나", "다", "라"], 1)]
            game.best_score = {"score": 100, "correct": 1, "total": 1}
            self.assertTrue(game.save_state())
            raw = path.read_text(encoding="utf-8")
            data = json.loads(raw)
            self.assertIn("한글 🐍", raw)
            self.assertEqual(set(data), {"quizzes", "best_score"})
            self.assertEqual(set(data["quizzes"][0]), {"question", "choices", "answer"})
            self.assertFalse(path.with_suffix(".json.tmp").exists())

    def test_all_invalid_top_level_shapes_recover_to_defaults(self) -> None:
        invalid_values = (None, [], "text", 42, {}, {"quizzes": None})
        for value in invalid_values:
            with self.subTest(value=value), tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / "state.json"
                path.write_text(json.dumps(value), encoding="utf-8")
                game = self.make_game(path)
                self.assertGreaterEqual(len(game.quizzes), 5)
                self.assertIsNone(game.best_score)

    def test_invalid_best_score_records_recover_to_defaults(self) -> None:
        invalid_scores = (
            -1,
            101,
            True,
            "100",
            [],
            {},
            {"score": -1, "correct": 0, "total": 1},
            {"score": 101, "correct": 1, "total": 1},
            {"score": 50, "correct": 2, "total": 1},
            {"score": 50, "correct": True, "total": 1},
        )
        for score in invalid_scores:
            with self.subTest(score=score), tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / "state.json"
                path.write_text(json.dumps({"quizzes": [], "best_score": score}), encoding="utf-8")
                game = self.make_game(path)
                self.assertGreaterEqual(len(game.quizzes), 5)
                self.assertIsNone(game.best_score)

    def test_legacy_integer_best_score_loads(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "state.json"
            path.write_text(json.dumps({"quizzes": [], "best_score": 80}), encoding="utf-8")
            game = self.make_game(path)
            self.assertEqual(game.best_score, {"score": 80, "correct": 80, "total": 0})

    def test_valid_state_survives_multiple_restart_cycles(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "state.json"
            game = self.make_game(path)
            game.quizzes.append(Quiz("persistent", ["1", "2", "3", "4"], 2))
            game.best_score = {"score": 80, "correct": 4, "total": 5}
            for _ in range(5):
                self.assertTrue(game.save_state())
                game = self.make_game(path)
                self.assertEqual(game.quizzes[-1].question, "persistent")
                self.assertEqual(game.best_score["score"], 80)

    def test_save_os_error_returns_false_and_removes_temporary_file(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "state.json"
            game = self.make_game(path)
            temporary = path.with_suffix(".json.tmp")
            temporary.write_text("partial", encoding="utf-8")
            with patch("main.os.replace", side_effect=OSError("disk failure")):
                output = self.capture(game.save_state)
            self.assertIn("disk failure", output)
            self.assertFalse(temporary.exists())


class FeatureExtremeTests(ExtremeTestCase):
    def test_menu_contains_exactly_all_five_required_actions(self) -> None:
        output = self.capture(QuizGame.display_menu)
        for number in range(1, 6):
            self.assertIn(f"{number}.", output)
        for label in ("풀기", "추가", "목록", "점수", "종료"):
            self.assertIn(label, output)

    def test_list_includes_total_number_and_every_question(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            game = self.make_game(Path(directory) / "state.json")
            output = self.capture(game.list_quizzes)
            self.assertIn(f"총 {len(game.quizzes)}개", output)
            for index, quiz in enumerate(game.quizzes, 1):
                self.assertIn(f"[{index}] {quiz.question}", output)

    def test_add_retries_blank_fields_and_invalid_answer_then_persists(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "state.json"
            answers = ["", " question ", "", "a", "b", "c", "d", "abc", "0", "5", " 4 "]
            game = self.make_game(path, answers)
            self.capture(game.add_quiz)
            loaded = self.make_game(path)
            added = loaded.quizzes[-1]
            self.assertEqual((added.question, added.choices, added.answer), ("question", ["a", "b", "c", "d"], 4))

    def test_play_all_wrong_reports_answers_and_zero_score(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "state.json"
            game = self.make_game(path)
            wrong = [str(quiz.answer % 4 + 1) for quiz in game.quizzes]
            game.input = lambda _prompt: wrong.pop(0)
            output = self.capture(game.play_quiz)
            self.assertEqual(game.best_score, {"score": 0, "correct": 0, "total": 5})
            self.assertEqual(output.count("오답입니다"), 5)
            self.assertIn("0점", output)

    def test_lower_and_equal_scores_do_not_replace_best(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            game = self.make_game(Path(directory) / "state.json")
            game.best_score = {"score": 100, "correct": 5, "total": 5}
            game.input = lambda _prompt: "1"
            self.capture(game.play_quiz)
            self.assertEqual(game.best_score, {"score": 100, "correct": 5, "total": 5})

    def test_score_display_handles_none_full_record_and_legacy_record(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            game = self.make_game(Path(directory) / "state.json")
            self.assertIn("기록이 없습니다", self.capture(game.show_best_score))
            game.best_score = {"score": 80, "correct": 4, "total": 5}
            full = self.capture(game.show_best_score)
            self.assertIn("80점", full)
            self.assertIn("5문제 중 4문제", full)
            game.best_score = {"score": 70, "correct": 70, "total": 0}
            self.assertIn("70점", self.capture(game.show_best_score))

    def test_full_menu_session_adds_lists_plays_scores_and_exits(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "state.json"
            session = [
                "2", "extra", "one", "two", "three", "four", "2",
                "3",
                "1", "1", "3", "2", "3", "3", "2",
                "4",
                "5",
            ]
            game = self.make_game(path, session)
            output = self.capture(game.run)
            self.assertIn("extra", output)
            self.assertIn("100점", output)
            self.assertIn("게임을 종료", output)
            restarted = self.make_game(path)
            self.assertEqual(restarted.quizzes[-1].question, "extra")
            self.assertEqual(restarted.best_score["score"], 100)

    def test_eof_and_keyboard_interrupt_each_save_current_data(self) -> None:
        for exception in (EOFError, KeyboardInterrupt):
            with self.subTest(exception=exception.__name__), tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / "state.json"
                game = self.make_game(path)
                game.quizzes.append(Quiz("before interrupt", ["1", "2", "3", "4"], 1))

                def stop(_prompt: str, error=exception) -> str:
                    raise error

                game.input = stop
                output = self.capture(game.run)
                self.assertIn("안전하게 종료", output)
                restarted = self.make_game(path)
                self.assertEqual(restarted.quizzes[-1].question, "before interrupt")


if __name__ == "__main__":
    unittest.main()
