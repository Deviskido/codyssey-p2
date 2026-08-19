"""기능 브랜치에서 개발한 도메인 기능 테스트."""

from __future__ import annotations

import contextlib
import io
import tempfile
import unittest
from pathlib import Path

from main import Quiz, QuizCollection, QuizGame, QuizSearch, ScoreCalculator


class QuizSearchTests(unittest.TestCase):
    def setUp(self) -> None:
        self.quizzes = [
            Quiz("Python 리스트 문제", ["tuple", "LIST", "dict", "set"], 2),
            Quiz("수도 문제", ["서울", "부산", "도쿄", "파리"], 1),
        ]

    def test_find_searches_questions_and_choices_case_insensitively(self) -> None:
        self.assertEqual(QuizSearch.find(self.quizzes, " python "), [self.quizzes[0]])
        self.assertEqual(QuizSearch.find(self.quizzes, "list"), [self.quizzes[0]])
        self.assertEqual(QuizSearch.find(self.quizzes, "서울"), [self.quizzes[1]])

    def test_find_returns_empty_list_for_blank_or_unknown_keyword(self) -> None:
        self.assertEqual(QuizSearch.find(self.quizzes, "   "), [])
        self.assertEqual(QuizSearch.find(self.quizzes, "없는 내용"), [])

    def test_game_searches_its_current_quizzes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                game = QuizGame(Path(directory) / "state.json")
            game.quizzes = self.quizzes
            self.assertEqual(game.search_quizzes("수도"), [self.quizzes[1]])


class ScoreCalculatorTests(unittest.TestCase):
    def test_calculate_returns_rounded_percentage(self) -> None:
        self.assertEqual(ScoreCalculator.calculate(0, 5), 0)
        self.assertEqual(ScoreCalculator.calculate(2, 3), 67)
        self.assertEqual(ScoreCalculator.calculate(5, 5), 100)

    def test_calculate_rejects_invalid_counts_and_types(self) -> None:
        invalid_values = (
            (-1, 5),
            (6, 5),
            (0, 0),
            (True, 5),
            (1, 2.0),
        )
        for correct, total in invalid_values:
            with self.subTest(correct=correct, total=total), self.assertRaises(ValueError):
                ScoreCalculator.calculate(correct, total)


class QuizCollectionTests(unittest.TestCase):
    def test_from_data_builds_quiz_objects(self) -> None:
        data = [
            {
                "question": "문제",
                "choices": ["하나", "둘", "셋", "넷"],
                "answer": 3,
            }
        ]
        quizzes = QuizCollection.from_data(data)
        self.assertEqual(len(quizzes), 1)
        self.assertIsInstance(quizzes[0], Quiz)
        self.assertEqual(quizzes[0].answer, 3)

    def test_from_data_accepts_empty_list_and_rejects_other_shapes(self) -> None:
        self.assertEqual(QuizCollection.from_data([]), [])
        for value in (None, {}, "quizzes", 1):
            with self.subTest(value=value), self.assertRaises(ValueError):
                QuizCollection.from_data(value)


if __name__ == "__main__":
    unittest.main()
