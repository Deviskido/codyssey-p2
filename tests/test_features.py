"""기능 브랜치에서 개발한 도메인 기능 테스트."""

from __future__ import annotations

import contextlib
import io
import tempfile
import unittest
from pathlib import Path

from main import Quiz, QuizGame, QuizSearch


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


if __name__ == "__main__":
    unittest.main()
