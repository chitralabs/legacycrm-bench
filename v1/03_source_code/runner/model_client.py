#!/usr/bin/env python3
"""Provider clients for LegacyCRM-Bench runs.

Providers: anthropic, openai, mock_reference, mock_garbage (offline pipeline tests).
Keys are read at call time from the environment or macOS Keychain
(`security find-generic-password -s lcb_anthropic|lcb_openai -w`); never from repo files.
Every call returns a uniform record: text, usage tokens, latency, params actually sent.
"""
import json
import subprocess
import time
from pathlib import Path

V1 = Path(__file__).resolve().parent.parent.parent


def _keychain(service: str):
    try:
        out = subprocess.run(["/usr/bin/security", "find-generic-password", "-s", service, "-w"],
                             capture_output=True, text=True, timeout=10)
        return out.stdout.strip() or None
    except Exception:
        return None


def _login_shell_var(var: str):
    """Read a variable exported in the user's shell profile, in memory only (never logged)."""
    try:
        out = subprocess.run(
            ["/bin/zsh", "-c", f'source ~/.zshrc >/dev/null 2>&1; printf %s "${var}"'],
            capture_output=True, text=True, timeout=15)
        return out.stdout.strip() or None
    except Exception:
        return None


def get_key(provider: str):
    import os
    if provider == "anthropic":
        return (os.environ.get("ANTHROPIC_API_KEY") or _keychain("lcb_anthropic")
                or _login_shell_var("ANTHROPIC_API_KEY"))
    if provider == "openai":
        return (os.environ.get("OPENAI_API_KEY") or _keychain("lcb_openai")
                or _login_shell_var("OPENAI_API_KEY"))
    return None


def call_model(model_cfg: dict, prompt: str, max_tokens: int = 16000, seed: int | None = None) -> dict:
    provider = model_cfg["provider"]
    t0 = time.monotonic()
    if provider == "mock_reference":
        case_dir = Path(model_cfg["_case_dir"])
        meta = json.loads((case_dir / "case.json").read_text())
        text = "".join(f"```file:{d}\n{(case_dir / 'reference' / d).read_text()}```\n"
                       for d in meta["deliverables"])
        return {"text": text, "input_tokens": 0, "output_tokens": 0,
                "latency_s": 0.0, "params": {"provider": provider}, "raw": None}
    if provider == "mock_garbage":
        return {"text": "I cannot help with that.", "input_tokens": 0, "output_tokens": 0,
                "latency_s": 0.0, "params": {"provider": provider}, "raw": None}

    if provider == "anthropic":
        import anthropic
        client = anthropic.Anthropic(api_key=get_key("anthropic"))
        params = {"model": model_cfg["id"], "max_tokens": max_tokens,
                  "messages": [{"role": "user", "content": [
                      {"type": "text", "text": prompt,
                       "cache_control": {"type": "ephemeral"}}]}]}
        if model_cfg.get("send_temperature"):
            params["temperature"] = 0
        resp = client.messages.create(**params)
        text = "".join(b.text for b in resp.content if getattr(b, "type", "") == "text")
        u = resp.usage
        cache_write = getattr(u, "cache_creation_input_tokens", 0) or 0
        cache_read = getattr(u, "cache_read_input_tokens", 0) or 0
        return {"text": text,
                "input_tokens": u.input_tokens + cache_write + cache_read,
                "output_tokens": u.output_tokens,
                "cache_read_tokens": cache_read,
                "cache_write_tokens": cache_write,
                "uncached_input_tokens": u.input_tokens,
                "latency_s": round(time.monotonic() - t0, 3),
                "params": {k: v for k, v in params.items() if k != "messages"},
                "stop_reason": resp.stop_reason,
                "raw": resp.model_dump()}

    if provider == "openai":
        import openai
        client = openai.OpenAI(api_key=get_key("openai"))
        params = {"model": model_cfg["id"], "max_completion_tokens": max_tokens,
                  "messages": [{"role": "user", "content": prompt}]}
        if model_cfg.get("send_temperature"):
            params["temperature"] = 0
        if seed is not None and model_cfg.get("send_seed"):
            params["seed"] = seed
        try:
            resp = client.chat.completions.create(**params)
        except openai.BadRequestError:
            # some models reject temperature/seed; retry without them (recorded in params)
            params.pop("temperature", None)
            params.pop("seed", None)
            resp = client.chat.completions.create(**params)
        text = resp.choices[0].message.content or ""
        u = resp.usage
        return {"text": text, "input_tokens": u.prompt_tokens, "output_tokens": u.completion_tokens,
                "cache_read_tokens": getattr(getattr(u, "prompt_tokens_details", None), "cached_tokens", 0) or 0,
                "uncached_input_tokens": u.prompt_tokens,
                "latency_s": round(time.monotonic() - t0, 3),
                "params": {k: v for k, v in params.items() if k != "messages"},
                "stop_reason": resp.choices[0].finish_reason,
                "raw": resp.model_dump()}

    raise ValueError(f"unknown provider {provider}")


def estimate_cost_usd(model_cfg: dict, rec: dict) -> float:
    """Conservative cost from usage fields and the config's verified prices (per MTok)."""
    pin = model_cfg.get("price_in_per_mtok", 0.0)
    pout = model_cfg.get("price_out_per_mtok", 0.0)
    pcache_read = model_cfg.get("price_cache_read_per_mtok", pin * 0.1)
    cin = rec.get("uncached_input_tokens", rec.get("input_tokens", 0))
    cache_read = rec.get("cache_read_tokens", 0)
    # cache writes billed at 1.25x input on Anthropic; fold conservatively into input price
    cache_write = rec.get("cache_write_tokens", 0)
    return ((cin + 1.25 * cache_write) * pin + cache_read * pcache_read
            + rec.get("output_tokens", 0) * pout) / 1e6
