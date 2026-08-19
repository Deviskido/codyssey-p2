# Python 기초 퀴즈 게임

## 프로젝트 개요

Python 기본 문법, 클래스, 예외 처리, JSON 파일 입출력을 연습하기 위한 터미널 퀴즈 게임입니다. 퀴즈를 풀거나 직접 추가할 수 있으며, 추가한 문제와 최고 점수는 프로그램을 다시 실행해도 유지됩니다.

## 퀴즈 주제와 선정 이유

기본 퀴즈의 주제는 **Python 기초 문법**입니다. 게임을 구현하면서 사용하는 자료형, 함수, 딕셔너리, 예외 처리 개념을 문제로 다시 확인할 수 있어 이 주제를 선택했습니다.

## 실행 방법

Python 3.10 이상이 필요하며 외부 패키지는 사용하지 않습니다. 먼저 `python3 --version`으로 사용 중인 버전을 확인합니다.

```bash
python3 main.py
```

처음 실행할 때 `state.json`이 없다면 기본 퀴즈 5개로 시작합니다. 종료 메뉴를 선택하거나 `Ctrl+C`, 입력 스트림 종료가 발생하면 가능한 데이터를 저장하고 안전하게 종료합니다.

테스트 실행 방법은 다음과 같습니다.

```bash
python3 -m unittest discover -s tests -v
```

## 기능 목록

- Python 기초 문제 5개 기본 제공
- 저장된 모든 퀴즈 풀기 및 문제별 정답 확인
- 문제, 선택지 4개, 정답 번호를 입력해 퀴즈 추가
- 저장된 퀴즈 목록 확인
- 최고 점수와 당시 정답 수 확인
- 빈 입력, 숫자가 아닌 입력, 범위 밖 입력 재처리
- 손상되거나 없는 데이터 파일의 복구
- `KeyboardInterrupt`와 `EOFError`의 안전한 종료 처리
- UTF-8 JSON을 이용한 퀴즈 및 최고 점수 영속화

## 파일 구조

```text
codyssey-p2/
├── LEARNING_GUIDE.md          # Python, OOP, JSON, Git 개념 가이드
├── kanban.md                  # 전체 과제 체크리스트
├── main.py                    # Quiz, QuizGame 클래스와 실행 진입점
├── state.json                 # 실행 중 생성되는 퀴즈 및 점수 데이터
├── tests/
│   └── test_main.py           # 클래스, 저장, 복구, 입력 및 점수 테스트
├── .gitignore
└── README.md
```

## 데이터 파일 설명

`state.json`은 프로젝트 루트에 생성되는 UTF-8 JSON 파일입니다. `quizzes`에는 문제 목록을, `best_score`에는 최고 점수와 그때의 정답 수를 저장합니다.

```json
{
  "quizzes": [
    {
      "question": "Python의 창시자는 누구인가요?",
      "choices": ["귀도 반 로섬", "리누스 토르발스", "제임스 고슬링", "데니스 리치"],
      "answer": 1
    }
  ],
  "best_score": {
    "score": 100,
    "correct": 5,
    "total": 5
  }
}
```

- `question`: 문제 문자열
- `choices`: 선택지 4개의 문자열 배열
- `answer`: 1부터 4 사이의 정답 번호
- `score`: 0부터 100까지의 최고 점수
- `correct`: 최고 점수 기록 당시 맞힌 문제 수
- `total`: 최고 점수 기록 당시 출제된 전체 문제 수

파일이 없으면 기본 데이터로 실행합니다. JSON이 손상되었거나 스키마가 올바르지 않으면 안내 메시지를 출력하고 기본 퀴즈로 복구합니다.

## Git 실습 안내

코드에 사용된 Python 문법, 객체지향, JSON, Git 개념은 [LEARNING_GUIDE.md](LEARNING_GUIDE.md)에서 실제 예시와 함께 설명합니다.

과제의 Git 이력 조건은 완성된 코드를 한 번에 커밋하는 것으로 충족되지 않습니다. 메뉴, 클래스, 플레이, 추가, 목록, 점수, 저장, 문서처럼 실제 작업 단위에 따라 의미 있는 커밋을 만들고, 퀴즈 풀기 기능은 별도 브랜치에서 작업한 후 `main`에 병합해야 합니다. 개발 완료 후 별도 디렉터리에 저장소를 `clone`하고, 간단한 문서 변경을 `push`한 뒤 기존 디렉터리에서 `pull`하여 반영 여부를 확인합니다.



## 재현 명령

```bash
python3 main.py
python3 -m unittest discover -s tests -v
git log --graph --decorate --oneline --all
git reflog --date=iso --all
git status
```


한줄추가했습니다@@@@
