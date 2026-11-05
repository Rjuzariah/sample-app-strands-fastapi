import os
from fastapi import FastAPI, Query, UploadFile, File
from typing import Annotated
from strands import Agent
from strands.models.openai import OpenAIModel
from dotenv import load_dotenv
from prompts import REQUIREMENT_ANALYZER_PROMPT, CODE_GENERATOR_PROMPT, CODE_REVIEWER_PROMPT    
from schema.spec_to_code_schema import SpecToCodeResponse, RequirementAnalysis, CodeGenerationResult, CodeReviewResult
from strands.multiagent import GraphBuilder
load_dotenv()


app = FastAPI()

@app.post("/single-agent")
async def single_agent(content: Annotated[str, Query(..., min_length=1, max_length=15000)]):

    model = OpenAIModel(
        client_args={
            "api_key": os.environ["INCEPTION_API_KEY"],       # or pull from env
            "base_url": "https://api.inceptionlabs.ai/v1",
        },
        model_id="mercury-3",
    )

    code_agent = Agent(
        model=model,
        system_prompt="""
        You are a senior Python developer.

        Given a software specification:
        1. Analyze the requirement.
        2. Generate Python code.
        3. Review your own implementation.
        4. Mention potential issues.


        Return:
        - File structure
        - File paths
        - Code content
        - Implementation assumptions

        Example output:

        {
        "files": [
            {
            "path": "",
            "content": ""
            }
        ],
        "assumptions": []
        }
        """, structured_output_model=SpecToCodeResponse)
    result = code_agent(f"Content: {content}") 
    return result


@app.post("/multi-agent")
async def multi_agent(content: Annotated[str, Query(..., min_length=1, max_length=15000)]):

    model = OpenAIModel(
        client_args={
            "api_key": os.environ["INCEPTION_API_KEY"],       # or pull from env
            "base_url": "https://api.inceptionlabs.ai/v1",
        },
        model_id="mercury-3",
    )

    requirement_analyzer_agent = Agent(model=model, system_prompt=REQUIREMENT_ANALYZER_PROMPT, callback_handler=None, structured_output_model=RequirementAnalysis)
    code_generator_agent = Agent(model=model, system_prompt=CODE_GENERATOR_PROMPT, callback_handler=None, structured_output_model=CodeGenerationResult)
    code_reviewer_agent = Agent(model=model, system_prompt=CODE_REVIEWER_PROMPT, callback_handler=None, structured_output_model=CodeReviewResult)


    builder = GraphBuilder()
    builder.add_node(requirement_analyzer_agent, "requirement_analysis")
    builder.add_node(code_generator_agent, "code_generation")
    builder.add_node(code_reviewer_agent, "code_review")

    builder.add_edge("requirement_analysis", "code_generation")
    builder.add_edge("code_generation", "code_review")

    builder.set_execution_timeout(600)
    graph = builder.build()
    result = graph(f"Content: {content}")

    print(result.results["code_generation"].result.structured_output.model_dump())
    

    return {
        "status": result.status,
        "requirement_analysis": result.results["requirement_analysis"].result.structured_output.model_dump(),
        "code_generation": result.results["code_generation"].result.structured_output.model_dump(),
        "code_review": result.results["code_review"].result.structured_output.model_dump()
    }



