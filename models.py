from pydantic import BaseModel,Field,field_validator
from typing import Lists,Optional
from datetime import datetime

class NewsRequest(BaseModel):
    topic:str=Field(...,min_length=3,max_length=200,description='Enter the news topics to search')
    send_whatsapp:bool=Field(default=True,description='Send to whatsapp')

    @classmethod
    @field_validator('topic')
    def validate(cls, value):
        if not value.strip() :
            raise ValueError("Topics cannot be empty")
        return value.strip()

class NewsResponse(BaseModel):
        success:bool
        topic:str
        news_items:List[NewsItem] # type: ignore #ignore
        total_results:int
        whatsapp_sent:bool=False
        generated_at: datetime = Field(default_factory=datetime.utcnow)
        message: str

class ErrorResponse(BaseModel):
        success:bool=False
        error:str
        detail:Optional[str]=None

    


       
