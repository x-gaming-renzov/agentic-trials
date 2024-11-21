from pydantic import BaseModel
from typing import List, Dict, Any
from langgraph.graph.message import add_messages
from typing import Annotated, Sequence, List
from langchain_core.messages import BaseMessage
from typing import TypedDict
from pydantic import BaseModel, Field


class ElementInfoState(BaseModel):
    file_path : str
    about_strucutre_of_file : str 
    user_info_about_data : str 
    first_few_elements : List[Dict[str, Any]] = None
    about_first_few_elements : str = None
    messesages : Annotated[Sequence[BaseMessage], add_messages]
    knowledge_base_doc : List[str] = None



# Define the structure of the review result using Pydantic
class CodeReviewResult(BaseModel):
    result: str = Field(..., description="The result of the code review: 'correct' or 'incorrect'.")
    message: str = Field(..., description="Optional message returned by the review agent.")

class corrected_field_names_spelling(TypedDict):
    old_field_path : str 
    corrected_spelling_field_path : str 

class corrected_field_names_spelling_list(TypedDict):
    corrected_field_names_spelling_list : Sequence[corrected_field_names_spelling] 

# Define the state
class AgentState(TypedDict):
    file_path: str
    first_few_lines: str
    user_info_about_data: str
    first_few_elements_path_name: str
    extracted_python_code: str
    code_review_result: CodeReviewResult
    generated_code: str
    instructions_to_code: str
    code_extraction_status: str
    code_review_status: str

"""class FieldInfo(BaseModel):
    field_name: str
    field_value_info : Dict[str, Any] = Field
    field_elements : List[Any]
    new_field_name : str = None
    field_description : str = None"""

class FieldInfoState(TypedDict):
    field_info : List[Dict] = None
    messages : Annotated[Sequence[BaseMessage], add_messages]
    knowledge_base_doc : List[str] = None
    file_path : str
    element_info : str = None
    user_info_about_data : str = None
    first_few_elements : List[Dict[str, Any]] = None