# Future Plan: Media File Integrity & Disk Verification (Approach A vs Approach B)

## Overview
Currently, memory records are stored in the Qdrant vector database (`content` contains the file path, e.g. `uploads/xxx.jpg`), while physical media files reside on local disk in `uploads/`.
If an image or media file is deleted or missing from the disk, the vector database may still return the path.

This document outlines the evaluation and ready-to-implement design for verifying file existence on disk, to be deployed if initial users or production testing report missing media errors.

---

## Comparison of Approaches

### Approach A: Verify in `search_memory` (Recommended)
- **Mechanism**: When `search_memory` queries Qdrant and gets top points, check `os.path.exists()` for any media (`image`, `video`, `audio`, `document`).
- **Tool Result**: Include `"file_exists": True/False` and `"status": "file_not_found_on_disk"` in the JSON returned to the LLM.
- **Advantages**:
  1. **Dynamic & Conversational**: The LLM understands the exact situation and generates a personalized, empathetic response in the user's language (English/Hindi/Hinglish).
  2. **Candidate Fallback**: If the top result is missing from disk but match #2 exists, the LLM can seamlessly select the existing file.
  3. **Near-Zero Latency**: Checking 5 local file paths with `os.path.exists()` takes `< 0.05 milliseconds` (virtually 0 overhead).

### Approach B: Verify after `_call_llm_parse`
- **Mechanism**: Only check `os.path.exists(parsed_response.path)` after the LLM selects a single file.
- **Drawbacks**:
  1. The LLM is blind to whether files actually exist on disk during reasoning.
  2. The user receives a static, hardcoded fallback string (e.g., `"Sorry, file might be corrupted"`), losing conversational tone and language matching.

---

## Step-by-Step Implementation Guide for Approach A

When ready to implement, apply the following 2 changes:

### 1. In `api/agent/memory_store.py`:
Add `import os` and update the search loop in `search_memory`:

```python
matches = []
for point in points:
    m_type = point.payload.get("memory_type")
    content = point.payload.get("content")
    metadata = point.payload.get("metadata", {})

    match_data = {
        "score": point.score,
        "memory_type": m_type,
        "content": content,
        "metadata": metadata
    }

    if m_type in ["image", "video", "audio", "document"]:
        file_exists = False
        if content and isinstance(content, str):
            if os.path.exists(content):
                file_exists = True
            else:
                api_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
                candidate = os.path.join(api_dir, content)
                file_exists = os.path.exists(candidate)
        
        match_data["file_exists"] = file_exists
        if not file_exists:
            match_data["status"] = "file_not_found_on_disk"
            match_data["note"] = "The file was not found at its saved location. It may have been moved, deleted, or corrupted."
        else:
            match_data["status"] = "available"

    matches.append(match_data)
```

### 2. In `api/agent/prompts.py` (under Section 2 & Section 7):
Add the instruction to `SYSTEM_PROMPT`:
```text
- MEDIA FILE AVAILABILITY:
  * When searching for media (image, document, video, audio): If `file_exists` is false or status is `file_not_found_on_disk`:
    Even though the memory record is in the database, the physical file is not on disk.
    - Return `type: "not_found"`, `path: null`.
    - Message: Politely explain that the record was found in memory, but the file could not be found at its saved location (it may have been deleted or corrupted).
    - NEVER return `type: "image"` if `file_exists` is false!
```
