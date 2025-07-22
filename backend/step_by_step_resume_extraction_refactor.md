# Step-by-Step Plan: Resume Extraction & Quality Checklist Refactor

## Goal
- Extract as much info as possible from raw input (across all JSON Resume fields, not just one section)
- Provide a per-field quality checklist (not just section completeness)
- Remove unnecessary fields like suggested topics, missing_critical_info, and completeness summary
- Return a response that Voiceflow can use to drive the conversation naturally

---

## Steps

### 1. Change Extraction Logic: Extract All Sections
- Always attempt to extract all possible fields for the entire JSON Resume schema from the raw input, regardless of which section is inferred.
- Use either a single LLM call with a prompt that asks for the full JSON Resume structure, or run multiple extractors for each section.

### 2. Implement Per-Field Quality Check
- For every field in the JSON Resume schema (e.g., basics.name, work[0].position, etc.), check:
  - Is it present?
  - Is it plausible (e.g., email format, date format)?
  - Is it high quality (e.g., summary is not too short)?
- Build a `quality_checklist` dictionary mapping each field to a status: "ok", "missing", "low_quality", "skipped" (if user wants to skip).

### 3. Update the LLM Prompt (if using LLM extraction)
- Update the prompt to:
  - Ask the LLM to extract and fill the entire JSON Resume structure from the raw input.
  - Instruct the LLM to leave fields empty if not present, and to be as complete as possible.

### 4. Remove Unnecessary Fields from the Response
- Remove `resume_completeness_summary`, `suggested_topics`, and `missing_critical_info` from the response.
- Only return:
  - The full extracted JSON Resume data
  - The `quality_checklist` for every field

### 5. Update Response Model
- Define a new response model:
  ```python
  class GenerateResumeResponse(BaseModel):
      status: str
      json_resume: dict
      quality_checklist: dict
  ```

### 6. (Optional) Allow Skipping Fields
- If the user says "skip" or "I don't want to provide X", mark that field as "skipped" in the checklist.

### 7. (Optional) Add Quality Check Utility
- Implement a utility function that, given a JSON Resume dict, returns a `quality_checklist` for every field.

---

## Rationale
- Users often provide info for multiple sections in one message. You want to capture everything, not just one part.
- This gives Voiceflow (or any frontend) granular control over what to ask next and when the resume is "done."
- The checklist is more flexible and powerful than a section-based completeness summary.
- The API becomes simpler and more maintainable. 