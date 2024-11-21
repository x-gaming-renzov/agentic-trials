from langchain.prompts import PromptTemplate

correct_field_names_spellin_prompt = PromptTemplate(
    template="""
    Given below is list of field path strings in json object. 
    You have to correct the spelling of field names in the list.
    Field names are : 
    {field_names}

    OBSERVE: path is always correct for a field but spelling of word can be wrong. Which means two or more fields with incorrect spelling can have same path.
    Provide the correct spelling of the field names in the Dict. If the field name is correct, provide the same field name as the correct spelling.
    """,
    input_variables=["field_names"],
)