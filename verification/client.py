"""A small client for the System One endpoint, written for re-runs.

Three properties matter here and nothing else:

* **The key never leaves this module.** It is read from the process environment
  and, on Windows, from the current user's environment registry. It is put into
  one header and into a mask set. Every string this module hands back is filtered
  through :func:`mask`, so a value cannot reach a log, a raw record or a report
  even along an error path.
* **It never raises.** A re-run of a few hundred items must not die on item 187.
  Every failure comes back as ``{"ok": False, ...}`` with a masked short reason.
* **A busy endpoint is waited out, a rejected request is not.** 429 and 529 are
  retried with growing waits; anything else is reported at once, because
  repeating a malformed request only spends budget.

The request shape follows the endpoint's own contract: the yes/no question type
is called ``noul`` on the wire and the answer field carries the same name.
"""

import json
import re
import time
import urllib.error
import urllib.request

URL = "https://api.typesafe.ai/v1/systemone"
MODEL = "jev-latest"
KEY_NAME = "TYPESAFE_API_KEY"

#: 429 and 529 mean "come back later"; every other status is an answer.
BUSY = (429, 529)

#: Growing waits, in seconds, between attempts at a busy endpoint.
BACKOFF = (1.0, 3.0, 9.0, 27.0)

#: How much of a remote error message is worth keeping once it is masked.
DETAIL_LIMIT = 200

REDACTED = "[redacted]"

#: Anything that looks like a bearer token, even one we have never held. A
#: remembered value is caught by exact match; this catches the rest.
TOKEN_SHAPED = re.compile(r"(?i)bearer\s+[A-Za-z0-9._\-]{8,}")

_SECRETS = set()


class KeyMissing(Exception):
    """The key could not be read. The message names the variable, never a value."""


def remember(secret):
    """Add a value to the mask set. Called for every key this module reads."""
    if secret and str(secret).strip():
        _SECRETS.add(str(secret).strip())


def forget_secrets():
    """Empty the mask set. For tests; a live run never needs it."""
    _SECRETS.clear()


def mask(text, secret=None):
    """Replace every known secret, and every bearer-shaped run, with a marker."""
    out = text if isinstance(text, str) else str(text)
    for value in sorted(_SECRETS | ({str(secret)} if secret else set()),
                        key=len, reverse=True):
        if value:
            out = out.replace(value, REDACTED)
    return TOKEN_SHAPED.sub("Bearer " + REDACTED, out)


def _registry_value(name):
    """The user's environment registry on Windows; None anywhere else."""
    try:
        import winreg
    except ImportError:
        return None
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as key:
            return winreg.QueryValueEx(key, name)[0]
    except OSError:
        return None


def read_key(name=KEY_NAME, registry_reader=_registry_value):
    """The key, from the process environment first, then the user's registry."""
    import os
    value = os.environ.get(name)
    if value and value.strip():
        remember(value.strip())
        return value.strip()
    value = registry_reader(name)
    if value and str(value).strip():
        remember(str(value).strip())
        return str(value).strip()
    raise KeyMissing("%s is set neither in the environment nor for the user" % name)


def build_body(state, questions):
    """The request body. Only the yes/no type is renamed; wording is untouched."""
    translated = {}
    for qid, spec in questions.items():
        if isinstance(spec, dict) and spec.get("type") == "boolean":
            spec = dict(spec, type="noul")
        translated[qid] = spec
    return {"state": state, "model": MODEL, "questions": translated}


def urllib_transport(url, headers, body, timeout):
    """The default transport. Returns (status, text); raises on a network fault."""
    request = urllib.request.Request(url, data=body, method="POST",
                                     headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.status, response.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as error:
        return error.code, error.read().decode("utf-8", "replace")


def _failure(status, reason, detail, latency_ms=0):
    return {"ok": False, "status": status, "reason": reason,
            "detail": mask(detail)[:DETAIL_LIMIT], "answers": {},
            "model": None, "latency_ms": latency_ms, "attempts": 0}


def call(state, questions, transport=urllib_transport, key_reader=None,
         timeout=60.0, sleep=time.sleep, max_attempts=len(BACKOFF) + 1,
         url=URL):
    """One request carrying the whole battery. Never raises.

    The battery goes in one request because independent questions are answered
    in parallel inside a single call, which is how the sources being re-run send
    them too. Splitting them would change both the cost and the conditions.
    """
    try:
        secret = (key_reader or (lambda: read_key()))()
    except KeyMissing as error:
        return _failure(0, "no_key", str(error))
    except Exception as error:  # a registry read can fail in ways we do not model
        return _failure(0, "no_key", type(error).__name__)
    remember(secret)

    try:
        payload = json.dumps(build_body(state, questions),
                             ensure_ascii=False).encode("utf-8")
    except (TypeError, ValueError) as error:
        return _failure(0, "unserialisable_state", type(error).__name__)

    headers = {"Content-Type": "application/json",
               "Authorization": "Bearer " + secret}

    last = _failure(0, "not_attempted", "no attempt was made")
    for attempt in range(1, max(1, max_attempts) + 1):
        started = time.monotonic()
        try:
            status, text = transport(url, headers, payload, timeout)
        except Exception as error:  # timeouts, resets, anything the socket throws
            last = _failure(0, "network", "%s: %s" % (type(error).__name__, error),
                            _ms(started))
        else:
            last = _read(status, text, _ms(started))
        last["attempts"] = attempt
        if last["ok"] or last["status"] not in BUSY:
            return last
        if attempt >= max_attempts:
            return last
        try:
            sleep(BACKOFF[min(attempt - 1, len(BACKOFF) - 1)])
        except Exception:
            pass
    return last


def _ms(started):
    return int((time.monotonic() - started) * 1000)


def _read(status, text, latency_ms):
    if status != 200:
        out = _failure(status, "http_%d" % status, text, latency_ms)
        return out
    try:
        data = json.loads(text)
    except (TypeError, ValueError):
        return _failure(status, "not_json", "the response body was not JSON",
                        latency_ms)
    if not isinstance(data, dict) or not isinstance(data.get("answers"), dict):
        return _failure(status, "no_answers", "the response carried no answers",
                        latency_ms)
    model = data.get("model")
    return {"ok": True, "status": status, "reason": None, "detail": "",
            "answers": data["answers"],
            "model": model if isinstance(model, str) and model.strip() else None,
            "latency_ms": latency_ms, "attempts": 1,
            "input_tokens": _tokens(data)}


def _tokens(data):
    usage = data.get("usage")
    if isinstance(usage, dict):
        for field in ("input_tokens", "inputTokens"):
            if isinstance(usage.get(field), int):
                return usage[field]
    return None
