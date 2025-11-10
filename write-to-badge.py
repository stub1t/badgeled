from array import array
from pathlib import Path
from lednamebadge import LedNameBadge

H, W = 11, 44

def parse_led(path: str):
    raw = Path(path).read_text().splitlines()
    frames, cur = [], []
    for line in raw:
        line = line.rstrip()
        if line.strip() == '---':
            if cur:
                frames.append(normalize_frame(cur))
                cur = []
            continue
        if line.strip() == '':
            continue
        cur.append(line)
    if cur:
        frames.append(normalize_frame(cur))
    if not frames:
        raise ValueError("No frames found.")
    return frames

def normalize_frame(lines):
    # trim left/right spaces, pad/truncate to width W, then pad/truncate to H rows
    rows = [l.strip().ljust(W, '.')[0:W] for l in lines[:H]]
    while len(rows) < H:
        rows.append('.' * W)
    return rows

def frame_to_bytes(rows):
    # rows: list of H strings length W
    blocks = (W + 7) // 8
    buf = bytearray(blocks * H)  # 11 bytes per block
    for y in range(H):
        for x in range(W):
            if rows[y][x] == 'X':
                block = x // 8
                bit = 7 - (x % 8)           # MSB = leftmost pixel in the byte
                idx = block * H + y         # 11 rows per block
                buf[idx] |= (1 << bit)
    return buf, blocks

def build_and_send(frames, brightness=75, speed=4):
    scenes = []
    lengths = []
    for fr in frames:
        data, blocks = frame_to_bytes(fr)
        scenes.append(data)
        lengths.append(blocks)
    mode = 5 if len(scenes) > 1 else 4  # 5=animation, 4=static
    buf = array('B')
    buf.extend(LedNameBadge.header(tuple(lengths), (speed,), (mode,), (0,), (0,), brightness))
    for s in scenes:
        buf.extend(s)
    LedNameBadge.write(buf)

if __name__ == "__main__":
    # hardcoded for simplicity; edit values here if needed
    frames = parse_led("icons.led")
    build_and_send(frames, brightness=75, speed=4)
