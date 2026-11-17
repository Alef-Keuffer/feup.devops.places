\newpage

# Revision history {.unnumbered}

Wiegers and Beatty ask that each circulated version of a requirements document carry a revision history [@wiegers2013, ch. 27]. Each version of this report is a tag in the group's repository, and the title page names the version the PDF was built from. Table \ref{tab:revisions} lists each version, when it was released, what changed and why. Who made each change is in the repository's history.

| Version | Date | What changed | Why |
|----------------------------|------------|----------------------------------------|--------------------|
| `delivery-1-draft-0.1` | 2026-11-14 | First draft. | For the group's read-through. |
| `delivery-1` | 2026-11-18 | Billing (G3) cancels a Booking's bill on *Booking cancelled* if the Promoter hasn't paid it, and refunds no paid bill (Messaging and collaborations, Open points). Question L5 is answered. Places no longer receives *Rating changed* from Reviews (G1): every five minutes it reads every Venue's Rating in one call, and a Venue missing from the answer loses its Rating (Messaging and collaborations, System operations). The report no longer says that Promoters rate Venues, since who may rate is Reviews' rule (Application requirements). Questions L6 and L13 are answered. | G3's answer to the draft. G1's answers and report: Reviews returns every Venue's Rating in one call, and a refresh that reads them all corrects itself where a lost message wouldn't (Messaging and collaborations). Reviews lets a user who attended an Event rate its Venue. |

: The versions of this report. \label{tab:revisions}
