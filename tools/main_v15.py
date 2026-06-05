#!/usr/bin/env python3
"""东台方言翻译核心 v15 - 短语级翻译+上下文感知+TTS+双模型ASR"""
import json, re, os, asyncio, hashlib, bisect
from collections import defaultdict

# ============ 语音识别纠错层 ============
ASR_CORRECTION = [
    # 代词
    ['我拉', '我俫'], ['我啦', '我俫'], ['我俩', '我俫'], ['我勒', '我俫'], ['我来', '我俫'],
    ['你拉', '你俫'], ['你啦', '你俫'], ['你俩', '你俫'], ['你勒', '你俫'], ['你来', '你俫'],
    ['他拉', '他俫'], ['他啦', '他俫'], ['他俩', '他俫'], ['他勒', '他俫'], ['他来', '他俫'],
    # 疑问词
    ['十的', '什的'], ['什地', '什的'], ['什尼', '什的'], ['什呢', '什的'],
    ['怎样', '怎呃'], ['怎的', '怎呃'], ['怎呢', '怎呃'], ['真呢', '怎呃'], ['争呢', '怎呃'],
    ['几点', '几钿'], ['几钱', '几钿'], ['几店', '几钿'],
    ['做什地', '做什的'],
    # 时间词
    ['今早', '今朝'], ['金朝', '今朝'], ['今招', '今朝'],
    ['明早', '明朝'], ['名招', '明朝'],
    ['后高', '侯告'], ['厚稿', '侯告'], ['候告', '侯告'], ['猴搞', '侯告'], ['后搞', '侯告'], ['号搞', '侯告'],
    ['中周', '中昼'], ['种周', '中昼'], ['上周', '上昼'], ['商周', '上昼'], ['下周', '下昼'],
    ['个歇', '搿歇'], ['格歇', '搿歇'], ['各歇', '搿歇'],
    # 否定词
    ['没的', '没得'], ['美的', '没得'], ['梅的', '没得'],
    ['不来事', '勿来事'], ['不来是', '勿来事'], ['弗来是', '勿来事'],
    ['不晓得', '勿晓得'], ['不晓的', '勿晓得'],
    # 称谓
    ['跌跌', '嗲嗲'], ['玛玛', '嫲嫲'], ['嬷嬷', '嫲嫲'],
    ['男酱', '男将'], ['南将', '男将'], ['女酱', '女将'], ['吕将', '女将'],
    ['歌歌', '锅锅'], ['佳佳', '假假'], ['小南', '小囡'],
    # 形容词/动词
    ['结滚', '结棍'], ['解棍', '结棍'], ['杰棍', '结棍'],
    ['饭嫌', '犯嫌'], ['凡嫌', '犯嫌'],
    ['零光', '灵光'], ['林光', '灵光'], ['表致', '标致'],
    ['小的', '晓得'], ['晓的', '晓得'], ['效得', '晓得'],
    ['惯了', '掼咧'], ['关了', '掼咧'], ['抗了', '囥咧'], ['炕了', '囥咧'],
    ['挖了', '搲咧'], ['瓦了', '搲咧'], ['大好', '汏好'],
    ['邦衬', '帮衬'], ['号稍', '豪稍'], ['好稍', '豪稍'], ['毫稍', '豪稍'],
    ['白想', '白相'], ['百相', '白相'], ['大寡', '搭寡'], ['搭瓜', '搭寡'],
    ['搞子', '杲昃'], ['高子', '杲昃'], ['事替', '事体'], ['是体', '事体'],
    ['老为', '劳为'], ['捞为', '劳为'], ['把哉', '罢哉'], ['八哉', '罢哉'],
    ['一他刮子', '一塌刮子'], ['胖海', '旁海'],
    # 常见误识别
    ['格格', '搿个'], ['隔的', '搿个'], ['格个', '搿个'], ['隔个', '搿个'],
    ['刷瓜', '刷刮'], ['刷瓜葛', '刷刮'],
    ['神呢', '什呢'], ['尸体', '事体'],
    ['物药紧', '勿要紧'], ['药紧', '要紧'],
    ['扎十', '扎实'], ['吓他', '下子'], ['瞎子', '下子'],
    ['克克', '刻刻'], ['可克', '刻刻'],
    ['吃力', '吃力'], ['气力', '吃力'],
    ['还有', '还有'],  # no-op filler to maintain sort
]
ASR_CORRECTION.sort(key=lambda x: -len(x[0]))
# Remove no-ops
ASR_CORRECTION = [[w, r] for w, r in ASR_CORRECTION if w != r]

def correct_asr(text):
    result = text
    for wrong, right in ASR_CORRECTION:
        if wrong in result:
            result = result.replace(wrong, right)
    # Context-aware: 不 before action verbs → 勿
    result = re.sub(r'不(?=[走做说吃看想会用能好去来要肯给买学写找打听])', '勿', result)
    return result

# ============ 翻译规则 V2 ============
# Priority-ordered: longer phrases first, then shorter
M2D_PHRASES = [
    # Multi-character phrases (highest priority)
    ['一塌刮子', '一塌刮子'],  # same in both
    ['老鼠钻风箱', '老鼠钻风箱'],
    # Common sentences/phrases
    ['不知道', '勿晓得'], ['不可能', '勿可能'], ['不要紧', '勿要紧'], ['没关系', '勿要紧'],
    ['不行了', '勿来事'], ['不得了', '了不得'], ['怎么办', '怎呃办'],
    ['是不是', '阿是'], ['要不要', '阿要'], ['能不能', '阿能'], ['会不会', '阿会'], ['好不好', '阿好'],
    ['干什么', '做什的'], ['怎么样', '怎呃样'], ['多少钱', '几钿'],
    ['这么多', '搿呃多'], ['那么远', '嗨呃远'], ['这么好', '搿呃好'], ['那么大', '嗨呃大'],
    ['这个', '搿个'], ['那个', '嗨个'], ['这里', '搿搭'], ['那里', '嗨搭'],
    ['这个地方', '搿搭'], ['那个地方', '嗨搭'],
    ['在这里', '在搿搭'], ['在哪里', '在哪块'], ['什么时间', '几点钟'],
    ['不得了', '蛮结棍'],
    # Time expressions
    ['今天', '今朝'], ['明天', '明朝'], ['昨天', '昨日子'], ['后天', '后朝'],
    ['去年', '旧年'], ['今年', '今年子'], ['前天', '前朝'],
    ['晚上', '侯告'], ['夜里', '夜头'], ['上午', '上昼'], ['下午', '下半天'], ['中午', '中昼'],
    ['早上', '早起'], ['现在', '搿歇'], ['以前', '老早'], ['以后', '后头'], ['刚才', '才将'],
    ['一会儿', '歇歇'], ['马上', '豪稍'], ['算了', '罢哉'], ['赶紧', '豪稍'],
    # Kinship
    ['爷爷', '嗲嗲'], ['奶奶', '阿婆'], ['姐姐', '假假'], ['哥哥', '锅锅'],
    ['丈夫', '男将'], ['妻子', '女将'], ['小孩', '小囡'], ['邻居', '邻舍'],
    ['叔叔', '爷叔'], ['婶婶', '婶婶'], ['阿姨', '阿姨'],
    # Body parts
    ['肚子', '肚皮'], ['脖子', '头颈'], ['脸', '面孔'], ['头', '头脑子'],
    ['腰', '腰杆子'], ['手指', '指末头'],
    # Food & objects
    ['东西', '杲昃'], ['事情', '事体'], ['衣服', '衣裳'], ['厨房', '灶间'],
    ['早饭', '朝饭'], ['午饭', '中饭'], ['晚饭', '夜饭'],
    ['黄鳝', '长鱼'], ['螃蟹', '旁海'], ['南瓜', '番瓜'], ['萝卜干', '罗服锅儿'],
    # Places
    ['学校', '学堂'], ['医院', '医院'], ['医生', '郎中'],
    # Pronouns
    ['我们', '我俫'], ['你们', '你俫'], ['他们', '他俫'], ['咱们', '我俫'],
    ['自己', '自家'], ['人家', '别家'],
    # Question words
    ['什么', '什的'], ['怎么', '怎呃'], ['哪里', '哪块'], ['多少', '好多'],
    # Adverbs
    ['非常', '蛮蛮'], ['特别', '蛮蛮'], ['一定', '安安'], ['全部', '一塌刮子'],
    ['很', '蛮'], ['太', '忒'], ['最', '顶'],
    # Negation
    ['没有什么', '没得什的'], ['没什么', '没得什的'], ['没有什么事', '没得什的事体'], ['没事', '没得事体'], ['没有', '没得'], ['不要', '嫑'], ['不行', '弗来事'], ['不了', '勿咧'],
    # Common adjectives
    ['厉害', '结棍'], ['漂亮', '标致'], ['聪明', '灵光'], ['笨', '戆'], ['傻', '戆'],
    ['累', '吃力'], ['舒服', '忺'], ['冷', '瀴'], ['脏', '龌龊'], ['小气', '抠'],
    ['讨厌', '犯嫌'], ['喜欢', '欢喜'], ['高兴', '快活'], ['生气', '气不过'],
    ['烦恼', '懊糟'], ['麻烦', '劳为'], ['了不起', '结棍'],
    # Common verbs
    ['知道', '晓得'],  ['找', '寻'], ['洗', '汏'], ['玩', '白相'],
    ['说', '讲'], ['睡觉', '困觉'], ['聊天', '搭寡'], ['回家', '家去'], ['回来', '转来'],
    ['帮忙', '帮衬'], ['帮我', '帮衬我'], ['帮他', '帮衬他'], ['帮她', '帮衬她'], ['谢谢', '难为'], ['扔', '掼'], ['丢', '厾'], ['放', '囥'],
    ['睡', '困'], ['想', '忖'],  ['吃', '噇'], ['走', '踅'],
     ['打', '夯'],  ['擦', '揩'],
    ['下了雨', '落咧雨'], ['下了雪', '落咧雪'], ['下雨了', '落雨咧'], ['下雪了', '落雪咧'], ['下雨', '落雨'], ['下雪', '落雪'], ['刮风', '起风'],
    # Greetings
    ['你好', '蛮好呃'], ['再见', '再会'], ['对不起', '勿好意思'],
    # Degree
    ['很冷', '蛮蛮瀴'], ['很热', '蛮蛮热'], ['很累', '蛮蛮吃力'], ['很快', '蛮蛮快'],
    ['很贵', '蛮蛮贵'], ['很便宜', '蛮蛮便宜'],
    # Weather
    ['便宜', '便宜'], 
]

# Build sorted by length desc for greedy matching
M2D_PHRASES.sort(key=lambda x: -len(x[0]))

# Reverse rules for D2M
D2M_PHRASES = []
for src, dst in M2D_PHRASES:
    if len(dst) >= 2 and src != dst:  # skip same-in-both
        D2M_PHRASES.append([dst, src])
# Add single-char dialect words
D2M_PHRASES.extend([
    ['勿', '不'], ['呒', '没'], ['蛮蛮', '非常'], ['寻', '找'], ['掼', '扔'],
    ['囥', '放'], ['困', '睡'], ['汏', '洗'], ['拨', '给'], ['搲', '拿'],
    ['揩', '擦'], ['噇', '吃'], ['夯', '打'], ['踅', '走'], ['忖', '想'],
    ['瀴', '冷'], ['忺', '舒服'], ['戆', '笨'], ['蛮', '很'], ['搿', '这'], ['嗨', '那'],
])
D2M_PHRASES.sort(key=lambda x: -len(x[0]))

# Suffix transformations
SUFFIX_M2D = {'了': '咧', '吧': '啘', '吗': '呃', '呢': '哩', '啊': '噶'}
SUFFIX_D2M = {'呃': '的', '咧': '了', '啘': '吧', '哉': '了', '噶': '啊', '伐': '吗', '哩': '呢'}

# ============ 语料库 V2 ============
_corpus_cache = None
_corpus_index = None  # for fast lookup

def load_corpus():
    global _corpus_cache, _corpus_index
    if _corpus_cache is not None:
        return _corpus_cache
    
    # Try compact corpus first, then full, then original
    paths = [
        os.path.join(os.path.dirname(__file__), 'corpus_compact.json'),
        os.path.join(os.path.dirname(__file__), 'corpus_55k_quality.json'),
        os.path.join(os.path.dirname(__file__), 'corpus.json'),
    ]
    for path in paths:
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    raw = json.load(f)
                # Handle compact format {m, d} or full format {mandarin, dongtai, ...}
                if raw and 'm' in raw[0]:
                    _corpus_cache = [{'mandarin': e['m'], 'dongtai': e['d']} for e in raw]
                else:
                    _corpus_cache = raw
                break
            except:
                continue
    
    if _corpus_cache is None:
        _corpus_cache = []
    
    # Build lookup indices
    _corpus_index = {
        'm2d': {},  # mandarin -> dongtai (exact)
        'd2m': {},  # dongtai -> mandarin (exact)
        'm_words': defaultdict(list),  # word -> entries containing it
        'd_words': defaultdict(list),
    }
    
    for entry in _corpus_cache:
        m = entry.get('mandarin', '').strip()
        d = entry.get('dongtai', '').strip()
        if m:
            _corpus_index['m2d'][m] = d
        if d:
            _corpus_index['d2m'][d] = m
        # Index by key words for fuzzy matching
        if m:
            for w in _extract_content_words(m):
                _corpus_index['m_words'][w].append(entry)
        if d:
            for w in _extract_content_words(d):
                _corpus_index['d_words'][w].append(entry)
    
    return _corpus_cache

def _extract_content_words(text):
    """Extract meaningful words (2+ chars) from text"""
    # Remove punctuation and common particles
    cleaned = re.sub(r'[，。！？、；：""''（）\s的了在是都也很到被把让给又]', '', text)
    words = []
    # Extract 2-4 char segments
    for i in range(len(cleaned)):
        for l in [4, 3, 2]:
            if i + l <= len(cleaned):
                w = cleaned[i:i+l]
                if len(w) >= 2:
                    words.append(w)
    return words

# ============ 方向检测 V2 ============
DIALECT_DETECT_MARKERS = [
    '我俫', '你俫', '他俫', '晓得', '什的', '怎呃',
    '没得', '犯嫌', '帮衬', '嗲嗲', '男将', '女将', '锅锅', '假假',
    '搿歇', '搿样', '嗨样', '搿搭', '嗨搭', '豪稍', '罢哉', '侯告',
    '今朝', '明朝', '蛮蛮', '阿是', '阿要', '弗要', '嫑', '结棍',
    '一塌刮子', '杲昃', '事体', '衣裳', '白相', '家去', '转来',
    '朝饭', '夜饭', '长鱼', '旁海', '罗服锅儿', '困觉', '搭寡',
    '懊糟', '灵光', '标致', '戆', '吃力', '瀴', '忺',
    '寻', '掼', '囥', '汏', '拨', '搲', '揩', '噇', '夯', '踅', '忖',
    '勿来事', '勿晓得', '做什的', '几钿', '蛮蛮', '呒没', '推板',
    '搿个', '嗨个', '搿呃', '嗨呃',
    '安安', '刻刻', '歇歇', '才将', '老早',
    '头脑子', '肚皮', '头颈', '面孔', '腰杆子',
    '小囡', '邻舍', '灶间', '学堂', '郎中',
    '落雨', '落雪', '起风',
]

def detect_direction(text):
    """Detect if text is dialect or mandarin"""
    count = sum(1 for m in DIALECT_DETECT_MARKERS if m in text)
    # Also check single-char strong markers
    single_markers = ['勿', '呒', '搿', '瀴', '忺', '囥', '汏', '噇']
    single_count = sum(1 for m in single_markers if m in text)
    total = count + single_count * 0.5
    return 'd2m' if total >= 1 else 'm2d'

# ============ 翻译引擎 V2 ============
def apply_m2d(text):
    """Apply M2D rules with greedy longest-match"""
    result = text
    # Pre-processing: context-aware weather pattern (下了X雨 → 落咧X雨)
    result = re.sub(r'下了(.{0,4})雨', r'落咧\1雨', result)
    result = re.sub(r'下了(.{0,4})雪', r'落咧\1雪', result)
    result = re.sub(r'下(.{0,4})雨了', r'落\1雨咧', result)
    result = re.sub(r'下(.{0,4})雪了', r'落\1雪咧', result)
    for src, dst in M2D_PHRASES:
        if src in result and src != dst:
            result = result.replace(src, dst)
    # Suffix transformation
    for suffix, dialect_suffix in SUFFIX_M2D.items():
        if result.endswith(suffix) and len(result) > len(suffix):
            result = result[:-len(suffix)] + dialect_suffix
            break
    return result

def apply_d2m(text):
    """Apply D2M rules with greedy longest-match"""
    result = text
    for src, dst in D2M_PHRASES:
        if src in result and src != dst:
            result = result.replace(src, dst)
    # Suffix transformation
    for dialect_suffix, suffix in SUFFIX_D2M.items():
        if result.endswith(dialect_suffix) and len(result) > len(dialect_suffix):
            result = result[:-len(dialect_suffix)] + suffix
            break
    return result

def _ngram_sim(s1, s2, n=2):
    """Character n-gram similarity"""
    if not s1 or not s2:
        return 0.0
    n1 = set(s1[i:i+n] for i in range(len(s1)-n+1))
    n2 = set(s2[i:i+n] for i in range(len(s2)-n+1))
    if not n1 or not n2:
        return 0.0
    return len(n1 & n2) / max(len(n1 | n2), 1)

def fuzzy_match(text, corpus, direction='m2d', limit=50):
    """V2 fuzzy matching using inverted index + n-gram"""
    load_corpus()  # ensure index built
    
    key = 'mandarin' if direction == 'm2d' else 'dongtai'
    target_key = 'dongtai' if direction == 'm2d' else 'mandarin'
    word_index = _corpus_index['m_words'] if direction == 'm2d' else _corpus_index['d_words']
    
    # Step 1: Use inverted index to find candidate entries
    candidates = defaultdict(int)
    words = _extract_content_words(text)
    for w in words:
        if w in word_index:
            for entry in word_index[w]:
                candidates[id(entry)] += 1
    
    # Step 2: Score candidates
    scored = []
    seen_entries = {}
    for entry_id, hit_count in candidates.items():
        # Find the entry
        for entry in corpus:
            if id(entry) == entry_id:
                corpus_text = entry.get(key, '')
                if not corpus_text:
                    break
                # Combine word overlap + n-gram similarity
                word_score = hit_count / max(len(words), 1)
                ngram_score = _ngram_sim(text, corpus_text)
                combined = 0.4 * word_score + 0.6 * ngram_score
                if combined > 0.5:
                    scored.append((combined, entry))
                break
    
    if not scored:
        return None
    
    # Step 3: Return best match
    scored.sort(key=lambda x: -x[0])
    best_score, best_entry = scored[0]
    return best_entry.get(target_key, '')

def phrase_chunk_translate(text, direction='m2d'):
    """V2: Break text into chunks with context-aware preprocessing"""
    result = text
    
    # Context-aware preprocessing (before phrase rules)
    if direction == 'm2d':
        # Weather: 下了X雨 → 落咧X雨, 下X雨了 → 落X雨咧
        result = re.sub(r'下了(.{0,6})雨', lambda m: '落咧' + m.group(1) + '雨', result)
        result = re.sub(r'下了(.{0,6})雪', lambda m: '落咧' + m.group(1) + '雪', result)
        result = re.sub(r'下(.{0,6})雨了', lambda m: '落' + m.group(1) + '雨咧', result)
        result = re.sub(r'下(.{0,6})雪了', lambda m: '落' + m.group(1) + '雪咧', result)
    
    # Greedy longest-match replacement
    rules = M2D_PHRASES if direction == 'm2d' else D2M_PHRASES
    for src, dst in rules:
        if src in result and src != dst:
            result = result.replace(src, dst)
    
    # Suffix
    suffix_map = SUFFIX_M2D if direction == 'm2d' else SUFFIX_D2M
    for suffix, replacement in suffix_map.items():
        if result.endswith(suffix) and len(result) > len(suffix):
            result = result[:-len(suffix)] + replacement
            break
    
    # Fix double suffix
    if result.endswith('呃咧'):
        result = result[:-2] + '咧'
    elif result.endswith('咧呃'):
        result = result[:-2] + '咧'
    
    return result

def translate(text, direction='auto', asr_mode=False):
    """V2 translation with improved accuracy"""
    if not text or not text.strip():
        return {'result': '', 'method': 'empty', 'confidence': 0}
    
    text = text.strip()
    original_text = text
    asr_corrected = False
    
    # ASR correction
    if asr_mode or direction == 'auto':
        corrected = correct_asr(text)
        if corrected != text:
            text = corrected
            asr_corrected = True
    
    # Direction detection
    if direction == 'auto':
        direction = detect_direction(text)
    
    corpus = load_corpus()
    key = 'mandarin' if direction == 'm2d' else 'dongtai'
    target_key = 'dongtai' if direction == 'm2d' else 'mandarin'
    exact_index = _corpus_index['m2d'] if direction == 'm2d' else _corpus_index['d2m']
    
    # 1. Exact match (O(1) lookup)
    if text in exact_index:
        return {
            'result': exact_index[text],
            'method': 'exact',
            'confidence': 100,
            'direction': direction,
            'asr_corrected': asr_corrected
        }
    
    # 2. Normalize and try exact match again
    normalized = text.rstrip('。！？，、')
    if normalized != text and normalized in exact_index:
        return {
            'result': exact_index[normalized],
            'method': 'exact_normalized',
            'confidence': 98,
            'direction': direction,
            'asr_corrected': asr_corrected
        }
    
    # 3. Corpus substring search - check if any corpus entry is contained in input
    # This handles "phrase within sentence" cases
    best_sub = None
    best_sub_len = 0
    for entry_text, translation in exact_index.items():
        if entry_text in text and len(entry_text) > best_sub_len:
            best_sub = (entry_text, translation)
            best_sub_len = len(entry_text)
    
    if best_sub and best_sub_len >= 4:
        # Found a corpus phrase within the input - combine with rules
        rule_result = phrase_chunk_translate(text, direction)
        # The corpus match is more reliable for that substring
        result = text.replace(best_sub[0], best_sub[1])
        # Apply rules to remaining parts
        if result != text:
            return {
                'result': result,
                'method': 'corpus_substring+rules',
                'confidence': 88,
                'direction': direction,
                'asr_corrected': asr_corrected
            }
    
    # 4. Rule-based translation (phrase-level)
    rule_result = phrase_chunk_translate(text, direction)
    if rule_result != text:
        # Check how much was actually translated
        change_ratio = sum(1 for a, b in zip(text, rule_result) if a != b) / max(len(text), 1)
        if change_ratio > 0.15:  # At least 15% of chars changed
            confidence = min(90, 75 + int(change_ratio * 50))
            return {
                'result': rule_result,
                'method': 'rules',
                'confidence': confidence,
                'direction': direction,
                'asr_corrected': asr_corrected
            }
    
    # 5. Fuzzy match from corpus
    fuzzy = fuzzy_match(text, corpus, direction)
    if fuzzy:
        return {
            'result': fuzzy,
            'method': 'fuzzy',
            'confidence': 70,
            'direction': direction,
            'asr_corrected': asr_corrected
        }
    
    # 6. Fallback: rules only
    if rule_result != text:
        return {
            'result': rule_result,
            'method': 'fallback',
            'confidence': 50,
            'direction': direction,
            'asr_corrected': asr_corrected
        }
    
    return {
        'result': text,
        'method': 'no_translation',
        'confidence': 20,
        'direction': direction,
        'asr_corrected': asr_corrected
    }

# ============ TTS语音合成 ============
def _tts_generate(text, voice='zh-CN-XiaoxiaoNeural'):
    """生成TTS音频文件"""
    import edge_tts
    cache_dir = os.path.join(os.path.dirname(__file__), 'tts_cache')
    os.makedirs(cache_dir, exist_ok=True)
    key = hashlib.md5(f'{text}_{voice}'.encode()).hexdigest()
    filepath = os.path.join(cache_dir, f'{key}.mp3')
    if os.path.exists(filepath) and os.path.getsize(filepath) > 100:
        return filepath
    async def gen():
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(filepath)
    asyncio.run(gen())
    return filepath

def translate_with_tts(text, direction='auto', asr_mode=False, voice='zh-CN-XiaoxiaoNeural'):
    """翻译并生成原文+译文TTS音频"""
    t = translate(text, direction, asr_mode)
    
    try:
        orig_voice = 'zh-CN-YunxiNeural' if t['direction'] == 'd2m' else voice
        t['audio_original'] = _tts_generate(text, orig_voice)
    except Exception as e:
        t['audio_original'] = None
    
    try:
        trans_voice = voice if t['direction'] == 'd2m' else 'zh-CN-YunxiNeural'
        t['audio_translated'] = _tts_generate(t['result'], trans_voice)
    except Exception as e:
        t['audio_translated'] = None
    
    return t

# ============ 双模型ASR语音识别管线 ============
_DUAL_ASR_CORRECTION = {
    "格格": "搿个", "隔的": "搿个", "格个": "搿个", "隔个": "搿个",
    "隔的菜": "搿个菜",
    "我来东台": "我俫东台", "老王来屋里": "老王俫屋里",
    "刷瓜": "刷刮", "刷瓜葛": "刷刮",
    "神呢": "什呢",
    "尸体": "事体",
    "物药紧": "勿要紧", "药紧": "要紧",
    "扎十": "扎实",
    "吓他": "下子", "瞎子": "下子",
}

def _asr_correct(text):
    corrected = text
    for wrong, right in _DUAL_ASR_CORRECTION.items():
        corrected = corrected.replace(wrong, right)
    corrected = correct_asr(corrected)
    return corrected

def recognize_audio(wav_path, fusion=True):
    """双模型融合ASR识别"""
    results = {}
    
    # Model 1: WenetSpeech-Wu
    try:
        import sherpa_onnx, wave, numpy as np
        model_dir = os.path.expanduser(
            "~/asr_models/sherpa-onnx-wenetspeech-wu-u2pp-conformer-ctc-zh-int8-2026-02-03"
        )
        onnx_file = os.path.join(model_dir, "model.int8.onnx")
        tokens_file = os.path.join(model_dir, "tokens.txt")
        
        if os.path.exists(onnx_file) and os.path.exists(tokens_file):
            recognizer = sherpa_onnx.OfflineRecognizer.from_wenet_ctc(
                model=onnx_file, tokens=tokens_file, num_threads=4, provider="cpu"
            )
            with wave.open(wav_path, 'rb') as wf:
                sr = wf.getframerate()
                frames = wf.readframes(wf.getnframes())
                nc = wf.getnchannels()
            samples = np.frombuffer(frames, dtype=np.int16).astype(np.float32) / 32768.0
            if nc > 1:
                samples = samples[::nc]
            stream = recognizer.create_stream()
            stream.accept_waveform(sr, samples.tolist())
            recognizer.decode_stream(stream)
            wu_raw = stream.result.text
            wu_fixed = _asr_correct(wu_raw)
            results["wu"] = {"raw": wu_raw, "corrected": wu_fixed}
    except Exception as e:
        results["wu_error"] = str(e)
    
    # Model 2: SenseVoiceSmall
    try:
        from funasr import AutoModel as FunASRModel
        sv = FunASRModel(model="iic/SenseVoiceSmall", device="cpu", disable_update=True)
        res = sv.generate(input=wav_path)
        raw = res[0]["text"] if res else ""
        sv_raw = re.sub(r'<\|[^|]*\|>', '', raw).strip()
        sv_fixed = _asr_correct(sv_raw)
        results["sv"] = {"raw": sv_raw, "corrected": sv_fixed}
    except Exception as e:
        results["sv_error"] = str(e)
    
    # Fusion
    if fusion and "wu" in results and "sv" in results:
        wu_c = results["wu"]["corrected"]
        sv_c = results["sv"]["corrected"]
        if wu_c == sv_c:
            results["text"] = wu_c
            results["confidence"] = 0.95
            results["model_used"] = "both"
        else:
            s1 = set(wu_c.replace("，","").replace("。",""))
            s2 = set(sv_c.replace("，","").replace("。",""))
            sim = len(s1 & s2) / max(len(s1), 1) if s1 else 0
            results["text"] = wu_c
            results["confidence"] = 0.85 if sim >= 0.9 else (0.75 if sim >= 0.7 else 0.5)
            results["model_used"] = "wu_primary"
    elif "wu" in results:
        results["text"] = results["wu"]["corrected"]
        results["confidence"] = 0.8
        results["model_used"] = "wu_only"
    elif "sv" in results:
        results["text"] = results["sv"]["corrected"]
        results["confidence"] = 0.7
        results["model_used"] = "sv_only"
    else:
        results["text"] = ""
        results["confidence"] = 0.0
        results["model_used"] = "none"
    
    return results

# ============ 自测 ============
if __name__ == '__main__':
    print("=== 东台方言翻译器 v15 (短语级+上下文感知+TTS+双ASR) ===")
    tests = [
        ('你好', '普→方'),
        ('我俫今朝去哪块吃饭咧', '方→普'),
        ('今天我们去哪里吃饭', '普→方'),
        ('侯告没得什的吃', '方→普'),
        ('帮忙', '普→方'),
        ('很冷', '普→方'),
        ('蛮蛮瀴', '方→普'),
        ('帮衬下伐', '方→普'),
        ('我不知道怎么办', '普→方'),
        ('搿歇怎呃做什的', '方→普'),
        ('爷爷说晚上很冷要回家', '普→方'),
        ('嗲嗲讲侯告蛮蛮瀴要家去', '方→普'),
        ('这个东西多少钱', '普→方'),
        ('杲昃几钿', '方→普'),
        ('明天我们去买螃蟹', '普→方'),
        ('明朝我俫去买旁海', '方→普'),
    ]
    for text, expected_dir in tests:
        r = translate(text)
        dir_label = '方→普' if r['direction'] == 'd2m' else '普→方'
        match = '✓' if dir_label == expected_dir else '✗'
        print(f"  {match} [{dir_label}] {text} → {r['result']} (method={r['method']}, conf={r['confidence']})")
