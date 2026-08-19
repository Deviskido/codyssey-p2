# 학습 개념 가이드

이 문서는 콘솔 게임에 실제로 사용된 Python과 Git 개념을 설명한다.

## Python 기초

변수는 값을 이름으로 저장해 재사용하게 한다. `play_quiz()`의 `correct`는 정답 수를, `total`은 전체 문제 수를 담는 예시다.

- `int`: `answer`, `score`처럼 정수를 표현한다.
- `str`: `question`과 선택지처럼 문자열을 표현한다.
- `bool`: `is_correct()`가 반환하는 참/거짓 값이다.
- `list`: `choices`, `quizzes`처럼 순서가 있는 여러 값을 담는다.
- `dict`: `actions`과 JSON 상태처럼 키와 값을 연결한다.

`if`/​`elif`/​`else`는 조건에 따라 다른 동작을 선택한다. 정답, 최고 점수, 종료 메뉴를 판단할 때 사용한다. `for`는 모든 문제처럼 대상이 정해진 반복에, `while`은 올바른 입력이나 종료 선택을 기다리는 반복에 적합하다.

함수는 `def 이름(매개변수):`로 정의한 재사용 코드다. 매개변수는 호출자의 값을 받고 `return`은 결과를 돌려준다. `read_number(prompt, minimum, maximum)`는 이 구조로 중복 입력 로직을 없앤다.

## 클래스와 객체

클래스는 데이터와 동작을 묶은 설계도이고, 객체는 그 설계도로 만든 실제 값이다. `Quiz`은 문제 하나를, `QuizGame`은 메뉴·점수·저장 흐름을 담당한다.

`__init__`은 객체 생성 시 자동 호출되는 초기화 메서드다. `self`는 현재 객체를 가리켜 각 문제의 데이터를 구분한다. 속성(attribute)은 `question`, `choices`처럼 객체가 보유한 데이터이고, 메서드(method)는 `display()`, `save_state()`처럼 클래스에 속한 함수다.

## 파일 입출력과 JSON

`with path.open(..., encoding="utf-8") as file` 형태는 파일을 열고 블록 종료 시 자동으로 닫는다. `json.load()`는 JSON을 Python `dict`/​`list`로 읽고 `json.dump()`는 반대로 쓴다. JSON은 사람이 읽을 수 있고 표준 라이브러리로 처리할 수 있어 영속 데이터에 적합하다.

`try`는 오류 가능 코드를 감싸고 `except`는 오류 발생 시 대응을 정의한다. 손상된 JSON, 파일 오류, 숫자 변환 실패, `Ctrl+C`, EOF를 처리해 안전하게 복구하거나 종료한다.

## Git과 GitHub

Git은 변경 이력을 로컬에서 관리하는 버전 관리 도구이고, GitHub는 Git 저장소를 온라인에 보관·공유하는 서비스다.

- `git init`: Git 저장소를 만든다.
- `git add`: 다음 커밋의 변경을 스테이징한다.
- `git commit`: 스테이징한 변경을 이력으로 저장한다.
- `git push`: 로컬 커밋을 원격으로 보낸다.
- `git pull`: 원격 변경을 가져와 통합한다.
- `git checkout`: 브랜치나 커밋 상태로 전환한다.
- `git clone`: 원격 저장소와 이력을 복제한다.

브랜치는 기준 코드와 분리해 기능을 개발하는 이력의 가지다. `merge`는 완성된 가지를 `main`에 통합한다. GitHub Pull Request를 이용하면 통합 전 토론과 코드 리뷰로 확장할 수 있다.
