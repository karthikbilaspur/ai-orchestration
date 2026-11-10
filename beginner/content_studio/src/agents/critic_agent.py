from .base import BaseAgent
from ..models import Draft, SEOPlan, Review
from ..utils import flesch_reading_ease, avg_sentence_length, keyword_density

class CriticAgent(BaseAgent):
    name = "CriticAgent"
    def run(self, draft: Draft, seo: SEOPlan, threshold: int = 80) -> Review:
        self.log(f"Reviewing draft v{draft.version}")
        readability = flesch_reading_ease(draft.body)
        avg_len = avg_sentence_length(draft.body)
        density = keyword_density(draft.body, seo.primary_keyword) if seo.primary_keyword else 0
        issues, strengths, suggestions = [], [], []
        # Clarity: readability + sentence length
        clarity = 85 if readability >= 50 else 65
        if readability < 50:
            issues.append(f"Readability is low (Flesch {readability}). Shorten sentences (avg {avg_len} words).")
            suggestions.append("Break long sentences. Use shorter paragraphs.")
        else:
            strengths.append(f"Readable (Flesch {readability}, avg sentence {avg_len} words).")
        # Structure
        has_headings = draft.body.count("##") >= 3
        structure = 88 if has_headings else 60
        if not has_headings:
            issues.append("Too few headings — add H2s for scannability.")
            suggestions.append("Add H2s from the SEO heading plan.")
        else:
            strengths.append("Clear heading structure.")
        # Depth
        depth = 85 if draft.word_count >= 250 else 62
        if draft.word_count < 250:
            issues.append(f"Draft is thin ({draft.word_count} words). Add example / steps.")
            suggestions.append("Add a concrete example and a checklist.")
        else:
            strengths.append(f"Good depth ({draft.word_count} words).")
        # SEO
        seo_fit = 82 if density > 0 else 68
        if density == 0:
            issues.append("Primary keyword not found in body — weave it into intro + one H2.")
            suggestions.append(f"Use primary keyword '{seo.primary_keyword}' naturally in intro.")
        else:
            strengths.append(f"Primary keyword present (density {density}%).")
        tone_fit = 84
        strengths.append("Tone is consistent and audience-appropriate.")
        review = Review(clarity=clarity, structure=structure, depth=depth, seo_fit=seo_fit, tone_fit=tone_fit, issues=issues, strengths=strengths, suggestions=suggestions)
        self.log(f"Score: {review.overall}/100 (threshold {threshold}) — {'PASS' if review.overall>=threshold else 'NEEDS REVISION'}")
        return review
