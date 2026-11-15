"""Pure forecast calculations; timestamps are UTC epoch seconds."""

def remaining(data, now):
    return [x for x in data.get("forecast", []) if x["timestampEnd"] > now]


def current(data, now):
    return next((x for x in remaining(data, now)
                 if x["timestampBegin"] <= now < x["timestampEnd"]), None)


def wet(data, now):
    return [x for x in remaining(data, now) if x["precipRate"] > 0]


def total(data, now):
    return sum(x["precipRate"] * (x["timestampEnd"] - max(now, x["timestampBegin"])) / 3600
               for x in remaining(data, now))


def episode_end(data, now):
    item = current(data, now)
    if not item or item["precipRate"] <= 0:
        return None
    for following in remaining(data, now):
        if following["precipRate"] <= 0:
            return following["timestampBegin"]
    # The episode extends beyond the forecast: its end is unknown.
    return None


def next_episode_end(data, now):
    """End of the first remaining wet episode, not the last wet minute."""
    started = False
    for item in remaining(data, now):
        if item["precipRate"] > 0:
            started = True
        elif started:
            return item["timestampBegin"]
    return None
