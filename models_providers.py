import os
from strands.models.openai import OpenAIModel
from dotenv import load_dotenv


load_dotenv()


class ModelProvider:

    @staticmethod
    def mercury():
        return OpenAIModel(
            client_args={
                "api_key": os.environ["INCEPTION_API_KEY"],
                "base_url": "https://api.inceptionlabs.ai/v1",
            },
            model_id="mercury-3",
        )