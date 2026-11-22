"""Make an audio cue sheet with concurrency and priority conflicts."""

from decimal import Decimal
import math


def items(data, key, *, allow_empty=False):
    value = data.get(key) if isinstance(data, dict) else None
    if not isinstance(value, list) or (not value and not allow_empty) or len(value) > 500:
        raise ValueError(f"{key} must be a list of up to 500 entries")
    if any(not isinstance(item, dict) for item in value):
        raise ValueError(f"Every entry in {key} must be an object")
    return value


def number(value, field, *, positive=False):
    if type(value) not in (int, float) or not 0 <= value <= 1e12 or not math.isfinite(value):
        raise ValueError(f"{field} must be a finite nonnegative number at most 1e12")
    if positive and value == 0:
        raise ValueError(f"{field} must be greater than zero")
    return value


def label(value, field):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be nonempty text")
    return value.strip()


TITLE = "Sound Cue Sheet"
DESCRIPTION = "Turn timed audio events into a mix cue sheet with competing sounds and peak voice counts."
PROMPT = "Prepare a mixing pass ordered by timeline. Call out the specific cues, times and priority ties that need listening tests. Never claim the log proves masking, loudness or the right decibel change."


def analyze(data: dict) -> dict:
    events = []
    names = set()
    for cue in items(data, "cues"):
        name = label(cue.get("id"), "cue id")
        start = number(cue.get("start"), "start")
        duration = number(cue.get("duration"), "duration", positive=True)
        # Add decimal timecodes before converting back to a sortable timestamp.
        end = float(Decimal(str(start)) + Decimal(str(duration)))
        if end <= start:
            raise ValueError("Cue duration must be large enough to advance its timestamp")
        priority = cue.get("priority")
        if name in names or type(priority) is not int or not 1 <= priority <= 5:
            raise ValueError("Each cue needs a unique ID and integer priority from 1 to 5")
        names.add(name)
        events.append((start, end, name, priority, label(cue.get("bus"), "bus")))

    active = peak = 0
    # Ends sort before starts so adjacent cues do not count as simultaneous.
    for _, change in sorted([(e[0], 1) for e in events] + [(e[1], -1) for e in events]):
        active += change
        peak = max(peak, active)
    pairs = ties = 0
    rows = []
    for start, end, name, priority, bus in sorted(events):
        others = [event for event in events if event[2] != name and event[0] < end and start < event[1]]
        pairs += len(others)
        ties += sum(event[3] == priority for event in others)
        higher = sorted(e[2] for e in others if e[3] > priority)
        equal = sorted(e[2] for e in others if e[3] == priority)
        actions = []
        if higher:
            actions.append("Check space for " + ", ".join(higher))
        if equal:
            actions.append("Balance with " + ", ".join(equal))
        rows.append({"Cue": name, "Start (s)": start, "End (s)": round(end, 4), "Bus": bus,
                     "Priority": priority, "Mix note": "; ".join(actions) or ("Lead over lower cues" if others else "Solo")})
    return {"summary": f"{len(events)} cues produce {pairs // 2} overlapping pairs, with up to {peak} active at once.",
            "metrics": {"Cues": len(events), "Peak voices": peak, "Overlap pairs": pairs // 2,
                        "Equal-priority pairs": ties // 2}, "rows": rows}
