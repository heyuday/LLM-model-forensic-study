#%%
"""Browse cached batch results."""

import json
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "cache.db"


#%%
conn = sqlite3.connect(str(DB_PATH))
tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='batch_cache'").fetchall()
if not tables:
    print("No cache yet — run explore.py first to generate responses.")
    rows = []
else:
    rows = conn.execute(
        "SELECT key, params_json, responses_json, created_at FROM batch_cache ORDER BY created_at"
    ).fetchall()
conn.close()

batches = []
for key, params_json, responses_json, created_at in rows:
    params = json.loads(params_json)
    responses = json.loads(responses_json)
    messages_list = params.get("messages_list", [])
    if not messages_list:
        continue
    messages = messages_list[0]
    user_prompt = next((m["content"] for m in messages if m["role"] == "user"), "")
    system_prompt = next((m["content"] for m in messages if m["role"] == "system"), "N/A")
    batches.append({
        "key": key,
        "created_at": created_at,
        "model": params.get("model", "unknown"),
        "system_prompt": system_prompt,
        "user_prompt": user_prompt,
        "responses": [r.get("choices", [{}])[0].get("message", {}).get("content", "") for r in responses],
        "n": len(responses),
    })

print(f"Found {len(batches)} cached batches\n")


#%%
for i, batch in enumerate(batches[-2:]):
    print(f"{'=' * 80}")
    print(f"Batch {i + 1} | {batch['created_at']} | {batch['model']} | {batch['n']} responses")
    print(f"\nSystem prompt:\n{batch['system_prompt']}\n")
    print(f"User prompt:\n{batch['user_prompt']}")
    print(f"{'=' * 80}\n")


#%%
for i, batch in enumerate(batches[-2:]):
    print(f"Batch {i + 1} responses:")
    for j, resp in enumerate(batch["responses"]):
        print(f"\n--- Response {j + 1} ---")
        print(resp)
    print()


# %%
