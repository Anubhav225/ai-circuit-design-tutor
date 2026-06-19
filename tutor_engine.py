"""
tutor_engine.py
Core AI engine using Groq API (llama-3.3-70b-versatile — free tier).
Handles all API calls, multi-turn conversation history, and JSON parsing.
"""

import json
import re
from typing import Optional
from groq import Groq
from prompts import (
    SYSTEM_PROMPT, QUIZ_SYSTEM_PROMPT, VIVA_SYSTEM_PROMPT,
    NOTES_SYSTEM_PROMPT, CHEATSHEET_SYSTEM_PROMPT, CHALLENGE_SYSTEM_PROMPT,
    build_question_prompt, build_quiz_prompt, build_viva_prompt,
    build_notes_prompt, build_cheatsheet_prompt, build_challenge_prompt,
)

MODEL      = "llama-3.3-70b-versatile"   # best free Groq model
MAX_TOKENS = 4096


class TutorEngine:
    """
    Wraps the Groq client and exposes tutoring endpoints.
    Maintains a rolling conversation history for the chat tab.
    """

    def __init__(self, api_key: str):
        self.client  = Groq(api_key=api_key)
        self.history: list[dict] = []   # multi-turn messages

    # ── Internal helpers ───────────────────────────────────────────────────────

    def _chat(
        self,
        user_content: str,
        system_prompt: str = SYSTEM_PROMPT,
        stateless: bool = False,
    ) -> str:
        """
        Call the Groq chat completion endpoint.
        stateless=True  → one-shot call, history not used/updated.
        stateless=False → uses and updates self.history.
        """
        if stateless:
            messages = [
                {"role": "system",    "content": system_prompt},
                {"role": "user",      "content": user_content},
            ]
        else:
            if not self.history:
                self.history.append({"role": "system", "content": system_prompt})
            self.history.append({"role": "user", "content": user_content})
            messages = self.history

        response = self.client.chat.completions.create(
            model=MODEL,
            messages=messages,
            max_tokens=MAX_TOKENS,
            temperature=0.4,
        )
        text = response.choices[0].message.content

        if not stateless:
            self.history.append({"role": "assistant", "content": text})

        return text

    @staticmethod
    def _parse_json(raw: str) -> dict | list:
        """
        Robustly extract JSON from model output.
        Handles markdown fences and surrounding prose.
        Returns a safe fallback dict on failure so the UI never crashes.
        """
        # Strip ```json ... ``` or ``` ... ```
        cleaned = re.sub(r"```(?:json)?", "", raw, flags=re.IGNORECASE).strip().rstrip("`").strip()

        # Direct parse
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            pass

        # Find first {...} or [...]
        for pat in (r"(\{[\s\S]*\})", r"(\[[\s\S]*\])"):
            m = re.search(pat, cleaned)
            if m:
                try:
                    return json.loads(m.group(1))
                except json.JSONDecodeError:
                    pass

        # Safe fallback
        return {
            "topic": "Response",
            "theory": raw,
            "known_values": [],
            "formulas_used": [],
            "calculations": [],
            "final_answer": "See explanation above.",
            "design_improvements": [],
            "common_mistakes": [],
            "practical_applications": [],
        }

    # ── Public endpoints ───────────────────────────────────────────────────────

    def ask_question(
        self,
        question: str,
        topic_hint: str = "",
        difficulty: str = "Intermediate",
    ) -> dict:
        """Main tutoring call. Returns structured JSON solution."""
        prompt = build_question_prompt(question, topic_hint, difficulty)
        raw    = self._chat(prompt, SYSTEM_PROMPT, stateless=False)
        return self._parse_json(raw)

    def generate_quiz(self, topic: str, n: int = 5, difficulty: str = "Mixed") -> list[dict]:
        raw    = self._chat(build_quiz_prompt(topic, n, difficulty), QUIZ_SYSTEM_PROMPT, stateless=True)
        result = self._parse_json(raw)
        return result if isinstance(result, list) else []

    def generate_viva(self, topic: str, n: int = 5) -> list[dict]:
        raw    = self._chat(build_viva_prompt(topic, n), VIVA_SYSTEM_PROMPT, stateless=True)
        result = self._parse_json(raw)
        return result if isinstance(result, list) else []

    def generate_notes(self, topic: str) -> dict:
        raw = self._chat(build_notes_prompt(topic), NOTES_SYSTEM_PROMPT, stateless=True)
        return self._parse_json(raw)

    def generate_cheatsheet(self, topic: str) -> dict:
        raw = self._chat(build_cheatsheet_prompt(topic), CHEATSHEET_SYSTEM_PROMPT, stateless=True)
        return self._parse_json(raw)

    def generate_challenge(self, topic: str, difficulty: str = "Intermediate") -> dict:
        raw = self._chat(build_challenge_prompt(topic, difficulty), CHALLENGE_SYSTEM_PROMPT, stateless=True)
        return self._parse_json(raw)

    def clear_history(self):
        self.history = []

    def history_preview(self) -> list[dict]:
        out = []
        for m in self.history:
            if m["role"] == "system":
                continue
            text = m.get("content", "")
            out.append({"role": m["role"], "preview": text[:120] + ("…" if len(text) > 120 else "")})
        return out
