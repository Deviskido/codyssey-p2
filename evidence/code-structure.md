# 코드 구조 증거

## 클래스

`main.py`에는 요구된 `Quiz`, `QuizGame`을 포함해 프로젝트가 직접 작성한 5개 클래스가 정의되어 있다.

| 클래스 | 위치 | 책임 |
|---|---:|---|
| `Quiz` | `main.py:14` | 문제 하나, 선택지, 정답 판정, 직렬화 |
| `QuizSearch` | `main.py:59` | 문제·선택지 키워드 검색 |
| `ScoreCalculator` | `main.py:75` | 백점 기준 점수 계산 |
| `QuizCollection` | `main.py:88` | 외부 퀴즈 목록 검증과 객체 변환 |
| `QuizGame` | `main.py:129` | 메뉴와 전체 게임 흐름 관리 |

`Path`도 클래스이지만 프로젝트가 직접 정의한 클래스 수에는 포함하지 않았다. 위 표의 직접 정의 클래스는 실제로 5개이며, 최소 2개 조건을 넘는다.

## 기능별 메서드 분리

| 기능 | 메서드 | 위치 |
|---|---|---:|
| 상태 초기화 | `_use_defaults()` | `main.py:143` |
| 최고 점수 검증 | `_parse_best_score()` | `main.py:148` |
| 데이터 불러오기 | `load_state()` | `main.py:165` |
| 데이터 저장 | `save_state()` | `main.py:196` |
| 숫자 입력 | `read_number()` | `main.py:218` |
| 문자 입력 | `read_text()` | `main.py:235` |
| 메뉴 출력 | `display_menu()` | `main.py:244` |
| 게임 진행 | `play_quiz()` | `main.py:255` |
| 퀴즈 추가 | `add_quiz()` | `main.py:282` |
| 목록 표시 | `list_quizzes()` | `main.py:295` |
| 점수 표시 | `show_best_score()` | `main.py:309` |
| 전체 메뉴 제어 | `run()` | `main.py:322` |

## 자동화된 검증

실행 명령:

```bash
python3 -m unittest discover -s tests -v
```

수집 결과:

```text
Ran 58 tests in 0.140s

OK
```

테스트 파일:

- `tests/test_main.py`: 핵심 클래스, 저장, 입력, 메뉴 테스트
- `tests/test_extreme.py`: 경계값, 손상 복구, 전체 세션 테스트
- `tests/test_features.py`: 검색, 점수 계산, 상태 변환 테스트
- `tests/test_kanban.py`: 제출 요구사항 인수 테스트
