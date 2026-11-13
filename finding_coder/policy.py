"""Review prompts, not diagnostic conclusions or warranty decisions."""
import re


def review_guidance(finding: str, candidates) -> list[str]:
    messages = []
    text = finding.lower()
    if not candidates:
        return ["No supported candidate. Search the catalog manually or gather more evidence."]
    top = candidates[0].row.description.lower()
    confirmed = re.search(r"\b(confirm\w*|replac\w*|broken|cracked|failed|stripped|torn|seized)\b", text)
    if re.search(r"\b(not confirmed|unconfirmed|not diagnosed)\b", text):
        confirmed = False
    if re.search(r"\b(replace|remove|repair)\b", top) and not confirmed:
        messages.append("Has the failed component and repair scope been confirmed? A symptom alone does not establish a repair.")
    if re.search(r"\b(no|not|without|never|isnt|isn't|doesnt|doesn't)\b", text):
        messages.append("Check negative statements against the proposed action. Text matching does not establish what has been ruled out.")
    if any(t.via_typo for c in candidates[:1] for t in c.matched):
        messages.append("Confirm the suggested spelling before selecting this line.")
    if re.search(r"\b(and|also|plus)\b", text):
        messages.append("Does this note describe more than one issue? Add a separate finding for each distinct problem.")
    return messages
