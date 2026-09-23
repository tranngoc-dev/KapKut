#!/usr/bin/env python3
import os
import re
import sqlite3
from pathlib import Path

base = Path(os.environ["LOCALAPPDATA"]) / "CapCut" / "User Data" / "Cache" / "ressdk_db"
pat = re.compile(rb"voice_type|effect_item_list|BV074|tonetype|sami_text")

for f in base.rglob("*"):
    if not f.is_file():
        continue
    try:
        sz = f.stat().st_size
    except OSError:
        continue
    if sz < 1000 or sz > 40_000_000:
        continue
    try:
        data = f.read_bytes() if sz <= 3_000_000 else f.read_bytes()[:3_000_000]
    except OSError:
        continue
    if pat.search(data):
        print(f"HIT {sz:10d} {f}")

for db in base.rglob("rp.db"):
    print(f"\nDB {db} ({db.stat().st_size})")
    try:
        con = sqlite3.connect(f"file:{db.as_posix()}?mode=ro", uri=True)
        tables = con.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
        print("tables:", [t[0] for t in tables])
        for (t,) in tables:
            try:
                cols = [c[1] for c in con.execute(f"PRAGMA table_info({t})").fetchall()]
                cnt = con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
                print(f"  {t}: rows={cnt} cols={cols[:15]}")
                # sample text-like columns
                for col in cols:
                    if any(k in col.lower() for k in ("json", "data", "content", "value", "body", "extra", "name")):
                        try:
                            row = con.execute(
                                f"SELECT {col} FROM {t} WHERE {col} IS NOT NULL LIMIT 1"
                            ).fetchone()
                            if row and row[0] is not None:
                                sample = row[0]
                                if isinstance(sample, bytes):
                                    sample = sample[:200]
                                else:
                                    sample = str(sample)[:200]
                                print(f"    sample {col}: {sample!r}")
                        except Exception:
                            pass
            except Exception as exc:
                print(f"  err {t}: {exc}")
        con.close()
    except Exception as exc:
        print("open err", exc)
