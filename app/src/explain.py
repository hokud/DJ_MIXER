import os
from typing import Dict
from tenacity import retry, stop_after_attempt, wait_exponential
from openai import OpenAI

_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

@retry(wait=wait_exponential(min=1, max=8), stop=stop_after_attempt(3))
def explain_transition(seed_meta: Dict, seed_feat: Dict, cand: Dict) -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return "(Set OPENAI_API_KEY to show an AI rationale.)"
    client = OpenAI(api_key=api_key)

    prompt = f"""
You are a concise DJ assistant. Explain in 1–2 sentences why the candidate track works after the seed track.
Mention specifics only: BPM match/offset, Camelot relation, and feel (e.g., gentle lift, tension→release).
Seed: {seed_meta['name']} by {', '.join(a['name'] for a in seed_meta['artists'])} [{seed_feat['tempo']:.1f} BPM, {seed_feat['camelot']}, energy {seed_feat['energy']:.2f}, dance {seed_feat['danceability']:.2f}]
Next: {cand['title']} by {cand['artist']} [{cand['tempo']:.1f} BPM, {cand['camelot']}, energy {cand['energy']:.2f}, dance {cand['danceability']:.2f}]
"""
    resp = client.chat.completions.create(
        model=_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4,
        max_tokens=120,
    )
    return resp.choices[0].message.content.strip()
