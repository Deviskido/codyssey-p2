"""터미널에서 실행하는 Python 기초 퀴즈 게임."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Callable


STATE_PATH = Path(__file__).resolve().parent / "state.json"


class Quiz:
    """문제 하나와 네 개의 선택지, 정답 번호를 표현한다."""

    def __init__(self, question: str, choices: list[str], answer: int) -> None:
        question = question.strip()
        choices = [str(choice).strip() for choice in choices]
        if not question:
            raise ValueError("문제는 비어 있을 수 없습니다.")
        if len(choices) != 4 or any(not choice for choice in choices):
            raise ValueError("선택지는 비어 있지 않은 4개여야 합니다.")
        if not isinstance(answer, int) or isinstance(answer, bool) or not 1 <= answer <= 4:
            raise ValueError("정답은 1부터 4 사이의 정수여야 합니다.")
        self.question = question
        self.choices = choices
        self.answer = answer

    def display(self, number: int | None = None) -> None:
        """문제와 선택지를 출력한다."""
        print("-" * 40)
        title = f"[문제 {number}]" if number is not None else "[문제]"
        print(f"{title} {self.question}")
        for index, choice in enumerate(self.choices, start=1):
            print(f"{index}. {choice}")

    def is_correct(self, answer: int) -> bool:
        return answer == self.answer

    def to_dict(self) -> dict[str, object]:
        return {
            "question": self.question,
            "choices": self.choices,
            "answer": self.answer,
        }

    @classmethod
    def from_dict(cls, data: object) -> "Quiz":
        if not isinstance(data, dict):
            raise ValueError("퀴즈 항목은 객체여야 합니다.")
        return cls(data["question"], data["choices"], data["answer"])


def create_default_quizzes() -> list[Quiz]:
    """Python 기초를 주제로 직접 작성한 기본 문제를 반환한다."""
    return [
        Quiz(
            "Python의 창시자는 누구인가요?",
            ["귀도 반 로섬", "리누스 토르발스", "제임스 고슬링", "데니스 리치"],
            1,
        ),
        Quiz(
            "다음 중 변경할 수 있는(mutable) 자료형은 무엇인가요?",
            ["tuple", "str", "list", "int"],
            3,
        ),
        Quiz(
            "함수가 값을 돌려줄 때 사용하는 키워드는 무엇인가요?",
            ["yield", "return", "break", "import"],
            2,
        ),
        Quiz(
            "딕셔너리 리터럴을 만들 때 사용하는 괄호는 무엇인가요?",
            ["소괄호 ()", "대괄호 []", "중괄호 {}", "꺾쇠괄호 <>"],
            3,
        ),
        Quiz(
            "예외를 처리할 때 함께 사용하는 키워드 조합은 무엇인가요?",
            ["if / else", "for / while", "try / except", "def / return"],
            3,
        ),
    ]


class QuizGame:
    """메뉴, 퀴즈 진행, 점수와 파일 저장을 관리한다."""

    def __init__(
        self,
        state_path: Path | str = STATE_PATH,
        input_func: Callable[[str], str] = input,
    ) -> None:
        self.state_path = Path(state_path)
        self.input = input_func
        self.quizzes: list[Quiz] = []
        self.best_score: dict[str, int] | None = None
        self.load_state()

    def _use_defaults(self) -> None:
        self.quizzes = create_default_quizzes()
        self.best_score = None

    @staticmethod
    def _parse_best_score(value: object) -> dict[str, int] | None:
        if value is None:
            return None
        if isinstance(value, int) and not isinstance(value, bool) and value >= 0:
            return {"score": value, "correct": value, "total": 0}
        if not isinstance(value, dict):
            raise ValueError("최고 점수 형식이 올바르지 않습니다.")
        score = value.get("score")
        correct = value.get("correct")
        total = value.get("total")
        values = (score, correct, total)
        if any(not isinstance(item, int) or isinstance(item, bool) for item in values):
            raise ValueError("최고 점수 값은 정수여야 합니다.")
        if not 0 <= score <= 100 or correct < 0 or total < 0 or correct > total:
            raise ValueError("최고 점수 값의 범위가 올바르지 않습니다.")
        return {"score": score, "correct": correct, "total": total}

    def load_state(self) -> None:
        """상태 파일을 읽으며, 없거나 손상된 파일은 기본값으로 복구한다."""
        if not self.state_path.exists():
            self._use_defaults()
            print("📂 저장 파일이 없어 기본 퀴즈를 사용합니다.")
            return
        try:
            with self.state_path.open("r", encoding="utf-8") as file:
                data = json.load(file)
            if not isinstance(data, dict) or not isinstance(data.get("quizzes"), list):
                raise ValueError("필수 데이터가 없습니다.")
            self.quizzes = [Quiz.from_dict(item) for item in data["quizzes"]]
            self.best_score = self._parse_best_score(data.get("best_score"))
            score_text = self.best_score["score"] if self.best_score else "기록 없음"
            print(
                f"📂 저장된 데이터를 불러왔습니다. "
                f"(퀴즈 {len(self.quizzes)}개, 최고 점수 {score_text})"
            )
        except (
            OSError,
            json.JSONDecodeError,
            KeyError,
            TypeError,
            ValueError,
            AttributeError,
        ) as error:
            print(f"⚠️ 저장 파일을 읽을 수 없습니다: {error}")
            print("기본 퀴즈 데이터로 복구합니다.")
            self._use_defaults()
            self.save_state()

    def save_state(self) -> bool:
        """상태를 UTF-8 JSON에 안전하게 저장하고 성공 여부를 반환한다."""
        data = {
            "quizzes": [quiz.to_dict() for quiz in self.quizzes],
            "best_score": self.best_score,
        }
        temporary_path = self.state_path.with_suffix(self.state_path.suffix + ".tmp")
        try:
            self.state_path.parent.mkdir(parents=True, exist_ok=True)
            with temporary_path.open("w", encoding="utf-8") as file:
                json.dump(data, file, ensure_ascii=False, indent=2)
                file.write("\n")
            os.replace(temporary_path, self.state_path)
            return True
        except OSError as error:
            print(f"⚠️ 데이터를 저장하지 못했습니다: {error}")
            try:
                temporary_path.unlink(missing_ok=True)
            except OSError:
                pass
            return False

    def read_number(self, prompt: str, minimum: int, maximum: int) -> int:
        """범위 안의 정수를 입력할 때까지 안내하고 다시 입력받는다."""
        while True:
            raw_value = self.input(prompt).strip()
            if not raw_value:
                print(f"⚠️ 값을 입력하세요. ({minimum}-{maximum})")
                continue
            try:
                value = int(raw_value)
            except ValueError:
                print(f"⚠️ 숫자를 입력하세요. ({minimum}-{maximum})")
                continue
            if not minimum <= value <= maximum:
                print(f"⚠️ {minimum}-{maximum} 사이의 숫자를 입력하세요.")
                continue
            return value

    def read_text(self, prompt: str) -> str:
        """비어 있지 않은 문자열을 입력받는다."""
        while True:
            value = self.input(prompt).strip()
            if value:
                return value
            print("⚠️ 내용을 입력하세요.")

    @staticmethod
    def display_menu() -> None:
        print("\n" + "=" * 40)
        print("        🎯 Python 기초 퀴즈 게임 🎯")
        print("=" * 40)
        print("1. 퀴즈 풀기")
        print("2. 퀴즈 추가")
        print("3. 퀴즈 목록")
        print("4. 점수 확인")
        print("5. 종료")
        print("=" * 40)

    def play_quiz(self) -> None:
        if not self.quizzes:
            print("⚠️ 등록된 퀴즈가 없습니다.")
            return
        print(f"\n📝 퀴즈를 시작합니다! (총 {len(self.quizzes)}문제)")
        correct = 0
        for number, quiz in enumerate(self.quizzes, start=1):
            quiz.display(number)
            answer = self.read_number("정답 입력 (1-4): ", 1, 4)
            if quiz.is_correct(answer):
                correct += 1
                print("✅ 정답입니다!")
            else:
                correct_choice = quiz.choices[quiz.answer - 1]
                print(f"❌ 오답입니다. 정답은 {quiz.answer}번 ({correct_choice})입니다.")

        total = len(self.quizzes)
        score = round(correct / total * 100)
        print("\n" + "=" * 40)
        print(f"🏆 결과: {total}문제 중 {correct}문제 정답! ({score}점)")
        is_new_best = self.best_score is None or score > self.best_score["score"]
        if is_new_best:
            self.best_score = {"score": score, "correct": correct, "total": total}
            print("🎉 새로운 최고 점수입니다!")
        print("=" * 40)
        self.save_state()

    def add_quiz(self) -> None:
        print("\n📌 새로운 퀴즈를 추가합니다.")
        question = self.read_text("문제를 입력하세요: ")
        choices = [self.read_text(f"선택지 {number}: ") for number in range(1, 5)]
        answer = self.read_number("정답 번호 (1-4): ", 1, 4)
        self.quizzes.append(Quiz(question, choices, answer))
        if self.save_state():
            print("✅ 퀴즈가 추가되고 저장되었습니다!")
        else:
            print("⚠️ 퀴즈는 현재 실행에 추가되었지만 파일에는 저장되지 않았습니다.")

    def list_quizzes(self) -> None:
        if not self.quizzes:
            print("⚠️ 등록된 퀴즈가 없습니다.")
            return
        print(f"\n📋 등록된 퀴즈 목록 (총 {len(self.quizzes)}개)")
        print("-" * 40)
        for number, quiz in enumerate(self.quizzes, start=1):
            print(f"[{number}] {quiz.question}")
        print("-" * 40)

    def show_best_score(self) -> None:
        if self.best_score is None:
            print("🏆 아직 퀴즈를 푼 기록이 없습니다.")
            return
        record = self.best_score
        if record["total"]:
            print(
                f"🏆 최고 점수: {record['score']}점 "
                f"({record['total']}문제 중 {record['correct']}문제 정답)"
            )
        else:
            print(f"🏆 최고 점수: {record['score']}점")

    def run(self) -> None:
        """종료를 선택할 때까지 메뉴 루프를 실행한다."""
        actions = {
            1: self.play_quiz,
            2: self.add_quiz,
            3: self.list_quizzes,
            4: self.show_best_score,
        }
        try:
            while True:
                self.display_menu()
                selection = self.read_number("선택: ", 1, 5)
                if selection == 5:
                    self.save_state()
                    print("👋 게임을 종료합니다.")
                    return
                actions[selection]()
        except (KeyboardInterrupt, EOFError):
            print("\n⚠️ 입력이 중단되었습니다. 데이터를 저장하고 안전하게 종료합니다.")
            self.save_state()


def main() -> None:
    QuizGame().run()


if __name__ == "__main__":
    main()
