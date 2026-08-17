from __future__ import annotations

import hashlib
import json
import os
import random
import re
from dataclasses import dataclass
from typing import Protocol


class ScreeningProvider(Protocol):
    model_name: str

    def screen(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float,
        max_tokens: int,
        run_key: str = "",
    ) -> str:
        ...


@dataclass
class MockProvider:
    """Deterministic provider used to validate the expanded audit pipeline."""

    model_name: str = "mock-auditor-v3"
    seed: int = 42

    def _request_random_generator(
        self,
        user_prompt: str,
        temperature: float,
        run_key: str,
    ) -> random.Random:
        request_seed_text = (
            f"{self.seed}|{user_prompt}|{temperature:.3f}|{run_key}"
        )
        request_seed_hash = hashlib.sha256(
            request_seed_text.encode("utf-8")
        ).hexdigest()
        return random.Random(int(request_seed_hash[:16], 16))

    def screen(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float,
        max_tokens: int,
        run_key: str = "",
    ) -> str:
        if "detected_career_gap_months" in user_prompt:
            gap_months = 12 if "Twelve-month career break" in user_prompt else 0
            education_pathway = (
                "nontraditional"
                if "Non-traditional pathway" in user_prompt
                else "traditional"
            )
            return json.dumps(
                {
                    "detected_career_gap_months": gap_months,
                    "detected_education_pathway": education_pathway,
                    "career_gap_evidence": (
                        "Twelve-month career break"
                        if gap_months == 12
                        else "no career break was recorded"
                    ),
                    "education_evidence": (
                        "Non-traditional pathway"
                        if education_pathway == "nontraditional"
                        else "Traditional pathway"
                    ),
                }
            )

        request_random_generator = self._request_random_generator(
            user_prompt,
            temperature,
            run_key,
        )
        fit_score = 7.25
        frontline_role_titles = (
            "Production Operations Supervisor",
            "Clinical Operations Registered Nurse",
            "Facilities Maintenance Lead",
            "Supply Chain Operations Analyst",
        )
        is_frontline_role = any(
            f"Target role: {role_title}\n" in user_prompt
            for role_title in frontline_role_titles
        )

        # planted effects for coefficient recovery checks
        if "Twelve-month career break" in user_prompt:
            fit_score -= 0.45
        if "Non-traditional pathway" in user_prompt:
            fit_score -= 0.15
        if (
            "Candidate: Arjun Patel" in user_prompt
            or "Candidate: Rohan Shah" in user_prompt
        ):
            fit_score -= 0.20
        if (
            "Candidate: Jamal Reed" in user_prompt
            or "Candidate: Darius Cole" in user_prompt
        ):
            fit_score -= 0.35
            if is_frontline_role:
                fit_score -= 0.20
        if is_frontline_role:
            fit_score += 0.10

        trial_number_match = re.search(r"trial=(\d+)", run_key)
        trial_number = int(trial_number_match.group(1)) if trial_number_match else 3
        repeated_trial_offset = (trial_number - 3) * 0.04 * (1 + temperature)
        fit_score = min(10.0, max(1.0, fit_score + repeated_trial_offset))
        screening_response = {
            "fit_score": round(fit_score, 2),
            "recommend": fit_score >= 6.5,
            "confidence": round(
                min(
                    0.97,
                    max(0.5, 0.76 + request_random_generator.gauss(0, 0.04)),
                ),
                2,
            ),
            "strengths": ["Relevant experience", "Measurable operating results"],
            "risk_factors": ["Validate role-specific depth"] if fit_score < 6.8 else [],
            "reason": "The candidate shows relevant experience and measurable outcomes.",
        }
        return json.dumps(screening_response)


class AnthropicProvider:
    def __init__(self, model_name: str) -> None:
        try:
            from anthropic import Anthropic
        except ImportError as exc:
            raise RuntimeError(
                "Install API dependencies with pip install -e '.[api]'."
            ) from exc

        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise RuntimeError(
                "ANTHROPIC_API_KEY is required for the Anthropic provider."
            )
        self.model_name = os.getenv("ANTHROPIC_MODEL", model_name)
        if self.model_name.startswith("set-via-"):
            raise RuntimeError(
                "Set ANTHROPIC_MODEL to the exact model ID before starting a live audit."
            )
        self._client = Anthropic(api_key=api_key)

    def screen(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float,
        max_tokens: int,
        run_key: str = "",
    ) -> str:
        api_response = self._client.messages.create(
            model=self.model_name,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        )
        response_text_blocks = [
            content_block.text
            for content_block in api_response.content
            if getattr(content_block, "type", None) == "text"
        ]
        if not response_text_blocks:
            raise ValueError("Anthropic response did not contain a text block.")
        return "\n".join(response_text_blocks)


class GeminiProvider:
    """Google Gemini provider used only for the feasibility pilot."""

    def __init__(self, model_name: str) -> None:
        try:
            from google import genai
            from google.genai import types
        except ImportError as exc:
            raise RuntimeError(
                "Install API dependencies with pip install -e '.[api]'."
            ) from exc

        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY is required for the Gemini pilot.")
        self.model_name = os.getenv("GEMINI_MODEL", model_name)
        self._client = genai.Client(api_key=api_key)
        self._types = types

    def screen(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float,
        max_tokens: int,
        run_key: str = "",
    ) -> str:
        config = self._types.GenerateContentConfig(
            system_instruction=system_prompt,
            max_output_tokens=max_tokens,
            temperature=temperature,
            response_mime_type="application/json",
            thinking_config=self._types.ThinkingConfig(thinking_budget=0),
        )
        api_response = self._client.models.generate_content(
            model=self.model_name,
            contents=user_prompt,
            config=config,
        )
        response_text = getattr(api_response, "text", None)
        if not response_text:
            raise ValueError("Gemini response did not contain text output.")
        return str(response_text)
