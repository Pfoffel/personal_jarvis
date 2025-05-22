from pydantic import Field, BaseModel
from typing import Optional, List, Literal

class SaveFile(BaseModel):
    """ Schema for saving the file to the corresping folder """
    file_name: str = Field(..., description="name of the file without extension (no dot)")
    content: str = Field(..., description="str content that should be written to the file")
    category: Literal["code", "writing", "notion", "research", "images", "other"] = Field(..., description="Category, beinng the folder it should create this file in")
    sub_folder: Optional[str] = Field(None, description="The subfolder it should be in within the category")
    file_type: str = Field(..., description="extension of the file without the dot")

class NewMemory(BaseModel):
    """ Schema for saving new memory """
    new_memory: str = Field(..., description="Concise summary of the new memory to be saved")
    source: Literal["user", "notion", "spring_reset_q2_2025", "other"] = Field(..., description="Source from where the new memory was taken (either 'user' or 'notion')")