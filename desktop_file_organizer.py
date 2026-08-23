
"""
Python Desktop File Organizer
Evidence-Based File Classification & Automation

Scans approved file types, gathers filename and document-text evidence,
classifies files by source and topic, assigns a confidence level, and only
permits automatic moves for HIGH-confidence results. Lower-confidence cases
remain in place for human review.

Safety features:
- DRY_RUN is enabled by default in this public portfolio version.
- Existing destination files are never overwritten.
- MEDIUM- and LOW-confidence files are not moved automatically.
- Move failures are caught and reported.

Requires: pypdf
"""

from pathlib import Path
from pypdf import PdfReader
import shutil


# --------------------------------------------------
# DESKTOP LOCATION
# --------------------------------------------------

# Choose the folder to organize.
# Default: standard Desktop folder.
# For Windows systems that store Desktop in OneDrive, use:
# desktop = Path.home() / "OneDrive" / "Desktop"
desktop = Path.home() / "Desktop"
# For Windows systems that store Desktop in OneDrive, use:
# desktop = Path.home() / "OneDrive" / "Desktop"
# Safety first: preview proposed moves before enabling real changes.
DRY_RUN = True
files_moved = 0
move_failures = 0

# --------------------------------------------------
# APPROVED FILE TYPES
# --------------------------------------------------

allowed_extensions = {
    ".pdf",
    ".docx",
    ".txt",
    ".xlsx",
    ".csv",
    ".jpg",
    ".jpeg",
    ".png",
}


# --------------------------------------------------
# SOURCE KEYWORDS
# --------------------------------------------------

source_keywords = {

    "Google Certifications": [
        "google certificate",
        "google certificates",
        "google certification",
        "google certifications",
        "google cert",
        "google certs",
        "google cybersecurity cert",
        "google cybersecurity",
    ],

    "Coursera": [
        "coursera",
    ],

    "WGU": [
        "wgu",
        "western governors university",
        "bscsia",
        "bsccsia",
    ],

    "CompTIA": [
        "comptia",
        "security+",
        "security plus",
    ],
}


# --------------------------------------------------
# SOURCE DETECTOR
# --------------------------------------------------

def detect_source(file_name, text=""):

    lower_name = file_name.lower()
    lower_text = text.lower()

    # Specific WGU document identity
    if "fundamentals test receipt" in lower_name:
        return "WGU"

    source_scores = {}

    for source_name, keywords in source_keywords.items():

        score = 0

        for keyword in keywords:

            if keyword in lower_name:
                score += 4

            if keyword in lower_text:
                score += 1

        source_scores[source_name] = score

    best_source = max(
        source_scores,
        key=source_scores.get
    )

    best_score = source_scores[best_source]

    if best_score >= 4:
        return best_source

    return "General"


# --------------------------------------------------
# TOPIC KEYWORDS
# --------------------------------------------------

category_keywords = {

    "Python": [
        "python",
        "function",
        "loop",
        "variable",
        "dictionary",
        "algorithm",
    ],

    "SQL": [
        "sql",
        "select",
        "database",
        "query",
        "join",
    ],

    "Linux": [
        "linux",
        "ubuntu",
        "permissions",
        "chmod",
        "chown",
        "bash",
        "terminal",
    ],

    "Security Plus Study": [
        "security+",
        "security plus",
        "comptia",
        "practice questions",
        "sy0",
    ],

    "Cybersecurity": [
        "cybersecurity",
        "access control",
        "authentication",
        "firewall",
        "malware",
        "wireshark",
        "tcpdump",
        "incident",
        "nist",
    ],

    "Network Security": [
        "network attack",
        "network attacks",
        "network security",
        "vpn",
        "proxy",
        "dns",
        "tcp",
        "packet",
        "wireshark",
        "tcpdump",
    ],

    "Threat Analysis": [
        "pasta",
        "threat model",
        "threat modeling",
        "pyramid of pain",
        "threat intelligence",
        "threat intel",
    ],

    "Phishing": [
        "phishing",
        "phishing email",
        "social engineering",
    ],

    "Vulnerability Assessments": [
        "vulnerability assessment",
        "vulnerability report",
        "security audit",
        "risk assessment",
    ],

    "Portfolio Projects": [
        "portfolio",
        "project",
        "dashboard",
        "investigation journal",
        "investigator journal",
        "professional statement",
    ],

    "Scholarships": [
        "scholarship",
        "scholarship essay",
    ],

    "Letters References": [
        "letter of reference",
        "reference letter",
        "recommendation",
        "letter",
    ],

    "Financial Aid Student Loans": [
        "fafsa",
        "pell grant",
        "student loan",
        "promissory note",
        "financial aid",
        "master promissory note",
    ],

    "Receipts Orders": [
        "amazon",
        "receipt",
        "order",
        "tracking",
    ],
}


# --------------------------------------------------
# TOPIC CLASSIFIER
# --------------------------------------------------

def classify_file(file_name, text=""):

    lower_name = file_name.lower()
    lower_text = text.lower()

    scores = {}
    filename_matches = {}

    for category_name, keywords in category_keywords.items():

        score = 0
        matched_filename = False

        # Strong WGU BSCSIA document identity
        if (
            category_name == "Cybersecurity"
            and "bachelor of science, cybersecurity and information assurance"
            in lower_text
        ):
            score += 10

        # Specific WGU Fundamentals test receipt
        if (
            category_name == "Cybersecurity"
            and "fundamentals test receipt" in lower_name
        ):
            score += 10

        for keyword in keywords:

            # Filename evidence
            if keyword in lower_name:

                matched_filename = True

                if category_name == "Cybersecurity":
                    score += 2
                else:
                    score += 4

            # Content evidence
            if keyword in lower_text:
                score += 1

        scores[category_name] = score
        filename_matches[category_name] = matched_filename

    best_category = max(
        scores,
        key=scores.get
    )

    best_score = scores[best_category]

    strong_filename_match = filename_matches[
        best_category
    ]

    if best_score >= 6:

        category = best_category
        confidence = "HIGH"

    elif best_score >= 4 and strong_filename_match:

        category = best_category
        confidence = "HIGH"

    elif best_score >= 3:

        category = best_category
        confidence = "MEDIUM"

    else:

        category = "Unknown"
        confidence = "LOW"

    return category, best_score, confidence


# --------------------------------------------------
# MULTI-TOPIC DETECTOR
# --------------------------------------------------

def detect_all_topics(file_name, text=""):

    lower_name = file_name.lower()
    lower_text = text.lower()

    detected_topics = []

    for category_name, keywords in category_keywords.items():

        topic_found = False

        for keyword in keywords:

            if keyword in lower_name:
                topic_found = True

            if keyword in lower_text:
                topic_found = True

        if topic_found:
            detected_topics.append(category_name)

    return detected_topics


# --------------------------------------------------
# DESTINATION FUNCTION
# --------------------------------------------------

def proposed_destination(
    source,
    category,
    confidence
):

    if confidence == "HIGH":
        return f"{source} / {category}"

    elif confidence == "MEDIUM":
        return "MEDIUM CONFIDENCE - REVIEW"

    else:
        return "LOW CONFIDENCE - REVIEW"


# --------------------------------------------------
# DISPLAY RESULT
# --------------------------------------------------

def display_result(
    file_name,
    source,
    category,
    score,
    confidence,
    all_topics
):

    destination = proposed_destination(
        source,
        category,
        confidence
    )

    print(f"Suggested source: {source}")
    print(f"Suggested topic: {category}")
    print(f"Evidence score: {score}")
    print(f"Confidence: {confidence}")

    secondary_topics = [
        topic
        for topic in all_topics
        if topic != category
    ]

    if secondary_topics:
        print(
            "Also detected: "
            + ", ".join(secondary_topics)
        )

    if DRY_RUN:

        if confidence == "HIGH":
            print("DRY RUN:")
            print("SAFE MOVE TEST:")
            print(f"WOULD MOVE: {file_name}")
            print(f"TO PATH: {destination}")

        else:
            print("DRY RUN:")
            print("HUMAN REVIEW REQUIRED")
            print(f"FILE: {file_name}")
            print(f"SUGGESTED REVIEW LOCATION: {destination}")
            print("NO FILE MOVE PERMITTED")


# --------------------------------------------------
# SAFE FILE MOVER
# --------------------------------------------------

def move_file_safely(
    file,
    source,
    category,
    confidence
):
    global files_moved, move_failures

    # Only HIGH-confidence files may move
    if confidence != "HIGH":
        return

    destination_folder = (
        desktop
        / source
        / category
    )

    destination_file = (
        destination_folder
        / file.name
    )

    # Never overwrite an existing file
    if destination_file.exists():

        print("MOVE BLOCKED:")
        print(
            f"File already exists: "
            f"{destination_file}"
        )

        return

    # Dry-run test
    if DRY_RUN:

        print("SAFE MOVE TEST:")
        print(f"FILE: {file.name}")
        print(
            f"WOULD MOVE TO: "
            f"{destination_file}"
        )

        return

       # Real mode
    destination_folder.mkdir(
        parents=True,
        exist_ok=True
    )

    try:

        shutil.move(
            str(file),
            str(destination_file)
        )

        files_moved += 1

        print("FILE MOVED:")
        print(f"FROM: {file}")
        print(f"TO: {destination_file}")

    except Exception as error:

        move_failures += 1

        print("MOVE FAILED:")
        print(f"FILE: {file.name}")
        print(f"Reason: {error}")
# --------------------------------------------------
# SCAN DESKTOP
# --------------------------------------------------

file_counts = {}
approved_files = []

if not desktop.exists():
    raise FileNotFoundError(
        f"Target folder does not exist: {desktop}. "
        "Update the desktop configuration near the top of the script."
    )

for item in desktop.iterdir():

    if item.is_file():

        extension = item.suffix.lower()

        if extension in allowed_extensions:

            file_counts[extension] = (
                file_counts.get(extension, 0) + 1
            )

            approved_files.append(item)


# --------------------------------------------------
# DISPLAY SCAN RESULTS
# --------------------------------------------------

print("\nDesktop File Scan")
print("-------------------")

total = 0

for extension, count in sorted(
    file_counts.items()
):

    print(f"{extension}: {count}")
    total += count

print("-------------------")
print(f"Total approved files found: {total}")
if DRY_RUN:
    print("Scan complete. DRY RUN mode - no files will be changed.")
else:
    print("Scan complete. LIVE mode - HIGH-confidence files may be moved.")


# --------------------------------------------------
# TXT FILE ANALYSIS
# --------------------------------------------------

print("\nTXT File Analysis")
print("-------------------")

for file in approved_files:

    if file.suffix.lower() != ".txt":
        continue

    print(f"\nFile: {file.name}")

    try:

        with open(
            file,
            "r",
            encoding="utf-8",
            errors="ignore"
        ) as text_file:

            content = text_file.read(3000)

    except Exception as error:

        print(
            "Could not analyze this TXT file."
        )

        print(
            "Review folder: "
            "COULD NOT ANALYZE - REVIEW"
        )

        print(f"Reason: {error}")

        continue

    source = detect_source(
        file.name,
        content
    )

    category, score, confidence = classify_file(
        file.name,
        content
    )

    all_topics = detect_all_topics(
        file.name,
        content
    )

    display_result(
        file.name,
        source,
        category,
        score,
        confidence,
        all_topics
    )

    move_file_safely(
        file,
        source,
        category,
        confidence
    )


# --------------------------------------------------
# PDF FILE ANALYSIS
# --------------------------------------------------

print("\nPDF File Analysis")
print("-------------------")

for file in approved_files:

    if file.suffix.lower() != ".pdf":
        continue

    print(f"\nFile: {file.name}")


    # ----------------------------------------------
    # TRY TO OPEN PDF
    # ----------------------------------------------

    try:

        reader = PdfReader(file)

    except Exception as error:

        print("Could not analyze this PDF.")

        print(
            "Review folder: "
            "COULD NOT ANALYZE - REVIEW"
        )

        print(f"Reason: {error}")

        if DRY_RUN:

            print("DRY RUN:")
            print("ANALYSIS FAILED - HUMAN REVIEW REQUIRED")
            print(f"FILE: {file.name}")
            print(
                "SUGGESTED REVIEW LOCATION: "
                "COULD NOT ANALYZE - REVIEW"
            )
            print("NO FILE MOVE PERMITTED")

        continue


    # ----------------------------------------------
    # PAGE COUNT
    # ----------------------------------------------

    page_count = len(reader.pages)

    print(
        f"Number of pages: {page_count}"
    )

    if page_count == 0:

        print("PDF contains no pages.")

        if DRY_RUN:

            print("DRY RUN:")
            print(f"WOULD MOVE: {file.name}")

            print(
                "TO PATH: "
                "COULD NOT ANALYZE - REVIEW"
            )

        continue


    # ----------------------------------------------
    # EXTRACT FIRST 10 PAGES
    # ----------------------------------------------

    pdf_text = ""

    pages_to_read = min(
        10,
        page_count
    )

    try:

        for page_number in range(
            pages_to_read
        ):

            page = reader.pages[
                page_number
            ]

            extracted_text = (
                page.extract_text()
            )

            if extracted_text:

                pdf_text += (
                    extracted_text + "\n"
                )

    except Exception as error:

        print(
            "Problem extracting text "
            "from this PDF."
        )

        print(f"Reason: {error}")

        pdf_text = ""


    # ----------------------------------------------
    # TEXT EXTRACTION RESULT
    # ----------------------------------------------

    if pdf_text.strip():

        print(
            "Text extraction: SUCCESS"
        )

        print(
            f"Characters extracted: "
            f"{len(pdf_text)}"
        )

    else:

        print(
            "Text extraction: "
            "NO TEXT FOUND"
        )

        print(
            "Using filename evidence only."
        )


    # ----------------------------------------------
    # SOURCE DETECTION
    # ----------------------------------------------

    source = detect_source(
        file.name,
        pdf_text
    )


    # ----------------------------------------------
    # PRIMARY TOPIC CLASSIFICATION
    # ----------------------------------------------

    category, score, confidence = classify_file(
        file.name,
        pdf_text
    )


    # ----------------------------------------------
    # MULTI-TOPIC DETECTION
    # ----------------------------------------------

    all_topics = detect_all_topics(
        file.name,
        pdf_text
    )


    # ----------------------------------------------
    # FINAL RESULT
    # ----------------------------------------------

    display_result(
        file.name,
        source,
        category,
        score,
        confidence,
        all_topics
    )

    move_file_safely(
        file,
        source,
        category,
        confidence
    )


# --------------------------------------------------
# FINISHED
# --------------------------------------------------

print(f"Files moved: {files_moved}")
print(f"Move failures: {move_failures}")
print("Files renamed: 0")
print("Files deleted: 0")
print("Files modified: 0")