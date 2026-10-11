import datetime
import os

# PDF 로컬 렌더링을 위한 절대 경로 변환기
def get_absolute_path(url_path):
    """
    웹 브라우저용 상대 경로(/assets/...)를 PDF 변환기(WeasyPrint)가 읽을 수 있는 
    서버의 물리적 절대 경로(예: 프로젝트/assets/...)로 변환합니다.
    """
    if not url_path:
        return None
        
    if url_path.startswith('/assets/'):
      # 생성된 이미지는 Streamlit 구현의 assets 디렉터리에 저장됩니다.
      assets_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets')
      return os.path.join(assets_dir, url_path.removeprefix('/assets/'))
        
    return url_path

def build_css(seed_color, sd_color, sl_color):
    """
    대표님의 오리지널 매거진 감성 디자인과 
    WeasyPrint 무한 루프 방어 로직이 완벽하게 결합된 마스터 CSS
    """
    return f"""
    @import url('https://fonts.googleapis.com/css2?family=Noto+Serif+KR:wght@300;400;600;700&family=Noto+Sans+KR:wght@300;400;500;700&display=swap');

    /* ==========================================================================
       [WeasyPrint PDF 기본 설정 및 에러 방어]
       ========================================================================== */
    @page {{
        size: A4;
      margin: 12mm 12mm;
    }}

    @page:first {{
      margin: 0;
    }}

    :root {{
        /* 파이썬에서 주입받는 브랜드 핵심 컬러 */
        --seed: #666666; /* 짙은 중간 회색 (버튼, 아이콘 등 포인트 컬러 - 차분한 강조) */
        --sd: #000000;   /* 검은색 (소제목, 텍스트 라인 - 가독성 100% 확보) */
        --sl: #F5F5F5;   /* 아주 밝은 회색 (정보 박스 배경색 - 화사하고 깨끗함) */

        /* 세련된 무채색 팔레트 (프리미엄 무드) */
        --bg: #FDFDFD;        /* 완전 흰색이 아닌 아주 미세한 웜톤 배경 */
        --surface: #FFFFFF;    /* 카드/박스 배경 */
        --text-main: #1A1A1A;  /* 너무 까맣지 않은 우아한 먹색 */
        --text-muted: #737373; /* 보조 텍스트 */
        --border-light: rgba(0, 0, 0, 0.08); /* 부드러운 테두리 */
        --border-strong: rgba(0, 0, 0, 0.15);
    }}

    * {{ box-sizing: border-box; margin: 0; padding: 0; }}

    body {{
      font-family: 'Noto Sans KR', sans-serif;
      background: var(--bg);
      color: var(--text-main);
      line-height: 1.55;
      -webkit-font-smoothing: antialiased;
    }}

    /* ==========================================================================
       [1. 커버 페이지 (매거진 스타일)]
       ========================================================================== */
    .cover {{
      min-height: 297mm;
        background: var(--seed);
        position: relative;
        page-break-after: always;
        overflow: hidden;
        display: flex;
        flex-direction: column;
        justify-content: flex-end;
      padding: 36px 28px;
    }}

    /* 감각적인 원형 배경 데코 (오버레이 블렌딩 느낌) */
    .deco {{ position: absolute; border-radius: 50%; background: var(--sd); opacity: 0.05; }}
    .deco1 {{ width: 140%; height: 140vw; top: -70%; right: -30%; }}
    .deco2 {{ width: 300px; height: 300px; bottom: 20%; left: -100px; opacity: 0.08; }}
    .cv-content {{ position: relative; z-index: 10; }}

    .cv-tag {{
        display: inline-block; border: 1px solid var(--sd); border-radius: 30px;
        padding: 6px 18px; font-size: 11px; letter-spacing: 0.25em; color: var(--sd);
        text-transform: uppercase; margin-bottom: 24px;
    }}
    .cv-brand {{
        font-family: 'Noto Serif KR', serif; font-size: 68px; font-weight: 700;
        color: var(--sd); letter-spacing: -0.02em; line-height: 1.1; margin-bottom: 8px;
    }}
    .cv-en {{ font-size: 16px; font-weight: 400; color: var(--sd); letter-spacing: 0.3em; text-transform: uppercase; margin-bottom: 32px; opacity: 0.8; }}
    .cv-div {{ width: 60px; height: 2px; background: var(--sd); margin-bottom: 24px; opacity: 0.4; }}
    .cv-meaning {{ font-size: 15px; font-weight: 500; color: var(--sd); line-height: 1.7; margin-bottom: 8px; opacity: 0.9; }}
    .cv-slogan {{ font-size: 13px; color: var(--sd); font-style: italic; opacity: 0.7; }}
    .cv-year {{ position: absolute; top: 60px; right: 70px; font-size: 12px; font-weight: 600; color: var(--sd); letter-spacing: 0.15em; opacity: 0.6; }}

    /* ==========================================================================
       [2. 섹션 공통 & 타이포그래피 (페이지 넘김 완벽 제어)]
       ========================================================================== */
    .section {{
      padding: 0;
      background: var(--bg);
      page-break-before: always; 
      page-break-inside: auto;  /* avoid를 auto로 변경! (내용이 길면 자연스럽게 넘어가도록 허용) */
      position: relative;
      width: 100%;
    }}
    .section:first-child {{ page-break-before: auto; }}

    .sec-hdr {{ margin-bottom: 12px; padding-bottom: 8px; border-bottom: 1px solid var(--border-light); }}
    .sec-num {{ font-size: 10px; font-weight: 700; letter-spacing: 0.18em; color: var(--sd); text-transform: uppercase; display: block; margin-bottom: 6px; }}
    .sec-title {{ font-family: 'Noto Serif KR', serif; font-size: 22px; font-weight: 700; color: var(--text-main); display: block; margin-bottom: 4px; }}
    .sec-sub {{ font-size: 12px; color: var(--text-muted); line-height: 1.5; display: block; }}

    /* ==========================================================================
       [3. 현대적인 Flexbox & Grid 시스템]
       ========================================================================== */
    .grid-2, .grid-3 {{ display: flex; flex-wrap: wrap; gap: 10px; margin-bottom: 12px; page-break-inside: auto; break-inside: auto; }}
    .grid-2 > * {{ width: calc(50% - 5px); }}
    .grid-3 > * {{ width: calc(33.333% - 6.67px); }}
    /* Enforce a true 4-column grid for persona/secondary lists to avoid wrapping into 3 cols */
    .grid-4 {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 12px; page-break-inside: avoid; break-inside: avoid-page; }}
    /* 강제 3열 그리드(트리거 카드용) */
    .triggers-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-bottom: 12px; page-break-inside: avoid; }}
    .triggers-grid > .card {{ page-break-inside: avoid; break-inside: avoid-page; min-width: 0; }}
    /* 중앙 정렬 카드 (타겟 정의 / 소비 행동 등) */
    .centered-card {{ display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; }}

    /* ==========================================================================
       [4. 컴포넌트: 카드, 스워치, 하이라이트]
       ========================================================================== */
    .card {{ background: var(--surface); border: 1px solid var(--border-light); border-radius: 12px; padding: 12px; page-break-inside: avoid; break-inside: avoid-page; }}
    .c-lbl {{ font-size: 10px; font-weight: 700; letter-spacing: 0.15em; color: var(--text-muted); text-transform: uppercase; margin-bottom: 10px; }}
    .c-ttl {{ font-size: 16px; font-weight: 700; color: var(--text-main); margin-bottom: 8px; line-height: 1.4; }}
    .c-body {{ font-size: 13px; color: #444; line-height: 1.8; }}

    .hl-box {{ background: var(--sl); border-radius: 10px; padding: 14px 16px; margin-bottom: 12px; border-left: 4px solid var(--sd); page-break-inside: auto; break-inside: auto; }}
    .hl-box p {{ font-size: 13.5px; line-height: 1.7; color: var(--text-main); margin: 0; }}

    /* ==========================================================================
       [5. 슬로건 & 인용구]
       ========================================================================== */
    .slogan-box {{ text-align: center; padding: 20px 16px; background: var(--surface); border-top: 2px solid var(--sd); border-bottom: 2px solid var(--sd); margin: 14px 0; page-break-inside: auto; break-inside: auto; }}
    .sl-ko {{ font-family: 'Noto Serif KR', serif; font-size: 26px; font-weight: 700; color: var(--sd); line-height: 1.5; margin-bottom: 8px; }}
    .sl-en {{ font-size: 13px; color: var(--text-muted); font-style: italic; letter-spacing: 0.05em; }}

    /* ==========================================================================
       [6. 데이터 테이블]
       ========================================================================== */
    .data-table {{ width: 100%; border-collapse: collapse; margin-top: 6px; margin-bottom: 10px; font-size: 10.5px; page-break-inside: auto; }}
    .data-table tr {{ page-break-inside: avoid; }}
    .data-table th {{ background: rgba(0,0,0,0.03); color: var(--text-muted); font-size: 10.5px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; text-align: left; padding: 10px 12px; border-bottom: 1px solid var(--border-strong); }}
    .data-table td {{ padding: 10px 12px; border-bottom: 1px solid var(--border-light); color: #444; line-height: 1.5; vertical-align: top; font-size: 10.5px; }}
    .data-table td strong {{ color: var(--text-main); font-weight: 700; }}

    /* ==========================================================================
       [7. 태그 & 리스트]
       ========================================================================== */
    .tags {{ margin-top: 10px; display: flex; flex-wrap: wrap; gap: 6px; justify-content: flex-start; }}
    .tag {{ display: inline-block; border-radius: 18px; padding: 5px 12px; font-size: 10.5px; font-weight: 600; border: 1px solid var(--border-strong); background: var(--surface); color: var(--text-main); }}

    /* Story box paragraph 규격 중앙 통제 */
    .story p {{ font-size: 13px; color: #2C2A29; margin-bottom: 14px; text-align: justify; line-height: 1.9; text-indent: 12px; }}

    /* A-4 하단: domains / sns 시각 구분 */
    .domains-box {{ background: rgba(240,248,255,0.6); border-radius: 10px; padding: 12px; }}
    .sns-box {{ background: rgba(255,248,240,0.6); border-radius: 10px; padding: 12px; }}
    /* 무드 태그용 중앙 정렬 변형 */
    .mood-tags {{ justify-content: center; }}

    /* 컬러 팔레트 칩 축소용 유틸 */
    .color-chip-large {{ height: 90px; }}
    .color-chip-medium {{ height: 48px; }}
    .do-dont-grid {{ page-break-inside: avoid; display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }}
    .do-dont-grid > div {{ page-break-inside: avoid; }}
    .color-name-small {{ font-size: 11px; }}
    .color-hex-small {{ font-size: 10.5px; }}

    /* 컬러 표 축소 규격 */
    .color-table {{ font-size: 10px; }}
    .color-table th {{ padding: 8px 10px; }}
    .color-table td {{ padding: 8px 10px; vertical-align: top; }}

    .custom-list {{ list-style: none; margin-top: 10px; }}
    .custom-list li {{ position: relative; padding: 12px 14px 12px 24px; background: var(--surface); border: 1px solid var(--border-light); margin-bottom: 8px; border-radius: 10px; font-size: 13.5px; font-weight: 600; color: var(--text-main); page-break-inside: avoid; break-inside: avoid-page; }}
    .custom-list li::before {{ content: "•"; position: absolute; left: 14px; top: 16px; color: var(--sd); font-size: 18px; line-height: 1; }}
    .custom-list li .note {{ display: block; font-size: 12px; color: var(--text-muted); font-weight: 400; margin-top: 6px; font-style: italic; }}

    .promise-block {{ background: var(--surface); border: 1px solid var(--border-light); border-left: 4px solid var(--sd); border-radius: 8px; padding: 14px 16px; margin-bottom: 10px; page-break-inside: auto; break-inside: auto; }}
    .promise-block .ch {{ font-size: 11px; font-weight: 700; color: var(--sd); letter-spacing: 0.1em; margin-bottom: 8px; text-transform: uppercase; }}
    .promise-block .ct {{ font-size: 13px; color: #444; line-height: 1.8; }}
    """

# 들어온 데이터(O, A, B, C, D, E)의 유무를 판단하여 전체 14페이지 분량의 HTML 문서를 유연하게 조립(레고 블록)하는 메인 통제소
def assemble_html(brand_info, data_A=None, data_B=None, data_C=None, data_DE=None, brand_dna=None, integrity_report=None, decision_traces=None):
    
    # 프론트엔드에서 씌운 이중 껍질(data_a, data_b 등) 안전하게 벗겨내기
    if data_A and 'data_a' in data_A: data_A = data_A['data_a']
    if data_B and 'data_b' in data_B: data_B = data_B['data_b']
    if data_C and 'data_c' in data_C: data_C = data_C['data_c']
    if data_DE and 'data_de' in data_DE: data_DE = data_DE['data_de']

    # 1. 컬러 시스템 설정 (동적 테마 적용)
    seed_color = brand_info.get('seed_color', '#000000') if brand_info else '#000000'
    sd_color = "#3A3A3A" # Accent/Highlight 컬러
    sl_color = "#F8F9FA" # Primary/Background 컬러

    if data_C:
        c_dict = {}
        if isinstance(data_C, (tuple, list)):
            for part in data_C:
                if isinstance(part, dict): c_dict.update(part)
        else:
            c_dict = data_C

        palette = c_dict.get('color_palette', [])
        for c in palette:
            role = c.get('role', '').lower()
            hex_code = c.get('hex_code', '')

            if 'primary' in role:
                sl_color = hex_code
            elif 'secondary' in role or 'accent' in role:
                sd_color = hex_code

    # 로고 및 캐릭터 이미지 경로를 WeasyPrint용 절대 경로로 변환
    logo_path = None
    char_path = None
    if data_DE:
        logo_path = get_absolute_path(data_DE.get('logo_path', None))
        char_path = get_absolute_path(data_DE.get('char_path', None))

    # 2. CSS 주입 및 HTML 뼈대 생성
    css = build_css(seed_color, sd_color, sl_color)
    html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <link href="https://fonts.googleapis.com/css2?family=Gothic+A1:wght@400;800&family=Noto+Sans+KR:wght@400;500;700&family=Noto+Serif+KR:wght@400;600;700&display=swap" rel="stylesheet">
  <style>{css}</style>
</head>
<body>
"""

    if brand_info:
        html += build_cover(brand_info)
        html += build_section_o_mvb(brand_info) 

    if data_A:
        html += build_a1_philosophy(data_A)
        html += build_a2_core_identity(data_A)
        html += build_a3_story(data_A)
        html += build_a4_verbal_toolkit(data_A)
        html += build_a5_positioning(data_A)
        html += build_a6_promise(data_A)

    if data_B:
        html += build_b1_target_profile(data_B)
        html += build_b2_persona_detail(data_B)
        html += build_b3_customer_journey(data_B)
        html += build_b4_customer_swot(data_B)
        html += build_b5_business_model(data_B)

    if data_C:
        html += build_c1_color_system(data_C)
        html += build_c2_typography(data_C)
        html += build_c3_visual_mood(data_C)

    if data_DE:
        html += build_d_logo_identity(data_DE, logo_path)
        html += build_e_character_guide(data_DE, char_path)

    if brand_dna:
        html += build_brand_dna_summary(brand_dna, integrity_report or {}, decision_traces or [])

    html += "</body>\n</html>"
    return html


def _list_cards(items, label):
    cards = ""
    for item in items or []:
      if isinstance(item, dict):
        cards += f"<div class='card'><div class='c-ttl'>{e(item.get('point', item.get('title', '')))}</div><div class='c-body'>{e(item.get('evidence', item.get('description', '')))}</div><div class='c-body' style='color:var(--sd); margin-top:6px;'>{e(item.get('implication', item.get('rationale', '')))}</div></div>"
    return cards or f"<div class='card'><div class='c-body'>{label} 데이터가 아직 없습니다.</div></div>"


def _section_data(data, wrapper_key):
    if not isinstance(data, dict):
        return {}
    wrapped = data.get(wrapper_key)
    return wrapped if isinstance(wrapped, dict) else data


def build_b4_customer_swot(B_data):
    data = _section_data(B_data, 'data_b')
    swot = data.get('customer_swot', {})
    if not isinstance(swot, dict) or not swot:
      swot = data
    columns = [("Strengths", "강점", swot.get("strengths", [])), ("Weaknesses", "약점", swot.get("weaknesses", [])), ("Opportunities", "기회", swot.get("opportunities", [])), ("Threats", "위협", swot.get("threats", []))]
    quadrants = "".join(f"<div><div class='c-lbl'>{title} · {ko}</div>{_list_cards(items, ko)}</div>" for title, ko, items in columns)
    responses = "".join(f"<div class='promise-block'><div class='ch'>{e(item.get('swot_type', ''))} · {e(item.get('customer_issue', ''))}</div><div class='ct'><b>Brand Response:</b> {e(item.get('brand_response', ''))}<br><b>Expected Effect:</b> {e(item.get('expected_effect', ''))}</div></div>" for item in swot.get('brand_responses', []))
    return f"""<div class='section'><div class='sec-hdr'><span class='sec-num'>Section B-4 · Customer SWOT</span><span class='sec-title'>고객의 현재 상태와 전략적 대응</span><span class='sec-sub'>{e(swot.get('strategic_reasoning', ''))}</span></div><div class='grid-2'>{quadrants}</div><div class='c-lbl'>Strategic Response · 브랜드 대응</div>{responses or '<div class="card">등록된 대응이 없습니다.</div>'}</div>"""


def build_b5_business_model(B_data):
  data = _section_data(B_data, 'data_b')
  model = data.get('business_model', {})
  if not isinstance(model, dict) or not model:
    model = data
  keys = [("Customer Problem", "customer_problem"), ("Value Proposition", "value_proposition"), ("Free Experience", "free_experience"), ("Paid Value", "paid_value"), ("Retention", "retention_loop"), ("Referral", "referral_loop")]
  flow = "".join(f"<div class='card'><div class='c-lbl'>{label}</div><div class='c-ttl'>{e(model.get(key, {}).get('title', ''))}</div><div class='c-body'>{e(model.get(key, {}).get('description', ''))}</div></div>" for label, key in keys)
  hypotheses = "".join(f"<div class='promise-block'><div class='ch'>Hypothesis</div><div class='ct'>{e(item.get('hypothesis', ''))}<br><b>Why:</b> {e(item.get('why_it_matters', ''))}<br><b>Validation:</b> {e(item.get('validation_method', ''))}</div></div>" for item in model.get('business_hypotheses', []))
  return f"""<div class='section'><div class='sec-hdr'><span class='sec-num'>Section B-5 · Business Model</span><span class='sec-title'>고객 가치에서 사업 가치로</span><span class='sec-sub'>{e(model.get('business_model_summary', '검증 전 사업 모델 가설'))}</span></div><div class='grid-2'>{flow}</div><div class='c-lbl'>Business Hypotheses · 검증이 필요한 가설</div>{hypotheses or '<div class="card">등록된 사업 가설이 없습니다.</div>'}</div>"""


def _value_label(key):
  return str(key).replace('_', ' ').strip().title()


def _render_structured_value(value, depth=0):
  if isinstance(value, dict):
    rows = []
    for key, child in value.items():
      rows.append(
        f"<div style='margin:4px 0 4px {depth * 10}px;'><strong>{e(_value_label(key))}</strong>: {_render_structured_value(child, depth + 1)}</div>"
      )
    return ''.join(rows) or '<span style="color:var(--text-muted);">-</span>'
  if isinstance(value, list):
    items = ''.join(f"<li>{_render_structured_value(item, depth + 1)}</li>" for item in value)
    return f"<ul style='margin:4px 0 4px 16px;'>{items}</ul>" if items else '<span style="color:var(--text-muted);">-</span>'
  return e(value) or '<span style="color:var(--text-muted);">-</span>'


def build_brand_dna_summary(dna, integrity_report, decision_traces=None):
  sections = []
  for key in ["foundation", "why", "who", "promise", "position", "voice", "visual", "behavior", "business"]:
    value = dna.get(key, {}) if isinstance(dna, dict) else {}
    sections.append(f"<div class='card'><div class='c-lbl'>{e(key.upper())}</div><div class='c-body'>{_render_structured_value(value)}</div></div>")
  status = e(integrity_report.get('status', 'NOT_CHECKED'))
  trace_html = "".join(
    f"<div class='promise-block'><div class='ch'>{e(trace.get('stage', ''))} · {e(trace.get('decision_type', ''))} · {e(trace.get('status', ''))}</div><div class='ct'><b>User Input:</b> {e(trace.get('user_input', ''))}<br><b>AI Interpretation:</b> {e(trace.get('ai_interpretation', ''))}<br><b>Brand Decision:</b> {e(trace.get('brand_decision', ''))}<br><b>Rationale:</b> {e(trace.get('rationale', ''))}</div></div>"
    for trace in (decision_traces or [])
  )
  appendix = f"""<div class='section'><div class='sec-hdr'><span class='sec-num'>Appendix · Internal Review</span><span class='sec-title'>내부 검토용 결정 기록</span><span class='sec-sub'>브랜드 결과를 추적하기 위한 내부 기록입니다. 고객용 핵심 가이드와 구분해 보관합니다.</span></div>{trace_html or '<div class="card">기록된 Decision Trace가 없습니다.</div>'}</div>"""
  return f"""<div class='section'><div class='sec-hdr'><span class='sec-num'>Brand DNA · Summary</span><span class='sec-title'>브랜드 DNA 요약</span><span class='sec-sub'>확정된 브랜드 기준과 전략 결과를 사람이 읽을 수 있는 형태로 정리합니다.</span></div><div class='grid-2'>{''.join(sections)}</div><div class='hl-box'><b>Brand Integrity Check · {status}</b></div></div>{appendix}"""

# HTML 이스케이프 함수: 브랜드 정보나 AI 분석 결과에 특수문자가 포함되어 있을 때 레이아웃이 깨지는 것을 방지하기 위해 사용합니다.
def e(text):
    """HTML 특수문자를 이스케이프 처리하여 렌더링 오류(레이아웃 깨짐)를 방지합니다."""
    if not text:
        return ""
    # 텍스트가 아닌 숫자/불리언 값일 경우를 대비해 문자열로 변환
    text = str(text) 
    # HTML에서 문제를 일으키는 3대장 특수문자 변환
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


# [Page 1] PDF 커버 페이지 (매거진 스타일)
def build_cover(brand_info):
    """PDF 커버 페이지 생성 (매거진 스타일)"""
    year = datetime.datetime.now().year
    
    bn = e(brand_info.get('brand_name', ''))
    bne = e(brand_info.get('brand_name_en', ''))
    meaning = e(brand_info.get('name_meaning', ''))
    slogan = e(brand_info.get('slogan', ''))
    
    return f"""
<div class="cover">
  <div class="deco deco1"></div>
  <div class="deco deco2"></div>
  
  <div class="cv-year">Brand Identity Guide · {year}</div>
  
  <div class="cv-content">
    <span class="cv-tag">Brand Identity</span>
    <div class="cv-brand">{bn}</div>
    <div class="cv-en">{bne}</div>
    <div class="cv-div"></div>
    <div class="cv-meaning">{meaning}</div>
    <div class="cv-slogan">"{slogan}"</div>
  </div>
</div>
"""

# [Page 2] Section O. 기초 브랜드 정체성 (MVB Core Assets)
def build_section_o_mvb(brand_info):
    bn = e(brand_info.get('brand_name', ''))
    bne = e(brand_info.get('brand_name_en', ''))
    meaning = e(brand_info.get('name_meaning', ''))
    slogan = e(brand_info.get('slogan', ''))
    summary = e(brand_info.get('story_summary', ''))
    
    seed = e(brand_info.get('seed_color', ''))
    seed_r = e(brand_info.get('seed_color_reason', ''))

    return f"""
<div class="section">
  <div class="sec-hdr">
    <span class="sec-num">Section O · MVB Foundation</span>
    <span class="sec-title">기초 브랜드 정체성</span>
    <span class="sec-sub">창업가 인터뷰를 통해 도출된 {bn}의 핵심 뼈대 자산입니다.</span>
  </div>

  <div class="hl-box" style="margin-bottom: 28px;">
    <div class="c-lbl" style="color: rgba(0,0,0,0.4); margin-bottom: 10px;">Core Narrative · 핵심 방향성</div>
    <p style="font-size: 14.5px; line-height: 1.8; color: var(--text-main); font-weight: 500;">
      {summary}
    </p>
  </div>

  <div class="c-lbl" style="margin-bottom: 14px;">Selected Brand Identity · 확정 자산 항목</div>
  <div class="o-identity-rows" style="display:flex; flex-direction:column; gap:12px; align-items:center; margin-bottom: 16px;">
    <div class="card" style="width:88%; text-align:center; padding:18px;">
      <div class="c-lbl">Brand Name & Meaning</div>
      <div class="c-ttl" style="font-size: 42px; font-family: 'Noto Serif KR', serif; margin-top: 6px; margin-bottom: 8px; color: var(--sd); text-align:center;">
        {bn}
        <div style="font-family: 'Noto Sans KR', sans-serif; font-weight: 400; color: var(--text-muted); font-size: 13px; margin-top:6px; letter-spacing: 1px;">{bne}</div>
      </div>
      <div class="c-body" style="color: var(--text-main); font-weight: 500; font-size: 13px; margin-top:6px;">
        {meaning}
      </div>
    </div>

    <div class="card" style="width:88%; text-align:center; padding:16px;">
      <div class="c-lbl">Brand Slogan</div>
      <div class="c-ttl" style="font-family: 'Noto Serif KR', serif; font-size: 18px; font-weight: 700; color: var(--text-main); margin-top: 12px; margin-bottom: 6px; line-height: 1.4; text-align:center;">
        "{slogan}"
      </div>
      <div class="c-body" style="font-size: 12px; color: var(--text-muted);">
        * 모든 대고객 커뮤니케이션과 마케팅 컨셉의 언어적 기준이 되는 문장입니다.
      </div>
    </div>

    <div class="card" style="width:88%; text-align:center; margin-top: 0; padding:14px;">
      <div class="c-lbl">Primary Seed Color</div>
      <div style="display: flex; align-items: center; gap: 12px; margin-top: 10px; justify-content:center;">
        <div style="width: 44px; height: 44px; border-radius: 50%; background: {seed}; border: 1px solid rgba(0,0,0,0.08); flex-shrink: 0; box-shadow: inset 0 2px 4px rgba(0,0,0,0.02);"></div>
        <div>
          <div style="font-family: monospace; font-size: 16px; font-weight: 700; color: var(--text-main); letter-spacing: 0.5px;">{seed}</div>
          <div style="font-size: 13px; color: var(--text-muted); margin-top: 3px; line-height: 1.5;">{seed_r}</div>
        </div>
      </div>
    </div>

  </div>
</div>
"""
# [Page 3] Section A-1. 브랜드 철학 및 에센스 (Philosophy & Essence)
def build_a1_philosophy(A_data):
    if isinstance(A_data, (tuple, list)):
        merged_data = {}
        for part in A_data:
            if isinstance(part, dict):
                merged_data.update(part)
        A_data = merged_data

    # 데이터 추출
    phil = A_data.get('brand_philosophy', {})
    essence = A_data.get('brand_essence', {})
    
    mani = e(phil.get('manifesto', ''))
    raison = e(phil.get('raison_detre', ''))
    ag = phil.get('stand_against', [])
    fo = phil.get('stand_for', [])
    
    ess_kw = e(essence.get('keyword', ''))
    ess_defn = e(essence.get('brand_definition', ''))
    ess_exp = e(essence.get('keyword_explanation', ''))

    # 거부(Against) / 지지(For) 가치 태그 생성
    ag_tags = "".join(f'<span class="tag" style="background: #FFF5F5; color: #C53030; border-color: #FEB2B2;">{e(t)}</span>' for t in ag)
    fo_tags = "".join(f'<span class="tag" style="background: #F0FFF4; color: #22543D; border-color: #9AE6B4;">{e(t)}</span>' for t in fo)

    return f"""
<div class="section">
  <div class="sec-hdr">
    <span class="sec-num">Section A-1 · Philosophy & Essence</span>
    <span class="sec-title">브랜드 철학 및 에센스</span>
    <span class="sec-sub">{ess_defn if ess_defn else "브랜드가 존재하는 이유와 세상을 바라보는 관점을 정의합니다."}</span>
  </div>

  <div class="hl-box" style="margin-bottom: 24px;">
    <div class="c-lbl" style="color: rgba(0,0,0,0.4); margin-bottom: 12px;">Manifesto · 철학 선언문</div>
    <p style="white-space: pre-wrap; font-size: 14px; line-height: 2.1; color: var(--text-main); font-weight: 400; letter-spacing: -0.01em;">
      {mani}
    </p>
  </div>

  <div class="card" style="margin-bottom: 24px;">
    <div class="c-lbl">Raison d'être · 존재 이유</div>
    <div class="c-ttl" style="font-family: 'Noto Serif KR', serif; font-size: 16px; color: var(--sd); margin-top: 4px; margin-bottom: 4px; font-weight: 600;">
      {raison}
    </div>
  </div>

  <div class="grid-2" style="margin-bottom: 28px;">
    <div class="card">
      <div class="c-lbl" style="color: #C53030; font-weight: 700;">Stand Against · 우리가 거부하는 것</div>
      <div class="tags" style="margin-top: 12px; gap: 6px;">
        {ag_tags}
      </div>
    </div>
    
    <div class="card">
      <div class="c-lbl" style="color: #22543D; font-weight: 700;">Stand For · 우리가 지지하는 것</div>
      <div class="tags" style="margin-top: 12px; gap: 6px;">
        {fo_tags}
      </div>
    </div>
  </div>

  <div style="border-top: 1px solid var(--border-light); padding-top: 16px; margin-top: 24px;">
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
      <span class="c-lbl" style="margin-bottom: 0;">Core Brand Essence</span>
      <span style="font-family: 'Noto Serif KR', serif; font-size: 18px; font-weight: 700; color: var(--sd); letter-spacing: 2px;">{ess_kw}</span>
    </div>
    <div style="font-size: 12.5px; color: var(--text-muted); line-height: 1.6; text-align: justify; padding-left: 2px;">
      {ess_exp}
    </div>
  </div>
"""

# [Page 4] Section A-2. 기업 코어 아이덴티티 (Mission, Vision, Values)
def build_a2_core_identity(A_data):
    if isinstance(A_data, (tuple, list)):
        merged_data = {}
        for part in A_data:
            if isinstance(part, dict):
                merged_data.update(part)
        A_data = merged_data

    # 데이터 추출
    ci = A_data.get('core_identity', {})
    mission = e(ci.get('mission', ''))
    vision = e(ci.get('vision', ''))
    vals = ci.get('core_values', [])
    
    # 3대 핵심 가치 테이블 로우(Row) 생성
    val_rows = ""
    for v in vals:
        val_rows += f"""
    <tr>
      <td style="width: 22%;"><strong>{e(v.get('value', ''))}</strong></td>
      <td style="width: 33%; color: var(--text-main); font-weight: 500;">{e(v.get('description', ''))}</td>
      <td style="color: #444; font-size: 12.5px; line-height: 1.65;">{e(v.get('example', ''))}</td>
    </tr>"""

    return f"""
<div class="section">
  <div class="sec-hdr">
    <span class="sec-num">Section A-2 · Corporate Identity</span>
    <span class="sec-title">기업 코어 아이덴티티</span>
    <span class="sec-sub">브랜드가 나아갈 궁극적인 지향점과 조직 내부의 행동 기준을 정의합니다.</span>
  </div>

  <div class="grid-2" style="margin-bottom: 36px;">
    
    <div class="card" style="border-top: 4px solid var(--sd);">
      <div class="c-lbl" style="color: var(--sd); font-weight: 700; margin-bottom: 4px;">Mission · 우리의 사명</div>
      <div style="font-size: 11px; color: var(--text-muted); margin-bottom: 14px; font-weight: 400;">우리가 지금 매일 세상에 제공하고 있는 실질적인 가치</div>
      <div class="c-body" style="font-size: 13.5px; font-weight: 500; color: var(--text-main); line-height: 1.6;">
        {mission}
      </div>
    </div>
    
    <div class="card" style="border-top: 4px solid var(--sd);">
      <div class="c-lbl" style="color: var(--sd); font-weight: 700; margin-bottom: 4px;">Vision · 우리의 비전</div>
      <div style="font-size: 11px; color: var(--text-muted); margin-bottom: 14px; font-weight: 400;">5~10년 후 브랜드가 도달하고자 하는 궁극적인 위상</div>
      <div class="c-body" style="font-size: 13.5px; font-weight: 500; color: var(--text-main); line-height: 1.6;">
        {vision}
      </div>
    </div>
    
  </div>

  <div class="c-lbl" style="margin-bottom: 12px; color: var(--text-main); font-weight: 700;">Core Values · 3대 핵심 가치</div>
  <table class="data-table">
    <thead>
      <tr>
        <th>핵심 가치</th>
        <th>의미 및 가이드라인</th>
        <th>실무 구현 예시 (Action Item)</th>
      </tr>
    </thead>
    <tbody>
      {val_rows if val_rows else "<tr><td colspan='3' style='text-align:center; color:var(--text-muted);'>등록된 핵심 가치가 없습니다.</td></tr>"}
    </tbody>
  </table>
</div>
"""

# [Page 5] Section A-3. 브랜드 스토리 전문 (Brand Story Narrative)
def build_a3_story(A_data):
    if isinstance(A_data, (tuple, list)):
        merged_data = {}
        for part in A_data:
            if isinstance(part, dict):
                merged_data.update(part)
        A_data = merged_data

    story_text = A_data.get('brand_story_full', '')
    if not story_text and 'brand_story' in A_data:
        raw_story = A_data.get('brand_story', '')
        story_text = raw_story.get('brand_story', '') if isinstance(raw_story, dict) else raw_story

    first_paragraph = next((p.strip() for p in str(story_text).split('\n') if p.strip()), '')
    highlight_quote = first_paragraph[:140] or "브랜드가 세상에 전하고 싶은 핵심 이야기"

    raw_paras = [p for p in str(story_text).split('\n')]
    paras = []
    for p in raw_paras:
      if not p or not p.strip():
        continue
      # 선행에 붙은 불필요한 마크(#, -, ─ 등)를 방어적으로 제거
      cleaned = p.strip().lstrip('#-–— ').strip()
      if cleaned:
        paras.append(cleaned)
    
    story_html = ""
    for i, p in enumerate(paras):
      # 중앙 통제된 .story p 규격을 사용
      story_html += f'<p>{e(p)}</p>'

    return f"""
<div class="section">
  <div class="sec-hdr" style="margin-bottom: 36px;">
    <span class="sec-num">Section A-3 · Brand Story Narrative</span>
    <span class="sec-title">브랜드 스토리 전문</span>
    <span class="sec-sub">브랜드의 탄생 서사와 존재 명분을 하나의 완성된 에세이로 전달합니다.</span>
  </div>

  <div style="text-align: center; padding: 32px 20px; margin-bottom: 36px; border-left: 3px solid var(--sd); background: rgba(0,0,0,0.01); border-radius: 0 12px 12px 0;">
    <span style="font-size: 32px; font-family: 'Noto Serif KR', serif; color: var(--sd); line-height: 1; display: block; margin-bottom: -10px; opacity: 0.3;">“</span>
    <div style="font-family: 'Noto Serif KR', serif; font-size: 18px; font-weight: 600; color: var(--sd); line-height: 1.6; font-style: italic;">
      {highlight_quote}
    </div>
    <span style="font-size: 32px; font-family: 'Noto Serif KR', serif; color: var(--sd); line-height: 1; display: block; margin-top: 6px; margin-bottom: -20px; opacity: 0.3;">”</span>
  </div>

  <div style="margin-bottom: 20px; padding-left: 6px;">
    <span style="font-size: 11px; font-weight: 700; color: var(--text-muted); letter-spacing: 2px; text-transform: uppercase; display: block; margin-bottom: 4px;">Chapter 01. Narrative</span>
    <h3 style="font-family: 'Noto Serif KR', serif; font-size: 20px; font-weight: 700; color: var(--text-main);">브랜드가 시작된 이유</h3>
  </div>

  <div class="story" style="background: var(--surface); border: 1px solid var(--border-light); border-radius: 14px; padding: 24px 28px; box-shadow: 0 4px 18px rgba(0,0,0,0.012);">
    {story_html if story_html else "<p style='text-align: center; color: var(--text-muted);'>내용이 존재하지 않습니다.</p>"}
    
    <div style="margin-top: 40px; border-top: 1px dashed var(--border-light); padding-top: 16px; text-align: right;">
      <span style="font-family: 'Noto Serif KR', serif; font-size: 13px; font-style: italic; color: var(--text-muted);">Written by NameTag AI Brand Director</span>
    </div>
  </div>
</div>
"""
# [Page 6] Section A-4. 언어적 자산 및 슬로건 툴킷 (Verbal Identity Toolkit)
def build_a4_verbal_toolkit(A_data):
    if isinstance(A_data, (tuple, list)):
        merged_data = {}
        for part in A_data:
            if isinstance(part, dict):
                merged_data.update(part)
        A_data = merged_data

    # 데이터 하위 딕셔너리 안전 추출
    ne = A_data.get('naming_expansion', {})
    se = A_data.get('slogan_expansion', {})

    # 변수 매핑 및 이스케이프 안전장치 처리
    name_story = e(ne.get('name_story', ''))
    main_slogan_en = e(se.get('main_slogan_en', ''))
    alts = ne.get('alternative_names', [])
    subs = se.get('sub_slogans', [])
    domains = ne.get('domain_suggestions', [])
    sns = ne.get('sns_handles', [])

    # 1. 대안 네이밍 리스트 HTML 생성
    alt_html = ""
    for a in alts:
        alt_html += f"""
    <div style="margin-bottom: 12px; padding-bottom: 10px; border-bottom: 1px dashed var(--border-light);">
      <div style="font-size: 13.5px; font-weight: 700; color: var(--text-main);">{e(a.get('name', ''))} <span style="font-size: 11px; font-weight: 400; color: var(--text-muted); font-family: monospace;">/{e(a.get('name_en', ''))}</span></div>
      <div style="font-size: 12px; color: #555; margin-top: 5px; line-height: 1.5; text-align: justify;">{e(a.get('rationale', ''))}</div>
    </div>"""
    if not alt_html:
        alt_html = "<div style='color: var(--text-muted); font-size: 12px; padding: 10px 0;'>추천 대안 네이밍 자산이 없습니다.</div>"

    # 2. 서브 슬로건 불릿 리스트 HTML 생성 (.custom-list 스타일 적용)
    sub_items_html = ""
    for s in subs:
        sub_items_html += f"""
    <li>
      {e(s.get('slogan', ''))}
      <span class="note">💡 활용처: {e(s.get('emphasis', ''))}</span>
    </li>"""

    # 3. 최하단 디지털 자산 태그 칩 생성
    dom_chips = "".join(f'<span class="tag" style="border-color: var(--border-strong); background: var(--surface); margin-right: 5px; margin-bottom: 6px; font-family: monospace; font-size: 11px;">{e(d)}</span>' for d in domains)
    sns_chips = "".join(f'<span class="tag" style="border-color: var(--border-strong); background: var(--surface); margin-right: 5px; margin-bottom: 6px; font-family: monospace; font-size: 11px;">{e(s)}</span>' for s in sns)

    return f"""
<div class="section" style="page-break-inside: avoid; break-inside: avoid-page;">
  <div class="sec-hdr" style="margin-bottom: 24px;">
    <span class="sec-num">Section A-4 · Verbal Identity</span>
    <span class="sec-title">언어적 자산 및 슬로건 툴킷</span>
    <span class="sec-sub">브랜드의 정당성을 증명하는 네이밍 서사와 대고객 접점용 슬로건 라이브러리입니다.</span>
  </div>

  <div class="slogan-box" style="padding: 18px 14px; margin: 0 0 18px 0;">
    <div class="sl-en" style="font-size: 16.5px; font-weight: 600; color: var(--sd); font-style: normal; letter-spacing: 0.04em; text-transform: uppercase;">
      {main_slogan_en if main_slogan_en else "등록된 영문 슬로건이 없습니다."}
    </div>
    <div style="font-size: 10px; color: var(--text-muted); margin-top: 6px; letter-spacing: 2px; text-transform: uppercase; font-weight: 700;">Global Verbal Slogan</div>
  </div>

  <div style="display:flex; flex-direction:column; gap:12px; align-items:center; margin-bottom: 20px;">
    <div class="card" style="width:88%; padding: 16px; text-align:center;">
      <div class="c-lbl">Name Story · 네이밍 서사</div>
      <div class="c-body" style="font-size: 13px; line-height: 1.75; color: var(--text-main); margin-top: 8px; text-align: center;">
        {name_story if name_story else '<span style="color:var(--text-muted);">등록된 네이밍 서사가 없습니다.</span>'}
      </div>
    </div>

    <div class="card" style="width:88%; padding: 14px; text-align:center;">
      <div class="c-lbl">Alternative Names · 후보 대안군</div>
      <div class="alt-grid" style="display:grid; grid-template-columns: repeat(2, 1fr); gap:12px; margin-top:8px; justify-items:center; align-items:start; width:100%;">
        {alt_html}
      </div>
    </div>
  </div>

  <div class="c-lbl" style="margin-bottom: 10px; color: var(--text-main); font-weight: 700;">Sub Slogans · 상황별 변형 카피라이팅</div>
  <ul class="custom-list" style="margin-top: 0; margin-bottom: 24px;">
    {sub_items_html if sub_items_html else "<li><span class='note'>등록된 상황별 슬로건 자산이 없습니다.</span></li>"}
  </ul>

  <div class="grid-2" style="border-top: 1px solid var(--border-light); padding-top: 12px; page-break-inside: avoid; break-inside: avoid-page;">
    <div class="card domains-box centered-card" style="padding:12px;">
      <div class="c-lbl" style="margin-bottom: 6px; color: var(--text-muted);">Recommended Brand Domains</div>
      <div class="tags" style="margin-top: 0;">{dom_chips if dom_chips else "<span style='font-size:12px; color:var(--text-muted);'>-</span>"}</div>
    </div>
    <div class="card sns-box centered-card" style="padding:12px;">
      <div class="c-lbl" style="margin-bottom: 6px; color: var(--text-muted);">Official SNS Handles</div>
      <div class="tags" style="margin-top: 0;">{sns_chips if sns_chips else "<span style='font-size:12px; color:var(--text-muted);'>-</span>"}</div>
    </div>
  </div>
</div>
"""

# [Page 7] Section A-5. 시장 포지셔닝 전략 (Market Positioning Strategy)
def build_a5_positioning(A_data):
    if isinstance(A_data, (tuple, list)):
        merged_data = {}
        for part in A_data:
            if isinstance(part, dict):
                merged_data.update(part)
        A_data = merged_data

    # 💡 방어적 코드 2: 선택된 포지셔닝 키를 종속성 없이 깊은 탐색(Deep Search)으로 자동 추출
    pos = A_data.get('positioning', {})
    if not pos:
        # 후보군 내부 스캔
        for key in ['candidate_1_ethereal_brilliance', 'candidate_2_warm_sanctuary', 'candidate_3_ethical_intellectual']:
            if key in A_data and 'positioning' in A_data[key]:
                pos = A_data[key]['positioning']
                break
    if not pos:
        # 동적 키 스캔 백업
        for k, v in A_data.items():
            if 'candidate' in k and isinstance(v, dict) and 'positioning' in v:
                pos = v['positioning']
                break

    # 데이터 매핑 및 이스케이프 이중 안전장치
    stmt = e(pos.get('statement', ''))
    diffs = pos.get('differentiators', [])
    
    # 포지셔닝 맵 스키마 변형 대응 (positioning_map 또는 positioning_map_visualized)
    pmap = pos.get('positioning_map_visualized', {}) if 'positioning_map_visualized' in pos else pos.get('positioning_map', {})
    axis_x = e(pmap.get('axis_x', ''))
    axis_y = e(pmap.get('axis_y', ''))
    quad_desc = e(pmap.get('quadrants_description', ''))
    our_pos = e(pmap.get('our_exact_position', '')) if 'our_exact_position' in pmap else e(pmap.get('our_position', ''))

    # 1. 3대 차별화 포인트(Differentiators) 테이블 데이터 빌드
    diff_rows = ""
    for i, dd in enumerate(diffs, 1):
        diff_rows += f"""
    <tr>
      <td style="width: 32%; font-weight: 700; color: var(--text-main);">
        <span class="badge" style="background: var(--sd); margin-right: 6px;">0{i}</span>{e(dd.get('point', ''))}
      </td>
      <td style="color: #444; font-size: 12.5px; line-height: 1.65; text-align: justify;">
        {e(dd.get('description', ''))}
      </td>
    </tr>"""
    if not diff_rows:
        diff_rows = "<tr><td colspan='2' style='text-align:center; color:var(--text-muted);'>도출된 차별화 전략 자산이 없습니다.</td></tr>"

    return f"""
<div class="section">
  <div class="sec-hdr" style="margin-bottom: 24px;">
    <span class="sec-num">Section A-5 · Market Positioning</span>
    <span class="sec-title">시장 포지셔닝 전략</span>
    <span class="sec-sub">전체 산업 생태계 안에서 브랜드가 독점할 영토와 타겟 설득을 위한 차별적 경쟁 우위를 정의합니다.</span>
  </div>

  <div class="hl-box" style="margin-bottom: 24px; padding: 22px 28px;">
    <div class="c-lbl" style="color: rgba(0,0,0,0.4); margin-bottom: 8px;">Positioning Statement · 가치 제안 선언</div>
    <p style="font-size: 13.5px; font-weight: 600; line-height: 1.7; color: var(--text-main); text-align: justify; margin-bottom: 0;">
      {stmt}
    </p>
  </div>

  <div class="c-lbl" style="margin-bottom: 10px; color: var(--text-main); font-weight: 700;">Differentiators · 3대 차별화 팩트</div>
  <table class="data-table" style="margin-bottom: 24px;">
    <thead>
      <tr>
        <th>차별화 핵심 가치</th>
        <th>실제 시장 진입 및 판매 전략의 근거</th>
      </tr>
    </thead>
    <tbody>
      {diff_rows}
    </tbody>
  </table>

  <div class="card" style="padding: 24px 26px;">
    <div class="c-lbl" style="margin-bottom: 14px;">Strategic Positioning Map · 4사분면 포지셔닝 맵</div>
    
    <div class="grid-2" style="margin-bottom: 16px; gap: 16px;">
      <div style="background: rgba(0,0,0,0.01); border-radius: 8px; padding: 10px 14px; border-left: 2px solid var(--text-muted);">
        <strong style="font-size: 11px; color: var(--sd); text-transform: uppercase; letter-spacing: 1px; display: block; margin-bottom: 2px;">X-Axis (가로축 기준)</strong>
        <span style="font-size: 12.5px; color: var(--text-main); font-weight: 500;">{axis_x}</span>
      </div>
      <div style="background: rgba(0,0,0,0.01); border-radius: 8px; padding: 10px 14px; border-left: 2px solid var(--text-muted);">
        <strong style="font-size: 11px; color: var(--sd); text-transform: uppercase; letter-spacing: 1px; display: block; margin-bottom: 2px;">Y-Axis (세로축 기준)</strong>
        <span style="font-size: 12.5px; color: var(--text-main); font-weight: 500;">{axis_y}</span>
      </div>
    </div>

    <div style="font-size: 12px; color: var(--text-muted); line-height: 1.6; margin-bottom: 18px; text-align: justify; padding-left: 2px;">
      <strong>시장 매트릭스 구도:</strong> {quad_desc}
    </div>

    <div style="background: var(--sl); border-radius: 10px; padding: 16px 20px; border: 1px solid rgba(0,0,0,0.02);">
      <strong style="font-size: 11px; color: var(--sd); text-transform: uppercase; letter-spacing: 1px; display: block; margin-bottom: 4px;">Our Absolute Position · 우리의 독보적 위치</strong>
      <div style="font-size: 13px; color: var(--text-main); font-weight: 600; line-height: 1.6; text-align: justify;">
        {our_pos}
      </div>
    </div>
  </div>
</div>
"""

# [Page 8] Section A-6. 타협 불가능한 약속 (Brand Promise & Action Rules)
def build_a6_promise(A_data):
    if isinstance(A_data, (tuple, list)):
        merged_data = {}
        for part in A_data:
            if isinstance(part, dict):
                merged_data.update(part)
        A_data = merged_data

    # 데이터 상위 딕셔너리 추출
    bp = A_data.get('unbreakable_brand_promise', {})
    if not bp:
        for k, v in A_data.items():
            if isinstance(v, dict) and 'unbreakable_brand_promise' in v:
                bp = v['unbreakable_brand_promise']
                break
    
    # 변수 매핑 및 이스케이프 안전장치 처리
    decl = e(bp.get('declaration', ''))
    
    # 💡 방어적 코드 2: 스키마 변형 대응 (proof_of_promise 또는 implementations 자동 감지)
    rules_list = bp.get('proof_of_promise', []) if 'proof_of_promise' in bp else bp.get('implementations', [])

    # 3대 채널별 구체적 행동 강령 블록 빌드 (.promise-block 컴포넌트 활용)
    promise_blocks = ""
    for item in rules_list:
        channel_name = e(item.get('channel', item.get('category', item.get('touchpoint', '채널 미상'))))
        rule_content = e(item.get('actionable_rule', item.get('example', item.get('rule', item.get('description', '')))))
        
        promise_blocks += f"""
  <div class="promise-block" style="margin-bottom: 20px; padding: 22px 26px;">
    <div class="ch" style="font-size: 12px; font-weight: 700; color: var(--sd); letter-spacing: 1px; margin-bottom: 8px;">
      📍 {channel_name} 실천 행동 수칙
    </div>
    <div class="ct" style="font-size: 13.5px; color: var(--text-main); line-height: 1.8; text-align: justify; font-weight: 500;">
      {rule_content}
    </div>
  </div>\n"""

    if not promise_blocks:
        promise_blocks = '<div class="card"><div class="c-body" style="text-align:center; color:var(--text-muted);">도출된 접점별 실천 수칙 수호 자산이 없습니다.</div></div>'

    return f"""
<div class="section">
  <div class="sec-hdr" style="margin-bottom: 28px;">
    <span class="sec-num">Section A-6 · Brand Promise</span>
    <span class="sec-title">타협 불가능한 약속 및 행동 수칙</span>
    <span class="sec-sub">모든 대고객 접점에서 브랜드의 신념을 증명하기 위해 반드시 준수해야 하는 실전 행동 강령입니다.</span>
  </div>

  <div class="slogan-box" style="padding: 32px 24px; margin: 0 0 32px 0;">
    <div class="sl-ko" style="font-family: 'Noto Serif KR', serif; font-size: 20px; font-weight: 700; color: var(--sd); line-height: 1.5; letter-spacing: -0.01em;">
      {decl if decl else "우리는 당신에게 항상 일상의 가장 아름다운 반짝임을 드립니다."}
    </div>
    <div style="font-size: 10px; color: var(--text-muted); margin-top: 8px; letter-spacing: 2px; text-transform: uppercase; font-weight: 700;">Brand Promise Declaration</div>
  </div>

  <div class="c-lbl" style="margin-bottom: 14px; color: var(--text-main); font-weight: 700;">Actionable Rules · 접점별 구체적 실행 지침</div>
  
  {promise_blocks}
  
</div>
"""

# [Page 9] Section B-1. 핵심 타겟 프로필 및 트리거 (Core Target & Triggers)
def build_b1_target_profile(B_data):
    if isinstance(B_data, (tuple, list)):
        merged_data = {}
        for part in B_data:
            if isinstance(part, dict):
                merged_data.update(part)
        B_data = merged_data

    # 데이터 추출
    strat_reason = e(B_data.get('strategic_reasoning', ''))
    group = B_data.get('core_target_group', {})
    triggers = B_data.get('emotional_triggers', [])

    # 타겟 그룹 세부 정보
    target_def = e(group.get('definition', ''))
    demographics = e(group.get('demographics', ''))
    keywords = group.get('lifestyle_keywords', [])
    behavior = e(group.get('consumption_behavior', ''))

    # 라이프스타일 키워드 태그 생성
    kw_tags = "".join(f'<span class="tag" style="background: var(--sl); border-color: var(--border-strong); margin-right: 5px; margin-bottom: 6px;">#{e(k)}</span>' for k in keywords)

    # 3대 감정 트리거 카드 생성
    trigger_html = ""
    for i, t in enumerate(triggers, 1):
        trigger_html += f"""
        <div class="card" style="padding: 12px 12px; border-left: 3px solid var(--sd);">
          <div style="font-size: 10.5px; font-weight: 700; color: var(--sd); margin-bottom: 4px; letter-spacing: 1px;">TRIGGER 0{i}</div>
          <div style="font-size: 12.5px; font-weight: 700; color: var(--text-main); margin-bottom: 6px;">{e(t.get('trigger', ''))}</div>
          <div style="font-size: 11.5px; color: #555; line-height: 1.45; text-align: justify;">{e(t.get('reason', ''))}</div>
        </div>"""

    return f"""
<div class="section">
  <div class="sec-hdr" style="margin-bottom: 24px;">
    <span class="sec-num">Section B-1 · Target Segmentation</span>
    <span class="sec-title">핵심 타겟 프로필 및 감정 트리거</span>
    <span class="sec-sub">브랜드의 가치에 가장 민감하게 반응하고 구매를 확정할 핵심 타겟의 심리적 지형도입니다.</span>
  </div>

  <div class="hl-box" style="margin-bottom: 24px; padding: 22px 28px;">
    <div class="c-lbl" style="color: rgba(0,0,0,0.4); margin-bottom: 8px;">Strategic Reasoning · 타겟 설정 근거</div>
    <p style="font-size: 13.5px; line-height: 1.75; color: var(--text-main); text-align: justify; margin-bottom: 0; font-weight: 500;">
      {strat_reason}
    </p>
  </div>

  <div class="grid-2" style="margin-bottom: 18px; gap: 12px; align-items: center; justify-content: center;">
    <div class="card centered-card" style="padding: 16px 18px; width:48%; margin:0 auto;">
      <div class="c-lbl">Core Target Group · 타겟 정의</div>
      <div style="font-size: 16px; font-weight: 700; color: var(--sd); margin-top: 8px; margin-bottom: 6px; font-family: 'Noto Serif KR', serif;">
        {target_def}
      </div>
      <div style="font-size: 12.5px; color: var(--text-muted); line-height: 1.5;">{demographics}</div>
      
      <div class="c-lbl" style="margin-top: 20px; margin-bottom: 10px;">Lifestyle Keywords</div>
      <div class="tags" style="margin-top: 0;">{kw_tags if kw_tags else "-"}</div>
    </div>
    
    <div class="card centered-card" style="padding: 16px 18px; width:48%; margin:0 auto;">
      <div class="c-lbl">Consumption Behavior · 소비 행동 특징</div>
      <div class="c-body" style="font-size: 12.5px; line-height: 1.6; color: var(--text-main); margin-top: 6px; text-align: center;">
        {behavior}
      </div>
      <div style="margin-top: 16px; padding-top: 12px; border-top: 1px dashed var(--border-light); font-size: 11px; color: var(--text-muted); font-style: italic;">
        * 이들은 단순한 제품이 아닌 '자기 정체성'을 대변하는 도구를 구매합니다.
      </div>
    </div>
  </div>

  <div class="c-lbl" style="margin-bottom: 12px; color: var(--text-main); font-weight: 700;">Emotional Triggers · 3대 구매 결정 트리거</div>
  <div class="triggers-grid">
  {trigger_html}
  </div>
</div>
"""

# [Page 10] Section B-2. 가상 페르소나 상세 분석 (Persona Deep Dive)
def build_b2_persona_detail(B_data):
    if isinstance(B_data, (tuple, list)):
        merged_data = {}
        for part in B_data:
            if isinstance(part, dict):
                merged_data.update(part)
        B_data = merged_data

    # 1. 메인 페르소나 (Primary Persona) 데이터 추출
    prim = B_data.get('primary_persona', {})
    p_name = e(prim.get('name', ''))
    p_desc = e(prim.get('age_and_job', ''))
    p_scene = e(prim.get('daily_scene', ''))
    p_pain = e(prim.get('pain_point_and_desire', ''))
    p_needs = prim.get('emotional_needs', [])
    p_deal = e(prim.get('deal_breaker', ''))

    # 감정적 니즈 태그 렌더링
    need_tags = "".join(f'<span class="tag" style="background: var(--surface); border-color: var(--border-strong); margin-right: 6px; margin-bottom: 6px;">{e(n)}</span>' for n in p_needs)

    # 2. 서브 페르소나 (Secondary Personas) 데이터 빌드
    secs = B_data.get('secondary_personas', [])
    sec_cards = ""
    for s in secs:
        sec_cards += f"""
    <div class="card" style="padding: 18px 20px;">
      <div style="font-size: 13.5px; font-weight: 700; color: var(--text-main); margin-bottom: 2px;">{e(s.get('name_and_demographic', ''))}</div>
      <div style="font-size: 11px; color: var(--sd); font-weight: 600; margin-bottom: 8px;">[{e(s.get('character_type', ''))}]</div>
      <div style="font-size: 12px; color: #555; line-height: 1.6; text-align: justify; margin-top: 8px; border-top: 1px dashed var(--border-light); padding-top: 8px;">
        <span style="font-weight: 600; color: var(--text-main);">구매 이유:</span> {e(s.get('why_they_buy', ''))}
      </div>
    </div>"""

    if not sec_cards:
        sec_cards = "<div style='color: var(--text-muted); padding: 10px;'>등록된 확장 타겟 정보가 없습니다.</div>"

    return f"""
<div class="section">
  <div class="sec-hdr" style="margin-bottom: 24px;">
    <span class="sec-num">Section B-2 · Persona Deep Dive</span>
    <span class="sec-title">가상 페르소나 상세 분석</span>
    <span class="sec-sub">브랜드에 가장 열광할 핵심 고객 1인과, 비즈니스 확장을 견인할 4인의 전략적 페르소나입니다.</span>
  </div>

  <div class="c-lbl" style="margin-bottom: 12px; color: var(--text-main); font-weight: 700;">Primary Persona · 1순위 핵심 고객</div>
  <div class="card" style="margin-bottom: 28px; padding: 0; overflow: hidden; border: 1px solid var(--border-strong);">
    
    <div style="background: var(--sl); padding: 20px 24px; border-bottom: 1px solid var(--border-light);">
      <div style="font-size: 20px; font-family: 'Noto Serif KR', serif; font-weight: 700; color: var(--sd); display: flex; align-items: center; gap: 8px;">
        <div style="width: 8px; height: 8px; border-radius: 50%; background: var(--sd);"></div>
        {p_name}
      </div>
      <div style="font-size: 13px; color: var(--text-main); font-weight: 500; margin-top: 4px; margin-left: 16px;">
        {p_desc}
      </div>
    </div>

    <div style="padding: 24px;">
      <div style="margin-bottom: 18px;">
        <div style="font-size: 11px; color: var(--text-muted); font-weight: 700; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 6px;">Daily Scene · 일상의 한 장면</div>
        <div style="font-size: 13.5px; color: var(--text-main); font-style: italic; line-height: 1.6; border-left: 2px solid var(--sd); padding-left: 12px;">
          "{p_scene}"
        </div>
      </div>
      
      <div style="margin-bottom: 20px;">
        <div style="font-size: 11px; color: var(--text-muted); font-weight: 700; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 6px;">Pain Point & Desire · 결핍과 욕망</div>
        <div style="font-size: 13px; color: var(--text-main); line-height: 1.7; text-align: justify;">
          {p_pain}
        </div>
      </div>

      <div style="margin-bottom: 20px;">
        <div style="font-size: 11px; color: var(--text-muted); font-weight: 700; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px;">Emotional Needs · 감정적 니즈</div>
        <div class="tags" style="margin-top: 0;">{need_tags if need_tags else "-"}</div>
      </div>

      <div style="background: #FFF5F5; border-radius: 8px; padding: 16px; border-left: 3px solid #C53030;">
        <div style="font-size: 11px; color: #C53030; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 4px;">Deal Breaker · 구매 포기 트리거</div>
        <div style="font-size: 12.5px; color: #742A2A; line-height: 1.5; font-weight: 500;">
          {p_deal}
        </div>
      </div>
    </div>
  </div>

  <div class="c-lbl" style="margin-bottom: 12px; color: var(--text-main); font-weight: 700;">Secondary Personas · 확장 타겟 그룹</div>
  <div class="grid-4" style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px;">
    {sec_cards}
  </div>
</div>
"""

# [Page 11] Section B-3. 5단계 고객 여정 맵 퍼널 (Customer Journey Map)
def build_b3_customer_journey(B_data):
    if isinstance(B_data, (tuple, list)):
        merged_data = {}
        for part in B_data:
            if isinstance(part, dict):
                merged_data.update(part)
        B_data = merged_data

    # 데이터 추출
    # 💡 방어적 코드 2: 동일 딕셔너리 내에 strategic_reasoning이 중복될 경우, 
    # customer_journey_map과 쌍을 이루는 두 번째 데이터셋의 추론 서사를 우선 확보
    strat_reason = ""
    if isinstance(B_data, dict):
        # 만약 백엔드 원천 데이터가 리스트 내부 딕셔너리 파트별로 쪼개져 들어왔을 때를 대비해 탐색
        strat_reason = B_data.get('strategic_reasoning', '')
        
    journey_list = B_data.get('customer_journey_map', [])

    # 5단계 퍼널 로우(Row) 생성 (와이드 테이블 레이아웃 구조)
    journey_rows = ""
    for item in journey_list:
        stage = e(item.get('stage', ''))
        touchpoint = e(item.get('touchpoint', ''))
        emotion = e(item.get('customer_emotion', ''))
        brand_action = e(item.get('brand_action', ''))
        
        # 단계명에서 숫자와 영문 분리 표기 효과를 위해 문자열 정제 처리
        stage_display = stage.replace("(", "<br><span style='font-size:10.5px; font-weight:400; color:var(--text-muted);'>").replace(")", "</span>")

        journey_rows += f"""
    <tr>
      <td style="width: 15%; font-weight: 700; color: var(--sd); text-align: center; vertical-align: middle; background: rgba(0,0,0,0.005); border-right: 1px solid var(--border-light);">
        {stage_display}
      </td>
      <td style="width: 20%; font-weight: 500; color: var(--text-main); vertical-align: middle;">
        {touchpoint}
      </td>
      <td style="width: 28%; color: #555; font-size: 12px; font-style: italic; line-height: 1.6; text-align: justify; vertical-align: middle;">
        {emotion}
      </td>
      <td style="color: var(--text-main); font-size: 12.5px; line-height: 1.65; text-align: justify; vertical-align: middle;">
        {brand_action}
      </td>
    </tr>"""

    if not journey_rows:
        journey_rows = "<tr><td colspan='4' style='text-align:center; color:var(--text-muted);'>도출된 고객 여정 맵 퍼널 자산이 없습니다.</td></tr>"

    return f"""
<div class="section">
  <div class="sec-hdr" style="margin-bottom: 24px;">
    <span class="sec-num">Section B-3 · Customer Journey</span>
    <span class="sec-title">5단계 고객 여정 맵 퍼널</span>
    <span class="sec-sub">잠재 고객이 브랜드를 인지하는 시점부터 자발적 전파자가 되기까지의 전 여정별 킬러 액션 가이드라인입니다.</span>
  </div>

  <div class="hl-box" style="margin-bottom: 28px; padding: 20px 24px;">
    <div class="c-lbl" style="color: rgba(0,0,0,0.4); margin-bottom: 8px;">Funnel Strategy & Retention Timing · 퍼널 설계 및 리텐션 전략</div>
    <p style="font-size: 13px; line-height: 1.75; color: var(--text-main); text-align: justify; margin-bottom: 0; font-weight: 500;">
      {strat_reason if strat_reason else "고객의 구매 여정 곳곳에 심리적 보상 요소를 배치하고, 인테리어 권태기나 교체 주기를 고려한 핀셋 리텐션 타이밍을 설정합니다."}
    </p>
  </div>

  <div class="c-lbl" style="margin-bottom: 12px; color: var(--text-main); font-weight: 700;">Customer Journey Matrix · 여정 단계별 실행 매트릭스</div>
  <table class="data-table" style="width: 100%; border-collapse: collapse;">
    <thead>
      <tr>
        <th style="text-align: center;">여정 단계</th>
        <th>주요 터치포인트</th>
        <th>고객의 무의식적 감정 상태</th>
        <th>브랜드의 핵심 킬러 액션 (Brand Action)</th>
      </tr>
    </thead>
    <tbody>
      {journey_rows}
    </tbody>
  </table>
</div>
"""

# [Page 12] Section C-1. 브랜드 컬러 팔레트 시스템 (Color Palette System)
def build_c1_color_system(C_data):
    if isinstance(C_data, (tuple, list)):
        merged_data = {}
        for part in C_data:
            if isinstance(part, dict):
                merged_data.update(part)
        C_data = merged_data

    palette = C_data.get('color_palette', [])

    # 💡 방어적 코드 2: 역할(Role)에 따른 정밀 분류 매핑 (데이터 순서가 바뀌어도 레이아웃 고정)
    primary_color = {}
    secondary_color = {}
    sub_colors = []

    for c in palette:
        role_lower = c.get('role', '').lower()
        if 'primary' in role_lower:
            primary_color = c
        elif 'secondary' in role_lower:
            secondary_color = c
        else:
            sub_colors.append(c)

    # 만약 데이터의 키 매핑이 부족할 경우를 대비한 순서 기반 백업 로직
    if not primary_color and len(palette) > 0: primary_color = palette[0]
    if not secondary_color and len(palette) > 1: secondary_color = palette[1]
    if not sub_colors and len(palette) > 2: sub_colors = palette[2:]

    # 1. 상단 메인/서브 대형 팬톤 칩 HTML 생성
    top_chips_html = ""
    for target in [primary_color, secondary_color]:
        if target:
            c_name = e(target.get('color_name', ''))
            hex_code = e(target.get('hex_code', '#FFFFFF'))
            role = e(target.get('role', ''))
            
            top_chips_html += f"""
    <div class="card" style="padding: 0; width: 48%; border-radius: 12px; overflow: hidden; border: 1px solid var(--border-strong); box-shadow: 0 4px 10px rgba(0,0,0,0.012);">
      <div style="background: {hex_code}; height: 90px; width: 100%; border-bottom: 1px solid var(--border-light);"></div>
      <div style="padding: 12px 14px; background: #FFFFFF;">
        <div style="font-size: 10.5px; font-weight: 700; color: var(--sd); text-transform: uppercase; letter-spacing: 1px; margin-bottom: 4px;">{role}</div>
        <div style="font-family: 'Noto Serif KR', serif; font-size: 15px; font-weight: 700; color: var(--text-main);">{c_name}</div>
        <div style="font-family: monospace; font-size: 12.5px; font-weight: 700; color: #444; margin-top: 6px; letter-spacing: 0.5px; background: var(--surface); padding: 3px 6px; border-radius: 4px; display: inline-block;">{hex_code}</div>
      </div>
    </div>"""

    # 2. 하단 3종 보조 컬러 중형 팬톤 칩 HTML 생성 (3열 배치용)
    bottom_chips_html = ""
    for target in sub_colors[:3]:  # 최대 3개까지만 제한하여 레이아웃 방어
        c_name = e(target.get('color_name', ''))
        hex_code = e(target.get('hex_code', '#FFFFFF'))
        role = e(target.get('role', ''))
        
        bottom_chips_html += f"""
    <div class="card" style="padding: 0; border-radius: 10px; overflow: hidden; border: 1px solid var(--border-light);">
      <div style="background: {hex_code}; height: 48px; width: 100%; border-bottom: 1px solid var(--border-light);"></div>
      <div style="padding: 8px 10px; background: #FFFFFF;">
        <div style="font-size: 9.5px; font-weight: 700; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 2px;">{role}</div>
        <div class="color-name-small" style="font-weight:700; color:var(--text-main); white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{c_name}</div>
        <div class="color-hex-small" style="font-family: monospace; font-weight:700; color:#555; margin-top:6px; background: rgba(0,0,0,0.02); padding:2px 6px; border-radius:4px; display:inline-block;">{hex_code}</div>
      </div>
    </div>"""

    # 3. 최하단 실무 맥락 공유용 설명 로우(Row) 생성
    desc_rows = ""
    for c in palette:
        desc_rows += f"""
    <tr>
      <td style="width: 25%; font-weight: 700; font-size: 12px;">
        <span style="display:inline-block; width:10px; height:10px; border-radius:50%; background:{e(c.get('hex_code',''))}; margin-right:6px; border:1px solid rgba(0,0,0,0.1);"></span>
        {e(c.get('color_name',''))} ({e(c.get('hex_code',''))})
      </td>
      <td style="width: 18%; font-size: 10px; font-weight: 700; color: var(--sd); text-transform: uppercase;">{e(c.get('role',''))}</td>
      <td style="color: #444; font-size: 10px; line-height: 1.3; text-align: justify;">{e(c.get('reason',''))}</td>
    </tr>"""

    return f"""
<div class="section">
  <div class="sec-hdr" style="margin-bottom: 24px;">
    <span class="sec-num">Section C-1 · Color Guideline</span>
    <span class="sec-title">브랜드 컬러 팔레트 시스템</span>
    <span class="sec-sub">브랜드의 시각적 일관성과 고유한 정서적 온도를 전개하기 위한 고유 색상 자산 명세서입니다.</span>
  </div>

  <div class="c-lbl" style="margin-bottom: 10px; color: var(--text-main); font-weight: 700;">Core Colors · 핵심 브랜드 컬러</div>
  <div style="display: flex; justify-content: space-between; margin-bottom: 24px;">
    {top_chips_html}
  </div>

  <div class="c-lbl" style="margin-bottom: 10px; color: var(--text-main); font-weight: 700;">Functional & Functional Colors · 보조 및 기능성 컬러</div>
  <div class="grid-3" style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 14px; margin-bottom: 28px;">
    {bottom_chips_html}
  </div>

  <div class="c-lbl" style="margin-bottom: 10px; color: var(--text-main); font-weight: 700;">Color Application Principles · 색상별 정의 및 수립 근거</div>
  <table class="data-table color-table" style="width: 100%;">
    <thead>
      <tr>
        <th>색상명 / HEX</th>
        <th>시스템 역할</th>
        <th>디자인 수립 근거 및 실무 가이드라인</th>
      </tr>
    </thead>
    <tbody>
      {desc_rows if desc_rows else "<tr><td colspan='3' style='text-align:center;'>지정된 컬러 명세 자산이 없습니다.</td></tr>"}
    </tbody>
  </table>
</div>
"""

# [Page 13] Section C-2. 타이포그래피 규칙 (Typography Rules)
def build_c2_typography(C_data):
    if isinstance(C_data, (tuple, list)):
        merged_data = {}
        for part in C_data:
            if isinstance(part, dict):
                merged_data.update(part)
        C_data = merged_data

    typo = C_data.get('typography', {})
    primary = typo.get('primary_font', {})
    secondary = typo.get('secondary_font', {})

    # 서체별 데이터 추출 및 이스케이프
    p_name = e(primary.get('font_name_kr', '고딕 A1'))
    p_google = e(primary.get('google_fonts_family', 'Gothic A1'))
    p_weight = primary.get('weight_recommendation', 800)
    p_usage = e(primary.get('usage_and_reason', ''))

    s_name = e(secondary.get('font_name_kr', '본고딕'))
    s_google = e(secondary.get('google_fonts_family', 'Noto Sans KR'))
    s_weight = secondary.get('weight_recommendation', 400)
    s_usage = e(secondary.get('usage_and_reason', ''))

    return f"""
<div class="section">
  <div class="sec-hdr" style="margin-bottom: 32px;">
    <span class="sec-num">Section C-2 · Typography System</span>
    <span class="sec-title">타이포그래피 규칙</span>
    <span class="sec-sub">브랜드의 신뢰도와 가독성을 결정짓는 공식 서체 규격 및 디지털 환경 배포 가이드라인입니다.</span>
  </div>

  <div class="card" style="margin-bottom: 28px; padding: 28px 32px; border-left: 4px solid var(--sd);">
    <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 20px;">
      <div>
        <div class="c-lbl" style="color: var(--sd); font-weight: 700; margin-bottom: 4px;">Primary Font · 헤드라인 서체</div>
        <div style="font-size: 20px; font-weight: 700; color: var(--text-main);">{p_name} ({p_google})</div>
      </div>
      <div style="text-align: right;">
        <div style="font-size: 10px; color: var(--text-muted); margin-bottom: 4px; font-weight: 700;">GOOGLE FONTS API</div>
        <code style="background: var(--surface); padding: 4px 10px; border-radius: 4px; font-family: monospace; font-size: 11.5px; border: 1px solid var(--border-light); color: #D53F8C;">
          family={p_google.replace(' ', '+')}:wght@{p_weight}
        </code>
      </div>
    </div>

    <div style="padding: 20px 0; border-top: 1px dashed var(--border-light); border-bottom: 1px dashed var(--border-light); margin-bottom: 16px;">
      <div style="font-family: '{p_google}', sans-serif; font-weight: {p_weight}; font-size: 36px; line-height: 1.2; color: var(--text-main); margin-bottom: 8px;">
        가나다라마바사아자차카타파하
      </div>
      <div style="font-family: '{p_google}', sans-serif; font-weight: {p_weight}; font-size: 18px; color: var(--text-muted); letter-spacing: 2px;">
        ABCDEFGHIJKLMNOPQRSTUVWXYZ 0123456789
      </div>
    </div>

    <div style="font-size: 12.5px; color: #555; line-height: 1.6; text-align: justify;">
      <strong>Usage & Rationale:</strong> {p_usage}
    </div>
  </div>

  <div class="card" style="padding: 28px 32px; border-left: 4px solid var(--text-muted);">
    <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 20px;">
      <div>
        <div class="c-lbl" style="color: var(--text-muted); font-weight: 700; margin-bottom: 4px;">Secondary Font · 본문 서체</div>
        <div style="font-size: 18px; font-weight: 700; color: var(--text-main);">{s_name} ({s_google})</div>
      </div>
      <div style="text-align: right;">
        <div style="font-size: 10px; color: var(--text-muted); margin-bottom: 4px; font-weight: 700;">GOOGLE FONTS API</div>
        <code style="background: var(--surface); padding: 4px 10px; border-radius: 4px; font-family: monospace; font-size: 11.5px; border: 1px solid var(--border-light); color: #D53F8C;">
          family={s_google.replace(' ', '+')}:wght@{s_weight}
        </code>
      </div>
    </div>

    <div style="padding: 20px 0; border-top: 1px dashed var(--border-light); border-bottom: 1px dashed var(--border-light); margin-bottom: 16px;">
      <div style="font-family: '{s_google}', sans-serif; font-weight: {s_weight}; font-size: 14.5px; line-height: 1.8; color: var(--text-main); text-align: justify;">
        이 샘플 문장은 본문용 서체의 가독성과 정보 위계를 확인하기 위한 예시입니다. 브랜드의 실제 메시지는 위 사용 기준과 확정된 언어 자산을 따릅니다.
      </div>
    </div>

    <div style="font-size: 12.5px; color: #555; line-height: 1.6; text-align: justify;">
      <strong>Usage & Rationale:</strong> {s_usage}
    </div>
  </div>
</div>
"""

# [Page 14] Section C-3. 비주얼 무드 & 그래픽 에셋 지시서
def build_c3_visual_mood(C_data):
    if isinstance(C_data, (tuple, list)):
        merged_data = {}
        for part in C_data:
            if isinstance(part, dict):
                merged_data.update(part)
        C_data = merged_data

    mood = C_data.get('visual_mood_guide', {})
    prin = C_data.get('design_principles', {})

    # 데이터 추출 및 백업 키 지원 (photography_do 가 없을 경우 visual_do 등으로 확장성 확보)
    dos = mood.get('photography_do', []) if 'photography_do' in mood else mood.get('visual_do', [])
    donts = mood.get('photography_dont', []) if 'photography_dont' in mood else mood.get('visual_dont', [])
    keywords = mood.get('mood_keywords', [])
    
    layout_dir = e(prin.get('layout_direction', ''))
    img_proc = e(prin.get('image_processing', ''))

    # 1. 무드 키워드 태그 칩 생성 (최상단 배치용)
    kw_tags = "".join(f'<span class="tag" style="background: var(--surface); border-color: var(--border-strong); margin-right: 8px; margin-bottom: 8px; font-size: 13px; font-weight: 700; color: var(--text-main); padding: 6px 14px;">{e(k)}</span>' for k in keywords)

    # 2. Do / Don't 리스트 HTML 생성
    do_html = "".join(f'<li style="margin-bottom: 12px; color: #1F472D; line-height: 1.6; text-align: justify;"><span style="color: #276749; font-weight: bold; margin-right: 6px;">✔</span>{e(d)}</li>' for d in dos)
    dont_html = "".join(f'<li style="margin-bottom: 12px; color: #742A2A; line-height: 1.6; text-align: justify;"><span style="color: #9B2C2C; font-weight: bold; margin-right: 6px;">✘</span>{e(d)}</li>' for d in donts)

    return f"""
<div class="section">
  <div class="sec-hdr" style="margin-bottom: 28px;">
    <span class="sec-num">Section C-3 · Visual Mood & Assets</span>
    <span class="sec-title">비주얼 무드 & 그래픽 에셋 지시서</span>
    <span class="sec-sub">사진 촬영, 3D 렌더링, 일러스트, UI 그래픽 등 모든 시각 결과물을 통제하는 아트 디렉팅 기준입니다.</span>
  </div>

  <div class="c-lbl" style="margin-bottom: 12px; color: var(--text-main); font-weight: 700;">Core Mood Keywords · 분위기 정의</div>
  <div class="tags mood-tags" style="margin-top: 0; margin-bottom: 24px;">
    {kw_tags if kw_tags else "<span style='color:var(--text-muted);'>도출된 무드 키워드가 없습니다.</span>"}
  </div>

  <div class="do-dont-grid" style="margin-bottom: 22px;">
    <div style="background: #F0FFF4; border: 1px solid #9AE6B4; border-radius: 10px; padding: 16px;">
      <div style="font-size: 16px; font-weight: 800; color: #22543D; margin-bottom: 12px;">
        DO <span style="font-size: 11px; font-weight: 600; color: #276749; margin-left: 6px;">권장 표현</span>
      </div>
      <ul style="list-style: none; padding: 0; margin: 0; font-size: 12.5px;">
        {do_html if do_html else "<li style='color: #276749;'>등록된 권장 수칙이 없습니다.</li>"}
      </ul>
    </div>
    
    <div style="background: #FFF5F5; border: 1px solid #FEB2B2; border-radius: 10px; padding: 16px;">
      <div style="font-size: 16px; font-weight: 800; color: #C53030; margin-bottom: 12px;">
        DON'T <span style="font-size: 11px; font-weight: 600; color: #9B2C2C; margin-left: 6px;">피해야 할 표현</span>
      </div>
      <ul style="list-style: none; padding: 0; margin: 0; font-size: 12.5px;">
        {dont_html if dont_html else "<li style='color: #9B2C2C;'>등록된 금지 수칙이 없습니다.</li>"}
      </ul>
    </div>
  </div>

  <div class="c-lbl" style="margin-bottom: 12px; color: var(--text-main); font-weight: 700;">Design Principles · 디자인 원칙 및 에셋 가공 규격</div>
  
  <div class="card" style="padding: 24px 28px; margin-bottom: 16px; border-left: 4px solid var(--sd);">
    <div style="font-size: 11px; color: var(--sd); font-weight: 700; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 6px;">Layout & UI Direction · 레이아웃 방향성</div>
    <div style="font-size: 13px; color: var(--text-main); line-height: 1.7; text-align: justify; font-weight: 500;">
      {layout_dir if layout_dir else "정의된 레이아웃 방향성이 없습니다."}
    </div>
  </div>

  <div class="card" style="padding: 24px 28px; border-left: 4px solid var(--text-muted);">
    <div style="font-size: 11px; color: var(--text-muted); font-weight: 700; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 6px;">Image & Asset Processing · 이미지 및 에셋 보정 규칙</div>
    <div style="font-size: 13px; color: var(--text-main); line-height: 1.7; text-align: justify; font-weight: 500;">
      {img_proc if img_proc else "정의된 이미지 보정 규칙이 없습니다."}
    </div>
  </div>

</div>
"""

# [Page 15] Section D-1. 로고 아이덴티티 & 컨셉 + Section D-2. 로고 사용 가이드
def build_d_logo_identity(data_D, logo_image_path=None):
    # Section E와 동일하게 candidates 껍질이 있다면 안전하게 벗겨냅니다.
    if data_D and 'candidates' in data_D and len(data_D['candidates']) > 0:
        data_D = data_D['candidates'][0]

    # 1. Root 레벨에서 데이터를 먼저 찾음
    logo_data = data_D.get('logo_identity', data_D)

    # 2. 만약 logo_identity가 없더라도 concept/guide가 바로 Root에 있다면 거기서 가져옴
    concept = logo_data.get('concept', data_D.get('concept', {}))
    guide = logo_data.get('guide', data_D.get('guide', {}))

    # 3. 데이터 추출 (방어적)
    symbol_reason = e(concept.get('symbol_reason', ''))
    color_reason = e(concept.get('color_reason', ''))
    overall_message = e(concept.get('overall_message', '')).replace('\n', '<br>')
    direction_text = e(concept.get('direction_text', ''))

    min_size = e(guide.get('minimum_size', ''))
    clear_space = e(guide.get('clear_space', ''))

    # 이미지 경로 처리 (WeasyPrint 로컬 렌더링용 절대경로)
    img_tag = ""
    if logo_image_path and os.path.exists(logo_image_path):
        safe_path = logo_image_path.replace('\\', '/')
        img_tag = f'<img src="file:///{safe_path}" style="max-width: 100%; max-height: 280px; object-fit: contain; margin: 0 auto; display: block;">'
    else:
        img_tag = f"""
        <div style="width: 100%; height: 250px; background: rgba(0,0,0,0.02); border: 1px dashed var(--border-strong); border-radius: 8px; display: flex; align-items: center; justify-content: center; color: var(--text-muted); font-size: 13px;">
            [로고 이미지 렌더링 대기 중]
        </div>"""

    return f"""
    <div class="section" style="page-break-inside: avoid; break-inside: avoid-page;">
        <div class="sec-hdr">
            <span class="sec-num">Section D-1</span>
            <span class="sec-title">Logo Identity & Concept</span>
            <span class="sec-sub">브랜드의 철학과 핵심 가치를 시각적으로 압축한 마스터 로고입니다.</span>
        </div>

        <div class="card" style="text-align: center; margin-bottom: 16px; padding: 28px 20px; box-shadow: 0 4px 20px rgba(0,0,0,0.02);">
            {img_tag}
        </div>

        <div class="hl-box">
            <div class="c-lbl">Design Direction · 시각적 방향성</div>
            <p style="font-weight: 500; font-style: italic;">"{direction_text}"</p>
        </div>

        <div class="grid-2" style="margin-bottom: 12px; gap: 10px;">
            <div class="card" style="border-top: 3px solid var(--sd); padding: 10px 11px;">
                <div class="c-lbl" style="font-size: 9.5px; margin-bottom: 6px;">Symbol Motif</div>
                <div class="c-body" style="text-align: justify; font-size: 11.5px; line-height: 1.55;">{symbol_reason}</div>
            </div>
            <div class="card" style="border-top: 3px solid var(--sd); padding: 10px 11px;">
                <div class="c-lbl" style="font-size: 9.5px; margin-bottom: 6px;">Color Identity</div>
                <div class="c-body" style="text-align: justify; font-size: 11.5px; line-height: 1.55;">{color_reason}</div>
            </div>
        </div>

        <div class="promise-block" style="margin-top: 6px;">
            <div class="ch">Brand Message · 로고가 전달하는 철학</div>
            <div class="ct" style="text-align: justify; font-size: 13.5px;">{overall_message}</div>
        </div>

        <div class="sec-hdr" style="margin-top: 32px;">
            <span class="sec-num">Section D-2</span>
            <span class="sec-title">Logo Usage Guide</span>
            <span class="sec-sub">브랜드의 시각적 일관성을 유지하기 위한 최소 규정입니다.</span>
        </div>

        <div class="grid-2" style="margin-bottom: 12px; gap: 10px;">
            <div class="card">
                <div class="c-lbl" style="font-size: 9.5px; margin-bottom: 6px;">Minimum Size · 최소 사용 크기</div>
                <div class="c-body" style="font-size: 11.5px; line-height: 1.55;">{min_size}</div>
            </div>
            <div class="card">
                <div class="c-lbl" style="font-size: 9.5px; margin-bottom: 6px;">Clear Space · 안전 여백</div>
                <div class="c-body" style="font-size: 11.5px; line-height: 1.55;">{clear_space}</div>
            </div>
        </div>
    </div>
    """


# [Page 16] Section E-1. 브랜드 페르소나 & 캐릭터 가이드 (Brand Persona & Character Guide)
def build_e_character_guide(data_E, char_image_path=None):
    # candidates 껍질이 있는지 확인하고 안전하게 벗겨냄
    if data_E and 'candidates' in data_E and len(data_E['candidates']) > 0:
        data_E = data_E['candidates'][0]
        
    guide = data_E.get('character_guide', {})
    intro = guide.get('intro', {})
    reasoning = guide.get('reasoning', {})
    story = guide.get('story', {})

    char_name = e(intro.get('name', ''))
    appearance = e(intro.get('appearance', '')).replace('\n', '<br>')
    symbolic_value = e(intro.get('symbolic_value', ''))

    selection_reason = e(reasoning.get('selection_reason', ''))
    emotional_connection = e(reasoning.get('emotional_connection', ''))

    background_story = e(story.get('background', '')).replace('\n', '<br>')
    brand_role = e(story.get('brand_role', ''))

    # 2. 이미지 경로 처리 (WeasyPrint 로컬 렌더링용 절대경로)
    img_tag = ""
    if char_image_path and os.path.exists(char_image_path):
        safe_path = char_image_path.replace('\\', '/')
        img_tag = f'<img src="file:///{safe_path}" style="max-width: 100%; max-height: 320px; object-fit: contain; margin: 0 auto; display: block; border-radius: 8px;">'
    else:
        img_tag = f"""
        <div style="width: 100%; height: 320px; background: rgba(0,0,0,0.02); border: 1px dashed var(--border-strong); border-radius: 8px; display: flex; align-items: center; justify-content: center; color: var(--text-muted); font-size: 13px;">
            [캐릭터 이미지 렌더링 대기 중]
        </div>"""

    return f"""
    <div class="section">
        <div class="sec-hdr">
            <span class="sec-num">Section E-1</span>
            <span class="sec-title">Brand Persona & Character</span>
            <span class="sec-sub">고객과 브랜드 사이의 정서적 유대감을 형성하는 핵심 페르소나입니다.</span>
        </div>

        <div style="display: grid; grid-template-columns: 4fr 6fr; gap: 16px; margin-bottom: 24px; page-break-inside: avoid;">
            
            <div class="card" style="display: flex; align-items: center; justify-content: center; padding: 20px; background: var(--bg);">
                {img_tag}
            </div>

            <div style="display: flex; flex-direction: column; gap: 12px;">
                <div class="slogan-box" style="margin: 0; padding: 16px; border-width: 1px; background: var(--surface);">
                    <div style="font-size: 11px; font-weight: 700; color: var(--text-muted); letter-spacing: 0.15em; text-transform: uppercase; margin-bottom: 4px;">Persona Name</div>
                    <div style="font-family: 'Noto Serif KR', serif; font-size: 24px; font-weight: 700; color: var(--sd); line-height: 1.3;">
                        {char_name}
                    </div>
                </div>

                <div class="card" style="flex-grow: 1;">
                    <div class="c-lbl">Appearance · 외형 및 디자인 특징</div>
                    <div class="c-body" style="text-align: justify;">{appearance}</div>
                </div>
            </div>
        </div>

    <div class="hl-box" style="margin-bottom: 16px;">
            <div class="c-lbl" style="color: rgba(0,0,0,0.5);">Worldview & Role · 세계관 및 브랜드 내 역할</div>
            <p style="font-size: 14px; font-weight: 600; line-height: 1.6; margin-bottom: 8px;">
                "{brand_role}"
            </p>
            <p style="font-size: 13px; font-weight: 400; opacity: 0.9;">
                {background_story}
            </p>
        </div>

        <div class="grid-2">
            <div class="card">
                <div class="c-lbl">Core Value · 상징 가치 및 선택 이유</div>
                <div class="c-body" style="text-align: justify; margin-bottom: 12px; padding-bottom: 12px; border-bottom: 1px dashed var(--border-light);">
                    <strong style="color: var(--text-main); font-weight: 600;">상징 가치:</strong> {symbolic_value}
                </div>
                <div class="c-body" style="text-align: justify;">
                    {selection_reason}
                </div>
            </div>
            
            <div class="card">
                <div class="c-lbl">Emotional Connection · 감성적 연결 포인트</div>
                <div class="c-body" style="text-align: justify;">
                    {emotional_connection}
                </div>
            </div>
        </div>
    </div>
    """