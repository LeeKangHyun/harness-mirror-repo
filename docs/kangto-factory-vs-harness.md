# 원본 `harness` vs `kangto-factory` — 측정 기반 심층 비교

> 2026-06-10. 멀티에이전트 비교 감사(에이전트 8개, 도구 호출 164회)의 종합 결과.
> 방법: **정적 비교 5축**(SKILL.md 전수 디프, references 12파일 대조, 도구 계층 검증, README 팩트체크, 토큰 실측) + **실행 비교**(동일 브리프로 두 스킬을 충실히 따라 하네스를 실제 생성 후 판정).
> 이 리포트에서 발견된 결함은 같은 날 수정됐다 — 하단 [수정 로그](#수정-로그-2026-06-10) 참조. 본문은 **수정 전** 상태 기준으로 서술한다.

## 한 줄 결론

골격(Phase 0~7, 6패턴, 3모드, QA 규칙, 진화 루프)은 사실상 1:1 이식이 확인됐고, kangto의 차별점(매니페스트+체커, 모델 티어링, ROI 게이트)은 같은 브리프 실행 비교에서도 실질 우위로 입증됐다. 다만 이식 과정의 진짜 손실 4건과 수정 가능한 결함 약 10건이 발견됐다(현재 대부분 수정됨).

## 1. 토큰 비용 (추정식: 비한글문자/4 + 한글문자×1.4 — 토크나이저 실측 아님)

| 구간 | 원본 | kangto | 차이 |
|---|---|---|---|
| 상시 (frontmatter description) | ≈249 tok | ≈230 tok | 사실상 동률 |
| 트리거 1회 (SKILL.md 본문) | ≈11,607 tok | ≈3,596 tok | **−69%** |
| 풀 워크플로 (references 전부 로드 시 상한) | ≈39,090 tok | ≈11,824 tok | −70% |

핵심 발견: 본문 **문자수** 차이는 7.7%뿐(15,544 vs 14,346자). 절감의 대부분은 압축이 아니라 **한글→영어 전환의 토큰 밀도 효과**다. "smaller per trigger"는 성립하지만, 이유는 "줄 수가 적어서"보다 "영어라서"가 크다. `scripts/`·`assets/`·`examples/`는 트리거 시 컨텍스트에 로드되지 않는 디스크 자산이므로 위 비교에서 제외.

## 2. 무엇이 살아남았고, 무엇이 진짜 사라졌나

원본 457줄 → kangto 171줄(당시)로 63% 압축됐지만, SKILL.md에서 빠진 것처럼 보이는 디테일 대부분은 **references로 이동해 생존**한 것이 번들 전수 grep으로 확인됐다: 실행 모드 의사결정 트리, 세션당 1팀 제약, PDF good/bad description 예시, near-miss 예시, 1회 재시도 정책, A/B 테스트 종료 조건, `_workspace` 아카이브 등. 일부는 이동하며 개선됐다(타임스탬프 아카이브, pre-edit 스냅샷 베이스라인, 이중 언어 예시).

**kangto 순수 추가 4종:** (1) `harness.json` 매니페스트+스키마, (2) `check_harness.py` 기계 드리프트 검증을 Phase 0/6/7 게이트로 삽입, (3) ROI 게이트 "When NOT to forge", (4) 생성물 토큰 최적화 원칙(2-4)과 역할별 모델 매핑(원본의 opus 고정 대체).

**번들 전체에서 소실된 진짜 손실 4건:**

1. ~~팀 크기 수치 표~~ (원본 :248-256, 작업 규모→팀원 수→팀원당 작업 수) → **복원됨** (`references/agent-design-patterns.md` "Team sizing")
2. 상충 데이터 "삭제 금지·출처 병기" 정책 (원본 :244) — 미복원
3. 대규모 변경 정량 임계값 "에이전트 3개 이상" (원본 :426) — 미복원 ("large changes"로만 잔존)
4. 모드별 데이터 전달 권장 조합 (원본 :233-235) — 미복원 (템플릿이 암묵적으로만 시연)

추가 간접 손실: `skill-writing-guide`→`skill-authoring` 재구성(-76%)에서 **데이터 스키마 표준**(grading.json 필드명 강제, eval_metadata.json 스키마)이 소실 — skill-testing-guide가 여전히 그 파일명을 전제하므로 규약 없는 파일명만 남았다. 원본 `team-examples.md`(5패턴 워크드 예시, 에이전트 파일 전문 2건)도 대응물이 없으며, `examples/deep-research/`가 1패턴분을 실물로 보상한다.

## 3. 발견된 결함과 수정 여부

| 결함 | 위치 | 상태 |
|---|---|---|
| 깨진 `see 5-3` 참조 (소실된 팀 크기 표의 잔재) | SKILL.md 2-4 | ✅ 수정 + 표 복원 |
| "update harness.json (and CLAUDE.md changelog)" — changelog 중복 금지 규칙(5-B, 7-3)과 모순 | SKILL.md 7-5 | ✅ 수정 |
| "Template + full examples" — 가리킨 파일에 전문 예시 없음 | SKILL.md Phase 3 | ✅ `examples/deep-research/` 포인터로 교체 |
| `examples/deep-research/`가 SKILL.md 어디에서도 미참조 (발견성 공백) | SKILL.md | ✅ Phase 3 + References 절에 등재 |
| 출하 체크리스트에 생성물 크기 상한 부재 (2-4 철학과 역행) | SKILL.md 체크리스트 | ✅ <300줄 항목 추가 |
| '하네스 현황', '하네스 엔지니어링' 한국어 트리거 누락 | SKILL.md description | ✅ 추가 |
| 비객체 agents 항목에서 AttributeError 크래시 | check_harness.py:54 | ✅ 수정 (스키마 오류로 보고) |
| agent `file` 키 부재 시 무검사 통과 | check_harness.py:64-66 | ✅ 항목 단위 필수 필드 검사 추가 |
| enum이 schema.json과 체커에 이중 정의 (DRY 위반) | check_harness.py | ✅ 스키마에서 규칙을 읽도록 변경 (fallback 유지) |
| 예제 매니페스트 3중 사본 + 실제 드리프트 1건 (academic-scout role 문구) | assets / manifest-guide / examples | ✅ 정본=examples, guide는 포인터화, assets는 동기화 사본으로 유지 |
| README "~157 lines" stale (실측 171, 수정 후 173) | README.md | ✅ 갱신 |
| README CLAUDE.md 주석 "trigger rule + changelog" — 스킬 사양과 모순 (팩트체크 '부정확' 판정) | README.md | ✅ "manifest pointer"로 수정 |

체커 수정 후 검증: 정상 케이스 exit 0(메시지 동일), 과거 크래시 케이스가 스키마 오류 10건 정밀 보고로 전환, standalone 사본 fallback 동작, 배열 매니페스트 FATAL exit 2 — 4개 테스트 모두 통과.

## 4. 실행 비교 — 같은 브리프, 다른 철학

동일 브리프(주간 경쟁사 모니터링: 수집→분석→경영진 리포트, 매주 반복)로 두 스킬을 각각 충실히 따라 하네스를 생성했다. 두 생성 에이전트 모두 자기 보고와 디스크가 일치했고 실행 품질은 양쪽 다 높았다 — 차이는 실행 편차가 아니라 **스킬의 명문 지시**에서 비롯됐다.

| | 원본 산출물 | kangto 산출물 |
|---|---|---|
| 모드 | 팀 (SendMessage 통신) — 스킬 기본값 | 서브에이전트 (파일 기반) — 2-4 right-sizing 적용 |
| 모델 | 전원 opus — 스킬이 강제 (:93) | sonnet/opus/sonnet 티어링 (:73) |
| 기록 | CLAUDE.md 12줄, 변경마다 이력 테이블 성장 | CLAUDE.md 6줄 고정 + harness.json 60줄 (비로드) |
| 드리프트 체크 | exit 2 (매니페스트가 설계상 부재) | exit 0 (기계 검증 통과) |
| 파일/규모 | 8파일 581줄 | 10파일 583줄 (+manifest, +config) |

판정: 5개 측면 중 4개(컨텍스트 무게, 에이전트 설계, 감사가능성, 유지보수)에서 kangto 우세, 스킬 설계 품질은 동등. 원본의 실질 우위도 확인됨 — **frontmatter `model:` 필드의 기계적 강제**(kangto 산출물은 prose 지시 의존), 더 풍부한 한국어 후속 트리거, 충실한 리포트 템플릿. 매주 반복 브리프는 "품질 최우선·팀 기본·프로즈 기록"(원본)보다 "반복 비용 최적화·기계 가독 정본·검증 가능성"(kangto) 철학에 부합하는 케이스였다.

## 5. README 팩트체크

비교 테이블·Honest caveats의 16개 주장 검증 결과: **13 정확 / 1 부분적 정확 / 1 부정확** (부정확·stale 2건은 수정 로그에 포함). "Honest caveats" 4건은 전부 유효했고, 특히 "token savings is reasoned, not measured"는 이번 추정식 측정으로 방향성이 확인되어 문구를 갱신했다. 원본에 대한 서술(한국어 ~458줄, prose changelog only, Korean-leaning 트리거, always opus)은 전수 grep으로 전부 사실 확인.

## 수정 로그 (2026-06-10)

이 리포트의 결함 목록(§3)을 일괄 수정: `SKILL.md` 6건, `references/agent-design-patterns.md` 팀 크기 표 복원, `references/manifest-guide.md` 인라인 사본 포인터화, `assets/harness.example.json` 정본 동기화, `scripts/check_harness.py` 재작성(스키마 단일 진실원 + 크래시 2경로 제거 + 항목 단위 필수 필드 검사), `README.md` 4건.

**미수정 잔여 항목** (후속 후보):
- 소실 손실 3건 복원 여부: 상충 데이터 출처 병기 정책, "에이전트 3개 이상" 정량 임계값, 모드별 데이터 전달 권장 조합
- 생성 에이전트 파일에 frontmatter `model:` 필드를 의무화 (실행 비교에서 원본의 우위로 확인된 항목)
- eval_metadata.json / grading.json 데이터 스키마 규약 복원 (skill-testing-guide가 전제하는 규약)
- sample-run 토큰 수치의 재현 스크립트 부재 (1회 기록이라 회귀 기준으로 못 씀)

## 부록 — 방법론 한계

- 토큰 수치는 문자 기반 추정식이며 한글 계수(1.4 tok/자) 가정에 민감하다. 토크나이저 실측 시 절대값은 달라질 수 있으나 방향성(영어 전환 효과가 지배적)은 유지될 것으로 본다.
- 실행 비교는 스킬당 1회 생성이라 분산을 말할 수 없다. 생성 에이전트에는 "사용자 질문 불가, 서브에이전트 스폰 금지" 제약이 있었고 양쪽 동일하게 적용됐다(생략 단계는 양쪽 모두 기록).
- 실행 비교 산출물은 임시 디렉터리에 생성됐고 저장소에는 커밋하지 않았다.
