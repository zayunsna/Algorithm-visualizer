# Algorithm Lab

경로 탐색, DP, Greedy, 비트 연산을 이벤트 단위로 실행하는 학습용 Pygame 앱입니다.
알고리즘은 pygame을 import하지 않는 generator이며, 화면은 이벤트를 받아 그립니다.
앞뒤 이동은 같은 입력의 기록을 재생하고 복원합니다.

![첫 화면](docs/screenshots/01-first-screen.png)

## 설치와 실행

프로젝트 폴더에서 실행합니다. 독자용 설치 대상은 **CPython 3.12 + pygame 2.6.1 공식 wheel**입니다.
이 조합의 깨끗한 설치·앱 실행은 네트워크 제한으로 아직 검증하지 못했으므로 정식 지원 범위를 확정하지 않았습니다.
Python 3.10 이상 모두 지원한다는 안내는 철회했습니다. Python 3.14 소스 빌드는 독자용 설치 대상으로 안내하지 않습니다.

```sh
python3.12 -m venv .venv
.venv/bin/python -m pip install --only-binary=:all: -r requirements.txt
./run.sh
```

### 테마

기본 테마는 네온 색과 입체 버튼을 쓰는 `arcade`입니다. 이전 화면이 편하면 `classic`으로 실행합니다.
`classic`은 테마 도입 전 화면과 픽셀 단위로 같습니다(실습 20개 × 기본·도움말·About 60장 비교).

```sh
./run.sh --theme classic
ALGOVIZ_THEME=classic ./run.sh     # 환경변수로 지정해도 됩니다
```

기존 가상환경이 있으면 보존하고 새 프로젝트 복사본에서 설치하세요. 프로젝트를 옮길 때 `.venv`는 복사하지 않습니다.
[공식 배포 목록](https://pypi.org/project/pygame/2.6.1/#files)에 CPython 3.12 macOS ARM64 wheel이 있습니다.
pygame-ce로 변경하지 않았으며 numpy, 외부 API, 인증 정보도 사용하지 않습니다.

### 개발 환경 메모

UI·headless smoke·verify는 Python 3.14.2 / pygame 2.6.1 / SDL 2.32.10의 **수정된 로컬 pygame**에서 수행했습니다.
이전 작업에서 로컬 pygame을 `.venv`에 복사하고 freetype 기반 `font.py`의 순환 import를 그 복사본 안에서 수정했습니다.
이번 사용성 작업에서 추가 서드파티 수정은 하지 않았습니다. 이 패치를 독자의 설치 방법으로 권하지 않습니다.
별도 Python 3.12.13의 `.venv-wheel`에는 이전 작업에서 PyPI DNS 연결 실패로 pygame wheel을 설치하지 못했습니다.
pygame 미의존 알고리즘 테스트는 이 환경에서 실행할 수 있지만 UI 검증을 대신하지 않습니다.
전역 환경과 참고 프로젝트는 수정하지 않았습니다.

## 첫 실습

첫 화면에는 **Path: BFS vs DFS**의 고정 지도가 준비됩니다.
상단 `BFS`를 눌러 실행하고, 완료 후 `DFS`를 눌러 비교하세요. 기다리지 않으려면 `End >|` 또는 End 키를 사용합니다.
오른쪽 비교표에 알고리즘별 **cost / edges / expanded**가 쌓입니다. BFS는 13간선, DFS는 북쪽으로 깊게 탐색해 25간선입니다.
경로 실습에는 번호 단계 버튼이 없고, 알고리즘 버튼만 바꾸면 됩니다. 다른 모듈의 단계 버튼은 유지합니다.
설명은 제목 옆 `i`(About)와 공통 `?` 안에 접어 두었습니다.

실습 선택 메뉴는 Path / DP / Greedy / Bits 그룹으로 나뉩니다. Bits의 아래 항목은 메뉴 안에서 휠로 이동합니다.
실습을 불러오면 현재 입력이 교체된다는 상태 메시지가 나옵니다. 같은 실습은 같은 좌표 지도·입력으로 재현됩니다.

## 조작

| 조작 | 동작 |
|---|---|
| Space / Play / Pause | 재생·일시정지; 완료 후 Play는 같은 기록 재생 |
| → / Step >, ← / < Back | 이벤트 한 개 전진·복원 |
| End / End >\| | 끝까지 계산; 뒤로 이동 기록 보존 |
| R / Start | 같은 기록 처음으로 이동 |
| Slow / Normal / Fast | 해당 실습 기본 속도의 0.5배 / 1배 / 2배 |
| ↑ / +, ↓ / − | 초당 이벤트 수를 1씩 미세 조정; 범위 1..240 |
| Reset lesson | 기본 입력·기본 속도로 복원하고 비교표 초기화 |
| Tab / Enter | 버튼·필드 초점 이동 / 실행 |
| 필드 클릭, Enter 또는 Apply | 편집 적용; 오류이면 이전 입력·기록 보존 |
| 오른쪽 패널 휠 | 긴 자료구조·표 데이터 목록 보기 |
| i / ? | 실습 배경 설명 / 공통 도움말 |
| Esc / 팝업 바깥 클릭 | 팝업 닫기; 그 클릭은 배경 조작으로 전달되지 않음 |

팝업이 열린 동안 뒤쪽 키·클릭·휠·드래그를 막고 재생을 일시정지합니다.
단계 버튼 위에 마우스를 올리면 한 줄 설명 tooltip이 나옵니다.
필드 편집 중에는 Space와 R도 문자 입력입니다. Esc는 입력을 취소하며, 팝업·메뉴·편집이 없으면 앱을 종료합니다.
상태 메시지는 하단 한 곳에 모으며 오류를 우선합니다.

### 속도

기본값: 경로 30 events/s(열린 Guided 지도는 60), DP 12, Greedy 동전10·회의3·bag6,
Bits 기본4(논리·거듭제곱 판별2, 부호 반전·clear3, 시프트·부분집합1).
사용자가 바꾼 속도는 해당 실습을 다시 불러오면 유지하며, Reset lesson은 기본값으로 되돌립니다.
대표 단계의 5~15초 재생을 목표로 이벤트 수에 맞췄지만 모든 단계가 이 범위에 들지는 않습니다.
짧은 경계 사례·DFS·역추적과 몇 번 안 되는 greedy 선택은 더 빠르게 끝납니다. 최대 입력의 DP는 더 오래 걸립니다.
실습별 실제 자동 재생 시간은 [verification.json](docs/verification.json)의 `lesson_stage_timing`에 기록합니다.
이는 사람의 읽기·입력·이해 시간이 아닙니다.

## 고정 경로 지도와 예상 결과

| 실습 | 고정 입력 | 비교 결과 |
|---|---|---|
| BFS vs DFS | 16×10, S=(1,5), G=(14,5), y=3의 x=3..12 벽 | BFS cost13 / edges13 / expanded102, DFS cost25 / edges25 / expanded25 |
| Swamp costs | 16×10, x=6..9·y=4..6 늪 띠(진입 비용5) | BFS cost29 / edges13 / expanded111, Dijkstra cost17 / edges17 / expanded150 |
| Guided search | 열린 24×14, S=(1,7), G=(22,7) | Dijkstra cost21 / expanded267, A* cost21 / expanded22 |
| Heuristic trap | 16×10, (7,5) 한 칸 비용5 | A* cost15 / edges15 / expanded42, A* (h×3) cost17 / edges13 / expanded14 |

BFS·DFS는 goal을 발견한 relax 이벤트 직후 종료합니다. Dijkstra·A*는 goal을 우선순위 큐에서 꺼낼 때 종료합니다.
시작=goal은 비용0·간선0이며, 시작·도착이 막히거나 연결되지 않으면 No path를 표시합니다.
BFS는 간선 수를 최소화하며 늪 비용을 최소화하지 않습니다. DFS는 도달 가능성만 보장합니다.
기본 지도에서 DFS는 goal 발견 뒤 다른 frontier를 소모하지 않고 25칸 확장으로 종료합니다.

`Wall / Swamp / Erase / Start / Goal`로 지도에 그리며 오른쪽 클릭은 지우기입니다.
`Clear`는 벽·늪을 지우고, `Seed`와 `Random maze`는 동일 seed의 랜덤 지도를 재현합니다.
지도 편집은 비교표·기록을 초기화합니다. 랜덤 미로는 연결을 보장하지 않습니다.
가중치는 양의 정수, 비용은 칸 진입 시 지불하며 시작 칸 자체는 비용0입니다.
작은 칸과 A*의 g/h/f는 hover 패널에서 확인합니다.

### 순서와 동점 규칙

- 이웃은 Up → Right → Down → Left. BFS는 FIFO 큐입니다.
- DFS는 이웃을 역순으로 push해 Up부터 pop하며 **발견 시 중복 삽입을 막습니다**.
  대기 중인 형제를 먼저 발견하므로 교과서 재귀 DFS와 방문 순서·부모 트리가 다를 수 있습니다.
- Dijkstra와 A*는 key가 같으면 먼저 삽입한 항목을 우선합니다. stale 항목도 실제 PQ에 남아 있는 동안 표시합니다.
- A*의 h는 Manhattan 거리이며 h×1은 이 양의 가중치 격자에서 admissible/consistent합니다.
  h×3은 최적성을 보장하지 않으며, 더 나은 g가 발견되면 노드를 다시 엽니다.
- LCS는 동점이면 위로, 배낭 DP는 동점이면 현재 물건을 건너뜁니다.
- 동전 DP는 동점이면 큰 동전부터, 회의·물건 ratio 정렬은 동점이면 원래 입력 순서입니다.
- 부분집합은 mask 오름차순, 가치 동점은 먼저 나온 mask를 유지합니다.

## DP·Greedy 실습

| 실습 | 단계 | 관찰 |
|---|---|---|
| Fibonacci calls | Run naive → Run memo → Compare n=8 | n6 값8, 호출25 대11; n8 값21, 호출67 대15 |
| LCS traceback | Fill table → Trace back → Swap strings | 표 완성 후 일시정지, 참조 칸·역추적, 두 문자열의 공통 부분수열 |
| 0/1 knapsack | Fill table → Trace back → Compare greedy | 물건(2,12),(4,20),(6,24), 용량10: 2+3의 가치44; 같은 입력 공유 |
| Coin counterexample | Run greedy → Run optimal → Canonical coins | {1,3,4},6: greedy 4+1+1(3개), 최적 3+3(2개) |
| Canonical coins | Run greedy → Run optimal → Counterexample | {1,5,10,25},63은 둘 다6개 |
| Earliest start trap | Run start → Run finish → Try duration trap | 가장 먼저 시작하는 긴 회의1개 vs 가장 먼저 끝나는 회의3개 |
| Shortest meeting trap | Run duration → Run finish → Try start trap | 가운데 짧은 회의1개 vs 호환 가능한 회의2개 |
| Fractional vs 0/1 | Run ratios → Run optimal → Open DP table | 동일 입력: fractional48, 0/1 greedy32, DP44 |

표는 가로·세로 자동 맞춤이며 **Columns / Amounts 버튼과 표 휠 이동은 없습니다**.
글꼴은 일반19px·보조16px로 고정합니다. LCS는 각12자, 배낭은 최대8물건·표시 용량25입니다.
표 최소 칸은 가로28px·세로22px이며, 배낭 값이 길면 필요한 칸 너비가 증가해 허용 용량이 더 줄어듭니다.
표에 들어가지 않는 입력은 오류로 거절하며 이전 입력을 보존합니다. 알고리즘 자체 용량 제한30과 UI 표시 제한은 다릅니다.
동전은 금액0..150, 한 줄10칸으로 감싸며 `금액: 최소 동전 수`를 표시합니다. 현재 칸과 참조 칸은 항상 전체 표 안에 있습니다.
피보나치는 모든 호출 노드를 읽을 수 있도록 n<=8로 제한합니다.

## 비트 실습

W=4/8/16, 각 칸은 비트 값·자리값, 행은 10진수·16진수입니다.
모든 단어·결과는 `& ((1 << W) - 1)`로 자릅니다. signed는 같은 단어의 2의 보수 해석입니다.
Python의 `~5 == -6` 및 음수 `>>`는 폭 제한 없는 정수 동작입니다. W비트 결과와 raw Python 결과를 구분합니다.
논리 우측 시프트는 0, 산술 우측 시프트는 부호를 채웁니다. 패널 값도 현재 signed/unsigned 보기를 따릅니다.

| 실습 | 단계 | 관찰 |
|---|---|---|
| Logic gates | AND → XOR → NOT | 152,60: AND24 / XOR164 / NOT103; OR188은 연산 버튼 |
| Shift and sign | Logical right → Arithmetic right → Shift left | 152를2칸: 38 / 단어230(signed−26) / 96 |
| Two's complement | Negate x → Try zero → Minimum value | 5→251(signed−5), 0→0, −128→같은 단어128 |
| Clear and count | Clear once → Count all ones → Try zero | 152→144; 반복152→144→128→0, popcount3; zero popcount0 |
| Isolate lowest one | Isolate x → Try zero → Try odd x | 152→8, zero→0, odd37→1 |
| Power of two | Test x → Try zero → Try power | 기본12는 False, zero guard로0도 False,16은 True |
| XOR singleton | Find singleton → Reorder words → Change example | 짝은 취소되고7; 순서를 뒤집어도7, 새 예제는11 |
| Subsets and knapsack | List subsets → Use bag input → Open knapsack DP | 8부분집합의 최적44, 같은 물건·용량을 DP로 비교 |

`Use bag input`은 이전 DP/Greedy의 사용자 입력을 가져옵니다. 기본 입력을 바꾸지 않았다면 같은 입력이 다시 나오는 버튼입니다.
`Reorder words`는 정답을 바꾸는 버튼이 아니라 누적 순서가 바뀌어도 답이 같음을 보여주는 실습입니다.
Power 실습은 Test x와 Try power의 기본 입력이 같던 중복을 제거했습니다(12 대16).
XOR는 마스킹 후 정확히 하나가1회, 나머지는2회 나와야 합니다. 부분집합은 최대8물건이며 n<=W입니다.

## 파일 구조

```text
algoviz/
  engine.py       이벤트·Timeline·undo
  pathfinding.py  경로 generator·결정적 frontier
  dp.py           Fibonacci·LCS·0/1 배낭 generator
  greedy.py       동전·회의·분할/0/1 비교 generator
  bits.py         W비트 generator
  app.py          UI·입력·재생·자동 맞춤·팝업
  bits_view.py    비트 UI
  lessons.py      20실습·속도·고정 지도
  education.py    About·tooltip·도움말 설명
  theme.py        arcade / classic 색 테마
  capture.py      PNG 저장
 tests/fixtures/pathfinding.py.txt  이전 weighted-search snapshot 참조
 tools/verify.py                   캡처·실습 재생시간·프레임 측정
 tools/benchmark_end.py            80×60 End 벤치마크
 docs/                            검증 기록·스크린샷
```

## 검증

```sh
./verify.sh
# Optional screenshot
mkdir -p exports
./run.sh --headless --lesson 7 --finish --frames 3 --screenshot exports/coin.png
```

최신 전체 테스트는 **52개**입니다. 결과는 [usability-verify-output.txt](docs/usability-verify-output.txt)에 있습니다.

| 대상 | 독립 기준·회귀 검사 |
|---|---|
| 경로 | seed9031, 400개 무작위 작은 격자. Bellman-Ford와 Dijkstra/A* 비용 비교; 무가중 BFS 비용·DFS 도달성 비교 |
| 경로 종료·실습 | BFS/DFS goal relax 직후 done, weighted goal pop 뒤 done; 시작=goal·막힌goal 포함; 네 지도 주장 고정 |
| LCS·배낭 | 각각250개 작은 입력을 전체 부분수열·부분집합 열거와 비교 |
| Fibonacci | naive 호출 수 2F(n+1)−1, memo는 n>=2에서2n−1 |
| Greedy | 동전·회의·bag를 독립 전체 탐색과 비교, 실패 예제 고정 |
| Bits | AND/OR/XOR 각각65,536쌍을 자리 목록 계산과 비교; 모든8비트 시프트0..8·negation·tricks,4/16비트 경계 |
| 기록 | 알고리즘마다 모든 상태를 역행·재전진해 동일한지 검사; weighted frontier는 이전 snapshot fixture와 비교 |
| UI | 실제 Pygame 이벤트 주입. 20실습(경로 알고리즘 버튼, 나머지48단계), resize·Tab/Enter·입력 오류·popup·tooltip·속도 기억 |
| 표 | 각12자 LCS,8물건/용량25,금액150을 매 이벤트 그려 두 해상도의 모든 칸·참조·현재칸 사각형 포함 검사 |

About의 수치·성질은 위 독립 참조 테스트와 대조했습니다. 일반 알고리즘 복잡도는 기록·렌더 비용을 제외합니다.
h×3의 재개방 탐색에 safe A*의 복잡도 보장을 적용하지 않습니다.
비트 Python 설명은 [공식 정수 비트 연산 문서](https://docs.python.org/3/library/stdtypes.html#bitwise-operations-on-integer-types)와 대조했습니다.

[화면 검증 기록](docs/SCREEN_REVIEW.md), [측정 원본](docs/verification.json), [PNG manifest](docs/capture-manifest.json)을 함께 관리합니다.
1280×720 / 1366×768은 headless 캡처와 입력 이벤트로 검증하며 실제 데스크톱 사람 조작으로 보고하지 않습니다.
3분 사용성 목표는 End·알고리즘 비교표로 실습 동선을 줄였지만 실제 초보 사용자 테스트가 남아 있습니다.

### 성능 기록

frontier는 매 이벤트 전체 복사·정렬 대신 추가·삭제된 항목만 기록하며 실제 pop 순서는 화면에서 만듭니다.
80×60 Dijkstra의 최초 전후 측정은 일반 실행1.3706초→0.0786초,
tracemalloc 최대 Python 할당56,186,592→10,691,616바이트입니다.
[이전](docs/end-before.json), [최초 개선](docs/end-after-initial.json), [최신 재측정](docs/end-after.json)을 보존합니다.
verification.json의 `end_80x60`은 before / initial_after / after를 구분합니다.
300프레임 tick+draw+dummy display.flip 측정은 대기 시간을 제외하며 실제 GPU·전체 구간60fps 보장이 아닙니다.

### 남은 제한

- 깨끗한 공식 pygame 설치, 실제 macOS/HiDPI/트랙패드·다른 OS와 초보 독자3분 사용성은 미확인입니다.
- 기록은 이벤트 수에 따라 메모리를 사용합니다. 알고리즘 복잡도에는 기록·표시 비용이 포함되지 않습니다.
- 최대 입력의 재생은 작은 기본 실습보다 깁니다. End로 결과를 보거나 속도를 조절하세요.
- 긴 오른쪽 패널은 스크롤하며 긴 필드 미리보기는 생략됩니다. 비트 Result는 10진수/16진수 줄로 나눠 표시합니다.
- `.gitignore`에 `.DS_Store`를 추가했습니다. 기존 `docs/.DS_Store`는 삭제 확인을 받지 않아 보존했습니다.
