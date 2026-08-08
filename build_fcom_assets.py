import re
from collections import OrderedDict
from pathlib import Path


SOURCE = Path("a320fcom.md")
OUTLINE = Path("fcom-outline.md")
STANDARD = Path("fcom-standard.md")
MARP = Path("fcom-presentation.md")
FLASHCARDS = Path("memory-items-flashcards.md")

SECTION_NAMES = {
    "GEN": "General Information",
    "DSC": "Aircraft Systems",
    "PRO": "Procedures",
    "LIM": "Limitations",
    "OEB": "Operations Engineering Bulletins",
    "PER": "Performance",
}

PRO_NAMES = {
    "ABN": "Abnormal and Emergency Procedures",
    "NOR": "Normal Procedures",
    "SPO": "Special Operations",
}

DSC_NAMES = {
    "20": "Aircraft General",
    "21": "Air Conditioning / Pressurization / Ventilation",
    "22": "Auto Flight",
    "23": "Communications",
    "24": "Electrical",
    "25": "Equipment",
    "26": "Fire Protection",
    "27": "Flight Controls",
    "28": "Fuel",
    "29": "Hydraulic",
    "30": "Ice and Rain Protection",
    "31": "Indicating / Recording Systems",
    "32": "Landing Gear",
    "33": "Lights",
    "34": "Navigation / Surveillance",
    "35": "Oxygen",
    "36": "Pneumatic",
    "38": "Water / Waste",
    "45": "Maintenance System",
    "46": "Information Systems",
    "49": "APU",
    "52": "Doors",
    "56": "Cockpit Windows",
    "70": "Engines",
}

LIM_NAMES = {
    "AG": "Aircraft General",
    "AFS": "Auto Flight System",
    "AIR": "Air Bleed / Air Conditioning / Pressurization / Ventilation",
    "APU": "Auxiliary Power Unit",
    "COM": "Communication",
    "ENG": "Engines",
    "F_CTL": "Flight Controls",
    "FUEL": "Fuel",
    "ICE_RAIN": "Ice and Rain Protection",
    "LG": "Landing Gear",
    "NAV": "Navigation",
    "OXY": "Oxygen",
    "SURV": "Surveillance",
}

PER_NAMES = {
    "LOD": "Loading",
    "OPD": "Operational Data",
    "THR": "Thrust",
    "TOF": "Takeoff",
    "FPL": "Flight Planning",
    "CLB": "Climb",
    "CRZ": "Cruise",
    "HLD": "Holding",
    "DES": "Descent",
    "GOA": "Go-Around",
    "LDG": "Landing",
    "OEI": "One Engine Inoperative",
}


def clean_title(title):
    title = re.sub(r"\s+", " ", title.replace("|", " ")).strip()
    title = re.sub(r"\b\d{2}\s+(JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)\s+\d{2}\b.*$", "", title).strip()
    title = title.strip("- ")
    return title


def code_title_pairs(text):
    pairs = OrderedDict()
    table_pattern = re.compile(r"^\|\s*((?:GEN|DSC|PRO|LIM|OEB|PER)[-_][A-Z0-9_/-]+)\s*\|\s*([^|]*)\|")
    plain_pattern = re.compile(r"^((?:GEN|DSC|PRO|LIM|OEB|PER)[-_][A-Z0-9_/-]+)\s+(.+)$")

    for raw_line in text.splitlines():
        line = raw_line.strip()
        match = table_pattern.match(line) or plain_pattern.match(line)
        if not match:
            continue

        code, title = match.groups()
        if code in pairs:
            continue

        title = clean_title(title)
        if not title or title in {"Continued", "FCOM"}:
            title = code

        pairs[code] = title

    return pairs


def split_code(code):
    return re.split(r"[-_]", code)


def display_name(parts, index, code, title):
    if index == 0:
        return SECTION_NAMES.get(parts[0], parts[0])

    if parts[0] == "DSC" and index == 1:
        return DSC_NAMES.get(parts[1], parts[1])

    if parts[0] == "PRO" and index == 1:
        return PRO_NAMES.get(parts[1], parts[1])

    if parts[0] == "LIM" and index == 1:
        return LIM_NAMES.get(parts[1], parts[1])

    if parts[0] == "PER" and index == 1:
        return PER_NAMES.get(parts[1], parts[1])

    if index == len(parts) - 1:
        return f"{code} - {title}" if title and title != code else code

    return "-".join(parts[: index + 1])


def build_outline(pairs):
    seen = set()
    lines = ["# A320 FCOM Outline", ""]

    for code, title in pairs.items():
        parts = split_code(code)
        for index in range(len(parts)):
            path = tuple(parts[: index + 1])
            if path in seen:
                continue
            seen.add(path)
            name = display_name(parts, index, code, title)
            indent = "\t" * index
            lines.append(f"{indent}- {name}")

    lines.append("")
    return "\n".join(lines)


def build_standard(outline):
    lines = [
        "# A320 FCOM Structured Index",
        "",
        "This is a navigation-first outline extracted from the local FCOM source.",
        "The raw source file is intentionally ignored by git.",
        "",
    ]
    current_section = None

    for line in outline.splitlines()[2:]:
        if not line:
            continue
        depth = len(line) - len(line.lstrip("\t"))
        item = line.lstrip("\t- ")

        if depth == 0:
            current_section = item
            lines.extend(["", f"## {current_section}", ""])
            continue

        lines.append(f"{'  ' * (depth - 1)}- {item}")

    lines.append("")
    return "\n".join(lines)


def build_marp():
    return """---
marp: true
theme: default
paginate: true
---

# A320 FCOM

Fast navigation deck for the local FCOM outline.

---

## Core Folders

- General Information
- Aircraft Systems
- Procedures
- Limitations
- Operations Engineering Bulletins
- Performance

---

## Procedures Focus

- Normal Procedures
- Abnormal and Emergency Procedures
- Memory Items
- Supplementary Procedures
- Special Operations

---

## Study Flow

1. Open the Markmap view for the whole structure.
2. Use the standard Markdown view for quick scanning.
3. Build flashcards from Memory Items.
"""


def build_flashcards():
    return """# A320 Memory Items Flashcards

Add cards below as you study.

## Template

### Question


### Answer


---
"""


def main():
    text = SOURCE.read_text(errors="replace")
    pairs = code_title_pairs(text)
    outline = build_outline(pairs)

    OUTLINE.write_text(outline)
    STANDARD.write_text(build_standard(outline))
    MARP.write_text(build_marp())
    FLASHCARDS.write_text(build_flashcards())
    print(f"Extracted {len(pairs)} FCOM index entries.")


if __name__ == "__main__":
    main()
