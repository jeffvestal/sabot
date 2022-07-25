from datetime import datetime

def unix2ts(ts):
    ts = int(ts)

    return datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
