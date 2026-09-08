"""
Configuration and environment variable management for AudioSense AI.
Credentials are NEVER hard-coded — they are read from environment variables only.
"""

import os
from dataclasses import dataclass


@dataclass
class GraniteConfig:
    api_key: str
    project_id: str
    model_id: str
    endpoint: str

    @property
    def is_configured(self) -> bool:
        """Return True only when all four required credentials are present."""
        return all([
            self.api_key,
            self.project_id,
            self.model_id,
            self.endpoint,
        ])


def load_granite_config() -> GraniteConfig:
    """
    Load IBM Granite credentials from environment variables.
    Returns a GraniteConfig whose is_configured property reflects
    whether credentials are actually present.
    """
    return GraniteConfig(
        api_key=os.environ.get("IBM_API_KEY", ""),
        project_id=os.environ.get("IBM_PROJECT_ID", ""),
        model_id=os.environ.get(
            "IBM_GRANITE_MODEL", "ibm/granite-13b-chat-v2"
        ),
        endpoint=os.environ.get(
            "IBM_ENDPOINT", "https://us-south.ml.cloud.ibm.com"
        ),
    )
