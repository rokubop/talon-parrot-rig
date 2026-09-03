"""Noise numbers. One rule wherever the rig means a number.

The digits are NOISE_NUMBERS in parrot_rig_settings, and tut before one of them
adds ten, so tut ah is 11 and tut mm is 19.
"""

from ..parrot_rig_settings import NOISE_NUMBERS, NUMBER_TEEN_PREFIX


def number_of(noise: str):
    """The number a noise means, or None. Takes "ah" or "tut ah"."""
    parts = (noise or "").split()
    if len(parts) == 2 and parts[0] == NUMBER_TEEN_PREFIX:
        digit = NOISE_NUMBERS.get(parts[1])
        return None if digit is None else digit + 10
    if len(parts) == 1:
        return NOISE_NUMBERS.get(parts[0])
    return None


def number_overlay(config: dict, window_ms: int, handler, label) -> dict:
    """A timed number meaning laid over an input map.

    Both keys survive. The plain one so the cheatsheet still shows the job
    underneath, and an ":init" one that input map takes because it comes later.
    That one falls through to the job once the window has closed, so the timing
    stays the handler's to keep rather than the key's.
    """
    out = dict(config)
    for noise in NOISE_NUMBERS:
        key = next((k for k in config if k.split(":")[0] == noise), None)
        if key is None:
            continue
        number, job = number_of(noise), config[key][1]
        out[f"{key}:init_{window_ms}"] = (
            label(number),
            lambda n=number, job=job: None if handler(n) else job(),
        )
    return out
