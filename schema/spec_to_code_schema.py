from pydantic import BaseModel


class RequirementAnalysis(BaseModel):
    feature: str
    functional_requirements: list[str]
    entities: list[str]
    api_requirements: list[str]
    business_rules: list[str]
    constraints: list[str]
    ambiguities: list[str]


class GeneratedFile(BaseModel):
    path: str
    content: str


class CodeGenerationResult(BaseModel):
    files: list[GeneratedFile]
    assumptions: list[str]


class ReviewIssue(BaseModel):
    severity: str
    category: str
    description: str
    suggestion: str


class CodeReviewResult(BaseModel):
    review_status: str
    issues: list[ReviewIssue]
    strengths: list[str]
    summary: str

class SpecToCodeResponse(BaseModel):
    status: str
    requirement_analysis: RequirementAnalysis
    code_generation: CodeGenerationResult
    code_review: CodeReviewResult