import os
from fastapi import FastAPI
from strands import Agent
from strands.models.openai import OpenAIModel
from dotenv import load_dotenv

load_dotenv()


app = FastAPI()


@app.get("/")
async def root():

    model = OpenAIModel(
        client_args={
            "api_key": os.environ["INCEPTION_API_KEY"],       # or pull from env
            "base_url": "https://api.inceptionlabs.ai/v1",
        },
        model_id="mercury-3",
    )

    agent = Agent(model=model)

    response = agent("What are the key differences between REST and GraphQL APIs?")
    print(response)
    return response



