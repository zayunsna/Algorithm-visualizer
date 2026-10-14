# 화면 검증 기록

2026-10-14 사용성 개선 검증입니다. SDL dummy video/audio로 생성한 **50개 PNG를 각각 직접 열어** 확인했습니다.
실제 데스크톱 창을 사람이 조작한 결과가 아닙니다. 모든 이미지는 이번 UI로 다시 생성했습니다.
기본1280×720,15/37/49/50번은1366×768이며 글꼴은 일반19px·보조16px로 유지합니다.

> 2026-10-14 갱신: 현재 PNG는 기본 **arcade 테마**로 다시 생성했습니다. 버튼·패널의 위치와 크기는 classic과 같고
> 색과 장식만 다릅니다. arcade 재생성 후에는 01·44번을 직접 열어 확인했으며, 아래 표의 내용 확인은 classic 캡처 기준입니다.
> `classic` 테마(`--theme classic`)는 테마 도입 전 화면과 픽셀 단위로 같습니다(60장 비교).

경로 실습은 번호 버튼 대신 알고리즘 줄과 고정 지도·비교표를 사용합니다.
DP·동전 표는 전체 자동 맞춤이며 가로 이동 버튼/휠 코드는 없습니다.
표의 현재칸·참조칸·역추적은 화면 안에 있습니다. 긴 오른쪽 데이터 목록은 의도적으로 스크롤합니다.
Tooltip은 hover 동안 Observe의 일부를 덮는 말풍선이며 마우스를 이동하면 사라집니다.
About·공통 도움말·dropdown이 배경을 가리는 것은 모달의 의도된 동작입니다.
About와 도움말의 바깥 클릭은 닫기만 수행하고 뒤쪽 조작으로 전달되지 않습니다.

| 캡처 | 직접 확인한 내용 |
|---|---|
| [01-first-screen.png](screenshots/01-first-screen.png) | 긴 설명을 접은 고정 지도, 알고리즘 줄·About·재생 조작에 바로 접근 |
| [02-bfs.png](screenshots/02-bfs.png) | BFS cost13 / edges13 / expanded102; goal 발견 뒤 종료 |
| [03-dfs.png](screenshots/03-dfs.png) | DFS cost25 / edges25 / expanded25; BFS 비교값과 잔여 스택 |
| [04-bfs-swamp.png](screenshots/04-bfs-swamp.png) | 늪 띠를 건너는 BFS cost29 / edges13; 비용 라벨과 경로 |
| [05-dijkstra.png](screenshots/05-dijkstra.png) | 늪 띠 우회 Dijkstra cost17 / edges17 / expanded150; BFS 비교표 |
| [06-astar.png](screenshots/06-astar.png) | 열린 지도 cost21; Dijkstra267 대 A*22 확장 비교 |
| [07-astar-overestimate.png](screenshots/07-astar-overestimate.png) | 정상 A*15 대 h×3 비용17; h×3은14칸 확장 |
| [08-fibonacci.png](screenshots/08-fibonacci.png) | n6 호출 트리25 대 memo11, 결과8·반복/캐시 색 |
| [09-lcs-trace.png](screenshots/09-lcs-trace.png) | LCS 표42칸·길이4 BCBA·역추적; 열 이동 버튼 없음 |
| [10-knapsack-trace.png](screenshots/10-knapsack-trace.png) | 배낭 표 가치44·선택 물건2,3·역추적 |
| [11-coin-failure.png](screenshots/11-coin-failure.png) | 동전 greedy3 대 optimal2; 금액: 최소개수 셀과 오른쪽 선택 동전 |
| [12-activity-start.png](screenshots/12-activity-start.png) | earliest start1 대 optimal3; 선택·거절 이유와 최적 밑줄 |
| [13-activity-duration.png](screenshots/13-activity-duration.png) | shortest duration1 대 optimal2; 가운데 구간 반례 |
| [14-bag-comparison.png](screenshots/14-bag-comparison.png) | 동일 물건의 fractional48 / greedy32 / DP44 |
| [15-size-1366x768.png](screenshots/15-size-1366x768.png) | 1366×768 동전 비교와 동일 글꼴·재생 조작 |
| [16-input-error.png](screenshots/16-input-error.png) | 잘못된0 동전 거절; 기존 유효 입력 보존·하단 오류 |
| [17-fibonacci-n8.png](screenshots/17-fibonacci-n8.png) | n8 호출67 대 memo15·결과21·트리와 재생 조작 |
| [18-dropdown.png](screenshots/18-dropdown.png) | 그룹별 dropdown의 항목과 배경 가림; 이벤트 테스트로 배경 실행 차단 |
| [19-dp-dependencies.png](screenshots/19-dp-dependencies.png) | LCS 현재칸·참조 대각선 색과 모든 표 칸 |
| [20-priority-frontier.png](screenshots/20-priority-frontier.png) | 열린 지도 A* 진행 중 PQ key/g/순번과 현재칸 |
| [21-coin-dependencies.png](screenshots/21-coin-dependencies.png) | dp6=dp3+1·참조2,3,5 강조, 금액표의 현재6칸 |
| [22-dfs-help.png](screenshots/22-dfs-help.png) | BFS/DFS discovery 종료 대 weighted pop 종료 설명과 DFS 순서 주의 |
| [23-bits-logic.png](screenshots/23-bits-logic.png) | 논리 AND24·진리표·비트 자리값·분리한 Result decimal/hex |
| [24-bits-shift.png](screenshots/24-bits-shift.png) | 논리38/산술230·버리는 비트와 새로 채우는 비트 |
| [25-bits-negate.png](screenshots/25-bits-negate.png) | 5의 반전−5·단어251·carry와 raw Python 결과 |
| [26-bits-clear.png](screenshots/26-bits-clear.png) | 152의3회 popcount·잔여0·반복 횟수 |
| [27-bits-isolate.png](screenshots/27-bits-isolate.png) | 152 AND−152로8·최저1비트 분리 |
| [28-bits-power.png](screenshots/28-bits-power.png) | 기본12의 power False; Try power16과 중복되지 않는 입력 |
| [29-bits-unique.png](screenshots/29-bits-unique.png) | XOR singleton7·처리5개·현재 원소와 누적 비트 |
| [30-bits-subset.png](screenshots/30-bits-subset.png) | 8부분집합·mask7·용량 초과와 최적44 |
| [31-bits-borrow.png](screenshots/31-bits-borrow.png) | 152→151에서 뒤집히는 낮은4비트, AND 전 단계 |
| [32-bits-sign-minimum.png](screenshots/32-bits-sign-minimum.png) | 최소 signed−128의 반전이−128·raw Python128 |
| [33-bits-shift-16.png](screenshots/33-bits-shift-16.png) | 16비트 signed 시프트 패널 Logical16382 / Arithmetic−2; Result 안 잘림 |
| [34-bits-zero-guard.png](screenshots/34-bits-zero-guard.png) | x0도 power False인 nonzero guard |
| [35-bits-group-menu.png](screenshots/35-bits-group-menu.png) | Bits 그룹 스크롤 후 마지막 실습 접근 |
| [36-bits-help.png](screenshots/36-bits-help.png) | W비트 마스킹과 Python 무제한 정수·음수 >>의 차이 도움말 |
| [37-bits-1366.png](screenshots/37-bits-1366.png) | 1366×768 16비트 AND24·자리값·진리표·Result |
| [38-map-depth.png](screenshots/38-map-depth.png) | 새 깊이 지도와 BFS/DFS cost·edges·expanded 비교 |
| [39-map-swamp.png](screenshots/39-map-swamp.png) | 새 늪 띠 지도와 BFS29 대 Dijkstra17 비교 |
| [40-map-guided.png](screenshots/40-map-guided.png) | 열린24×14 지도와 Dijkstra267 대 A*22 확장 비교 |
| [41-map-trap.png](screenshots/41-map-trap.png) | heuristic 반례 정상15 대 h×3 비용17 비교 |
| [42-lcs-maximum.png](screenshots/42-lcs-maximum.png) | 1280×720 최대12자×12자 LCS의13행·13열·역추적이 메인 안에 포함 |
| [43-coin-150.png](screenshots/43-coin-150.png) | 1280×720 금액150:151칸, 한 줄10칸, 현재150과 참조146/147/149가 보임 |
| [44-about.png](screenshots/44-about.png) | About6줄: What / Key idea / Watch / Cost / Space와 닫기 안내 |
| [45-tooltip.png](screenshots/45-tooltip.png) | Fill table 한 줄 tooltip; hover 동안 Observe 일부를 의도적으로 덮는 말풍선 |
| [46-speed-presets.png](screenshots/46-speed-presets.png) | Slow / Normal / Fast·미세 조정·선택 Fast24 ev/s·재생 버튼 접근 |
| [47-knapsack-maximum.png](screenshots/47-knapsack-maximum.png) | 8물건·용량25:9행×26열, 가치60·선택1..6·아래 footer와 겹치지 않음 |
| [48-shift-signed.png](screenshots/48-shift-signed.png) | 8비트 signed 시프트: Logical62 / Arithmetic−2; Result decimal−2 / hexFE |
| [49-lcs-1366.png](screenshots/49-lcs-1366.png) | 1366×768 최대 LCS의13행·13열·역추적 포함 |
| [50-coin-1366.png](screenshots/50-coin-1366.png) | 1366×768 금액150 전체 표·최적38·greedy39·재생 조작 |

## 테스트와 측정

전체 **52개 테스트 통과**: [verify 실행 로그](usability-verify-output.txt), [단위 테스트 로그](test-results.txt).
순수 알고리즘은 별도 Python3.12.13에서 **23개 통과**: [로그](python312-algorithm-tests.txt).
마지막 canonical coin About 문구를 해당 실습의 관찰값63/6개로 구체화한 뒤,
20실습×두 해상도의 About·tooltip 회귀를 추가 실행해 통과했습니다: [로그](about-final-test.txt).

headless 시작·종료 smoke와 verify.sh를 실행했습니다. 실제 Pygame 클릭·드래그·키·휠·Tab/Enter·resize·QUIT 이벤트를 주입했습니다.
경로4실습의5알고리즘 버튼, 나머지16실습의48번호 버튼, 비트4/8/16 폭을 검증했습니다.
52개에는 기존400개 무작위 격자의 Bellman-Ford 비교, DFS 도달성, 경계 사례와 이벤트 undo/replay가 포함됩니다.
새 종료 테스트는 BFS/DFS의 goal relax 직후 done과 weighted goal expand 뒤 done을 구분합니다.

최대 LCS12자·배낭8물건/용량25·동전150은 **모든 이벤트마다** 표를 그려,
각 칸 및 현재·참조 칸의 사각형이 두 해상도에서 메인 영역 안에 포함되는지 검사했습니다.
긴 배낭 숫자는 칸·행 라벨 너비를 늘리며, 공간이 모자라면 오류로 거절합니다.
용량30·9물건·13자 문자열·금액151을 UI에서 거절하고 이전 입력을 보존합니다.
10자리 배낭 가치도 글꼴을 줄이지 않고 표시하는 회귀를 포함했습니다.

About의 수치·알고리즘 성질은 경로 참조값, DP/Greedy 전체 탐색, 비트 전수 테스트와 대조했습니다.
복잡도는 기록/렌더를 제외한 알고리즘을 설명합니다. safe A*의 복잡도는 h×3 재개방 탐색의 보장이 아닙니다.
Python 정수 설명은 README에 링크한 공식 문서와 대조했습니다.

단계 검토: Bits의 Use bag input은 커스텀 bag을 공유하지 않았으면 기본 입력을 다시 사용합니다.
Reorder words는 최종 정답을 의도적으로 유지하며 누적 순서의 변화를 보여 줍니다.
Power의 Test x와 Try power가 모두16이던 중복은 기본값12 / Try power16으로 수정했습니다.
LCS Swap strings는 같은 최적 길이를 유지할 수 있지만 표의 차원·의존·역추적 비교를 위한 단계입니다.

첫 지도 BFS와 DFS 자동 재생 합계는 **9.76초**, End를 쓴 자동 입력·렌더·계산 작업은 **0.0126초**입니다.
이전44.33초의3번호 단계와는 지도·종료 시점·버튼 흐름도 달라 단순 속도 비교로 해석하지 않습니다.
기본 speed와 실제 각 단계 시간은 [verification.json](verification.json)의 lesson_stage_timing에 기록합니다.
대부분의 설명용 계산 단계는 약5~15초이나, DFS·traceback·zero·몇 개 안 되는 greedy 선택은 더 짧습니다.
모든 단계가 이 범위를 만족했다고 보고하지 않습니다. 사람의 클릭·이해 시간도 포함하지 않습니다.

80×60 Dijkstra 진행 중300프레임: 평균 **8.19ms**, p95 **8.442ms**, 최대 **9.124ms**.
80×60 End 최신 일반 계산 **0.084초**·3,871확장·비용79이며 전후 측정 원본은 verification.json에 있습니다.
tick+draw+dummy display.flip을 재고 대기는 제외했습니다. 실제 GPU·HiDPI·전체 탐색 구간의60fps 보장이 아닙니다.
캡처 manifest의50개 상대 경로·해상도·SHA-256과 파일 내용을 대조합니다.

## 확인하지 못한 사항

- **공식 pygame wheel의 깨끗한 설치·UI 실행은 이전 PyPI DNS 실패 이후 검증하지 못했습니다.**
  UI·smoke·verify는 Python3.14.2의 로컬 수정 pygame2.6.1에서만 수행했습니다.
- 실제 macOS 창의 키·트랙패드·HiDPI, 다른 OS/Python 조합은 확인하지 않았습니다.
- 초보 블로그 독자의 설명서 없이3분 내 실습 완료 여부는 실제 사용자 테스트가 남아 있습니다.
- 기존 docs/.DS_Store는 삭제 승인을 받지 않았으므로 보존했습니다.

이전30/44개 테스트 로그와 최초 End 전후 수치는 과거 기록입니다.
현재 기능·화면·기대값의 기준은 이 문서, README, verification.json, capture-manifest.json입니다.
