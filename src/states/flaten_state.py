from pydantic import BaseModel
from typing import List, Dict, Any
from langgraph.graph.message import add_messages
from typing import Annotated, Sequence
from langchain_core.messages import BaseMessage


class FlatState(BaseModel):
    file_path : str
    first_few_lines : str 
    about_strucutre_of_file : str 
    user_info_about_data : str 
    first_few_elements : List[Dict[str, Any]] = None
    about_first_few_elements : str = None
    sample_field_data_path : str = None
    sample_field_data_info : str = None
    sample_field_chunking_instructions : str = None
    messesages : Annotated[Sequence[BaseMessage], add_messages]
