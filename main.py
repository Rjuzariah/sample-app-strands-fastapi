from fastapi import FastAPI, Query, UploadFile, File
from typing import Annotated
from strands import Agent
from schema.spec_to_code_schema import SpecToCodeResponse, RequirementAnalysis, CodeGenerationResult, CodeReviewResult
from strands.multiagent import GraphBuilder
from tools import query_product_database
from models_providers import ModelProvider
from utils import needs_revision, load_prompt


app = FastAPI()

@app.post("/single-agent-tool")
async def single_agent_tool(
    content: Annotated[str, Query(..., min_length=1, max_length=15000)]
):
    model_provider = ModelProvider().mercury()

    code_agent = Agent(
        model=model_provider,
        system_prompt=load_prompt("product_assistance.md"),
        tools=[
            query_product_database
        ]
    )

    result = code_agent(content)

    return result

@app.post("/single-agent")
async def single_agent(content: Annotated[str, Query(..., min_length=1, max_length=15000)]):

    model_provider = ModelProvider().mercury()

    code_agent = Agent(
        model=model_provider,
        system_prompt=load_prompt("spec_to_code_single_agent.md"), structured_output_model=SpecToCodeResponse)
    result = code_agent(f"Content: {content}") 
    return result


@app.post("/multi-agent")
async def multi_agent(content: Annotated[str, Query(..., min_length=1, max_length=15000)]):

    model_provider = ModelProvider().mercury()

    requirement_analyzer_agent = Agent(model=model_provider, system_prompt=load_prompt("requirement_analyzer.md"), structured_output_model=RequirementAnalysis)
    code_generator_agent = Agent(model=model_provider, system_prompt=load_prompt("code_generator.md"), structured_output_model=CodeGenerationResult)
    code_reviewer_agent = Agent(model=model_provider, system_prompt=load_prompt("code_reviewer.md"), structured_output_model=CodeReviewResult)


    builder = GraphBuilder()
    builder.add_node(requirement_analyzer_agent, "requirement_analysis")
    builder.add_node(code_generator_agent, "code_generation")
    builder.add_node(code_reviewer_agent, "code_review")

    builder.add_edge("requirement_analysis", "code_generation")
    builder.add_edge("code_generation", "code_review")
    builder.add_edge("code_review", "code_generation", condition=needs_revision)
    
    builder.set_max_node_executions(10)
    builder.reset_on_revisit(True)
    

    builder.set_execution_timeout(600)
    graph = builder.build()
    result = graph(f"Content: {content}")

    # print(result.execution_order)
    print("execution_count", result.execution_count)
    print("completed nodes", result.completed_nodes)
    print("failed nodes",result.failed_nodes)
    

    return {
        "status": result.status,
        "requirement_analysis": result.results["requirement_analysis"].result.structured_output.model_dump(),
        "code_generation": result.results["code_generation"].result.structured_output.model_dump(),
        "code_review": result.results["code_review"].result.structured_output.model_dump(),
        # "accumulated_usage": result.accumulated_usage,
        "all": result.to_dict()
    }


# def needs_revision(state) -> bool:
#     review_result = state.results.get("code_review")
#     if review_result is None:
#         return False
#     return review_result.result.structured_output.review_status not in ("approved", "passed")


# def load_prompt(filename):
#     return Path(
#         f"prompts/{filename}"
#     ).read_text(encoding="utf-8")

