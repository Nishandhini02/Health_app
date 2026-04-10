"""
gemini_fallback.py
──────────────────
Centralised Gemini model-fallback + key-rotation logic.

Fallback chain (tried in order):
  1. gemini-2.5-flash-lite   ← cheapest / fastest
  2. gemini-2.5-flash        ← mid-tier
  3. gemini-1.5-flash        ← stable fallback
  4. gemini-1.5-flash-8b     ← lightest legacy model

Both generate() and get_langchain_llm() honour the same chain so that
app.py and rag_chatbot.py stay in sync automatically.
"""

from __future__ import annotations

import time
import threading
from typing import Optional

import google.generativeai as genai

# ── Model fallback chain ──────────────────────────────────────────────────────
# Listed from most-preferred (cheapest/fastest) to least-preferred (most robust)
GEMINI_MODEL_CHAIN: list[str] = [
    "gemini-2.5-flash-lite",
    "gemini-2.5-flash",
    "gemini-1.5-flash",
    "gemini-1.5-flash-8b",
]

# ── Errors that should trigger a model switch (not just a key switch) ─────────
_MODEL_ERRORS = (
    "not found", "404", "does not exist",
    "model_not_found", "unsupported", "deprecated",
    "invalid model", "not supported",
)

# ── Errors that should trigger a key cooldown ─────────────────────────────────
_QUOTA_ERRORS = (
    "quota", "rate", "429", "resource_exhausted",
    "limit", "exceeded", "too many",
)


# ─────────────────────────────────────────────────────────────────────────────
# Round-Robin Key Manager (same as in app.py — kept here for rag_chatbot use)
# ─────────────────────────────────────────────────────────────────────────────

class RoundRobinKeyManager:
    """Thread-safe key rotator with per-key cooldown on quota errors."""

    def __init__(self, keys: list[str], cooldown_seconds: int = 70):
        self._keys     = list(keys)
        self._idx      = 0
        self._lock     = threading.Lock()
        self._cooldown = cooldown_seconds
        self._failed_at: dict[str, float] = {}

    # ── public ───────────────────────────────────────────────────────────────

    def get_ordered_keys(self) -> list[str]:
        """All keys starting from current pointer; cooling-down keys last."""
        with self._lock:
            n, idx = len(self._keys), self._idx
        now = time.time()
        available = [
            self._keys[(idx + i) % n]
            for i in range(n)
            if self._is_available(self._keys[(idx + i) % n], now)
        ]
        cooling = [k for k in self._keys if k not in available]
        return available + cooling

    def advance(self):
        with self._lock:
            self._idx = (self._idx + 1) % max(len(self._keys), 1)

    def mark_failed(self, key: str):
        self._failed_at[key] = time.time()

    def __len__(self):
        return len(self._keys)

    # ── private ──────────────────────────────────────────────────────────────

    def _is_available(self, key: str, now: Optional[float] = None) -> bool:
        ft = self._failed_at.get(key)
        if ft is None:
            return True
        return ((now or time.time()) - ft) > self._cooldown


# ─────────────────────────────────────────────────────────────────────────────
# Core generator — tries every (key × model) combination
# ─────────────────────────────────────────────────────────────────────────────

def gemini_generate_with_fallback(
    prompt: str,
    key_manager: RoundRobinKeyManager,
    model_chain: list[str] | None = None,
    feature: str = "general",
    retry_delay: float = 1.0,
) -> str:
    """
    Generate text using Gemini with full key-rotation AND model-fallback.

    Strategy
    ────────
    For each model in the chain:
        For each available API key:
            → try the call
            → on quota/rate error  : mark key as cooling, try next key
            → on model error       : break inner loop, try next model
            → on success           : advance key pointer, return result
    If every combination fails → return error string.
    """
    models = model_chain or GEMINI_MODEL_CHAIN
    last_error: Exception | None = None

    for model_name in models:
        keys_to_try = key_manager.get_ordered_keys()
        model_failed = False          # set True when THIS model is broken

        for i, key in enumerate(keys_to_try):
            try:
                genai.configure(api_key=key)
                model  = genai.GenerativeModel(model_name)
                result = model.generate_content(prompt).text

                key_manager.advance()
                _log_api("gemini", feature, True)
                print(f"✅ Gemini OK — model={model_name} key={i+1}")
                return result

            except Exception as e:
                last_error = e
                err_str    = str(e).lower()

                if any(kw in err_str for kw in _MODEL_ERRORS):
                    print(f"⚠️  Model '{model_name}' unavailable: {e}. Trying next model…")
                    model_failed = True
                    break                     # skip remaining keys for this model

                if any(kw in err_str for kw in _QUOTA_ERRORS):
                    key_manager.mark_failed(key)
                    print(f"⚠️  Key {i+1} quota hit for '{model_name}'. Cooling down…")
                else:
                    print(f"⚠️  Key {i+1} error on '{model_name}': {e}")

                if i < len(keys_to_try) - 1:
                    time.sleep(retry_delay)

        if model_failed:
            continue          # move to next model immediately

    _log_api("gemini", feature, False)
    return f"⚠️ All Gemini models/keys failed. Last error: {last_error}"


# ─────────────────────────────────────────────────────────────────────────────
# LangChain LLM with model-fallback (for rag_chatbot.py)
# ─────────────────────────────────────────────────────────────────────────────

def get_langchain_llm_with_fallback(
    key_manager: RoundRobinKeyManager,
    model_chain: list[str] | None = None,
    temperature: float = 0.3,
):
    """
    Return a LangChain ChatGoogleGenerativeAI instance, trying each model in
    the fallback chain until one initialises without error.

    The returned LLM uses the current best API key from the manager.
    Call this function each time you need a fresh LLM (e.g. per RAG invocation)
    so that key rotation is respected across sessions.
    """
    from langchain_google_genai import ChatGoogleGenerativeAI

    models = model_chain or GEMINI_MODEL_CHAIN
    keys   = key_manager.get_ordered_keys()

    if not keys:
        raise RuntimeError("No Gemini API keys available.")

    # Pick first available key
    api_key = keys[0]

    last_error: Exception | None = None
    for model_name in models:
        try:
            llm = ChatGoogleGenerativeAI(
                model=model_name,
                google_api_key=api_key,
                temperature=temperature,
            )
            # Quick smoke-test: invoke with a tiny prompt to detect dead models
            llm.invoke("hi")
            print(f"✅ LangChain LLM ready — model={model_name}")
            return llm, model_name

        except Exception as e:
            last_error = e
            err_str    = str(e).lower()
            if any(kw in err_str for kw in _MODEL_ERRORS):
                print(f"⚠️  LangChain model '{model_name}' unavailable: {e}. Trying next…")
                continue
            # Non-model error (quota, auth, etc.) — don't keep trying models
            print(f"⚠️  LangChain LLM error on '{model_name}': {e}")
            raise

    raise RuntimeError(
        f"All Gemini models failed for LangChain LLM. Last: {last_error}"
    )


# ─────────────────────────────────────────────────────────────────────────────
# Admin logging helper (optional — won't crash if admin_panel absent)
# ─────────────────────────────────────────────────────────────────────────────

def _log_api(provider: str, feature: str, success: bool):
    try:
        from admin_panel import log_api_call
        log_api_call(provider, feature, success)
    except Exception:
        pass