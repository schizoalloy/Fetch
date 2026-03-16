import os
from functools import lru_cache


class Settings:
    nova_act_api_key: str | None
    nova_act_model_id: str

    def __init__(self) -> None:
        self.nova_act_api_key = os.getenv("NOVA_ACT_API_KEY")
        # Use latest stable model by default
        self.nova_act_model_id = os.getenv("NOVA_ACT_MODEL_ID", "nova-act-latest")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()

