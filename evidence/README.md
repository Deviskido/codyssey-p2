# 제출 요구사항 증거 인덱스

검증 기준: `trash/submit_requirements` 원문  
증거 수집일: 2026-08-19 (Asia/Seoul)

| 요구사항 | 상태 | 증거 |
|---|---|---|
| 메뉴와 풀기·추가·목록·점수·종료 | 충족 | `runtime-demo.md`, `main.py:243-341` |
| 주제별 퀴즈 5개 이상 | 충족 | `state-and-persistence.md`, 루트 `state.json` |
| 재실행 후 퀴즈·점수 유지 | 충족 | `runtime-demo.md` |
| 클래스 2개 이상 및 메서드 분리 | 충족 | `code-structure.md` |
| 루트 state.json UTF-8 저장·로드 | 충족 | `state-and-persistence.md` |
| GitHub 업로드 | 충족 | `git-evidence.txt` |
| 의미 있는 커밋 10개 이상 | 충족 | `git-evidence.txt` 수집 당시 13개 |
| 브랜치 생성·checkout·merge | 충족 | `git-evidence.txt`의 3개 기능 브랜치 |
| clone과 pull 사용 | 충족 | `git-evidence.txt`의 reflog |
| README 필수 항목 | 충족 | `readme-evidence.md` |

## 재현 명령

```bash
python3 main.py
python3 -m unittest discover -s tests -v
git log --graph --decorate --oneline --all
git reflog --date=iso --all
git status
```
