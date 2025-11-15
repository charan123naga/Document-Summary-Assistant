from __future__ import annotations

import re
from typing import List, Dict
from collections import Counter

_STOPWORDS = {
    'the','a','an','and','or','but','if','while','is','are','was','were','be','been','being',
    'of','on','in','at','to','for','with','as','by','that','this','these','those','from','it','its',
    'into','out','up','down','over','under','than','then','so','such','very','can','could','may','might',
    'will','would','shall','should','do','does','did','not'
}


def _clean(text: str) -> str:
    return re.sub(r'\s+', ' ', text).strip()


def _split_sentences(text: str) -> List[str]:
   
    raw = re.split(r'(?<=[.!?])\s+', text.strip())
    sentences = [s.strip() for s in raw if s.strip()]

    return [s for s in sentences if re.search(r'[A-Za-z0-9]', s)]


def _tokenize(text: str) -> List[str]:
    return [t.lower() for t in re.findall(r'[A-Za-z0-9]+', text)]


def _score_sentence(sent: str, freq: Dict[str, int]) -> float:
    tokens = _tokenize(sent)
    content = [t for t in tokens if t not in _STOPWORDS]
    if not content:
        return 0.0
   
    return sum(freq.get(t, 0) for t in content) / len(content)


def _choose_summary_sentences(sentences: List[str], level: str) -> List[str]:
  
    if level == 'short':
        n = 2
    elif level == 'medium':
        n = 5
    else:
        n = 10
    return sentences[:n]


def _key_points(sentences: List[str], freq: Dict[str,int], max_points: int = 5) -> List[str]:
    scored = [(s, _score_sentence(s, freq)) for s in sentences]
   
    scored.sort(key=lambda x: (-x[1], sentences.index(x[0])))
    points = [s for s, sc in scored[:max_points] if sc > 0]
  
    seen = set()
    ordered = []
    for s in sentences:
        if s in points and s not in seen:
            ordered.append(s)
            seen.add(s)
    return ordered


def _suggestions(text: str, sentences: List[str]) -> List[str]:
    suggestions: List[str] = []
    if len(text) < 200:
        suggestions.append('Input text is quite short; consider providing more content for richer summaries.')
   
    long_sents = [s for s in sentences if len(_tokenize(s)) > 25]
    if long_sents:
        suggestions.append('Some sentences are long (>25 words); splitting them could improve clarity.')
  
    passive_candidates = [s for s in sentences if re.search(r'\b(was|were|been|being|is|are)\b\s+\w+ed\b', s.lower())]
    if passive_candidates:
        suggestions.append('Passive constructions detected; active voice may improve engagement.')
  
    tokens = _tokenize(text)
    freq = Counter(tokens)
    repeated = [w for w,c in freq.items() if c >= 5 and w not in _STOPWORDS]
    if repeated:
        suggestions.append('Frequent repetition of terms: ' + ', '.join(sorted(repeated)[:5]))
    if not suggestions:
        suggestions.append('Text is concise and well-structured; no major improvements needed.')
    return suggestions


def summarize(text: str, level: str = 'short') -> Dict[str, object]:
   
    original = _clean(text)
    sentences = _split_sentences(original)
    if not sentences:
        return {
            'summary': '',
            'points': [],
            'suggestions': ['No content provided to summarize.'],
            'level': level,
            'chars': 0
        }

    tokens = _tokenize(original)
    freq = Counter(t for t in tokens if t not in _STOPWORDS)

    summary_sents = _choose_summary_sentences(sentences, level)
    summary_text = ' '.join(summary_sents)
    points = _key_points(sentences, freq)
    suggestions = _suggestions(original, sentences)

    return {
        'summary': summary_text,
        'points': points,
        'suggestions': suggestions,
        'level': level,
        'chars': len(original)
    }

