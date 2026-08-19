# state.json 및 영속성 증거

- 기본 경로: `main.py:11`의 `Path(__file__).resolve().parent / "state.json"`
- UTF-8 로드: `main.py:172`의 `open("r", encoding="utf-8")`
- JSON 역직렬화: `main.py:173-177`
- UTF-8 저장: `main.py:205`의 `open("w", encoding="utf-8")`
- 한글 보존: `main.py:206`의 `ensure_ascii=False`
- 안전한 교체: `main.py:202-208`의 임시 파일과 `os.replace()`

현재 루트 `state.json`에는 각각 문제, 선택지 4개, 정답 번호를 갖춘 상식 퀴즈 5개가 있다.

```text
1. 대한민국의 수도는 어디인가요?
2. 태양계에서 가장 큰 행성은 무엇인가요?
3. 물의 화학식은 무엇인가요?
4. 한글을 창제한 왕은 누구인가요?
5. 1킬로미터는 몇 미터인가요?
```

추가 퀴즈와 최고 점수의 재실행 유지 결과는 `runtime-demo.md`에 기록했다.
