"""Properties to provide GPT prompts and OpenAI API keys."""

import random
import os
import utils
from typing import Dict

API_KEYS_POOL = [
    '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',  # from Shaohan gpt4-available
    # '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',  # from Long
    # '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',  # from Yimin
    # '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',  # from Muchen
    # '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',  # from Tianshu
    # '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'   # from Josie
]


class ApiKeySelector:
    """Each time polls one api_key from pool."""

    def __init__(self):
        self.api_pool = API_KEYS_POOL
        self.rb_index = random.choice(range(len(API_KEYS_POOL)))

    def retrieve_api_key(self) -> str:
        selected_key = self.api_pool[self.rb_index % len(self.api_pool)]
        self.rb_index += 1
        return selected_key


def load_prompts_map() -> Dict:
    try:
        prompts_map = {}
        for root, dirs, files in os.walk(utils.get_root_path() + '/service/ai_prompt'):
            for file in files:
                file_path = os.path.join(root, file)
                prompt_key = file.strip().split('.')[0]
                with open(file_path, 'r', encoding='utf-8') as f:
                    prompts_map[prompt_key] = f.read().strip()
        return prompts_map
    except Exception as e:
        print('Failed to load AI prompts with error {e}', e)
