import json

def label_backlink(record):
    score = 0

    # Anchor Text
    anchor = record.get("anchor_text", "").lower()
    if len(anchor) < 3 or anchor in {"click here", "read more", "visit"}:
        score -= 1
    elif any(char.isalpha() for char in anchor):
        score += 1

    # Link URL domain
    link_url = record.get("link_url", "")
    if ".gov" in link_url or ".edu" in link_url:
        score += 2
    elif any(domain in link_url for domain in ["blogspot", "weebly", "wix", "freehosting"]):
        score -= 1

    # Nofollow attribute
    if record.get("nofollow", False):
        score -= 1

    # Context richness
    context = record.get("context", "")
    if len(context) > 20 and any(word in context.lower() for word in anchor.split()):
        score += 1

    return "high" if score >= 2 else "low"

# Input/output paths
input_path = "backlinks.jsonl"
output_path = "backlinks_labeled.jsonl"

# Label and save
with open(input_path, "r", encoding="utf-8") as fin, open(output_path, "w", encoding="utf-8") as fout:
    for line in fin:
        try:
            record = json.loads(line)
            record["quality_label"] = label_backlink(record)
            fout.write(json.dumps(record) + "\n")
        except json.JSONDecodeError:
            print("Skipping malformed line.")

print(f"✅ Labeling complete. Output saved to: {output_path}")
