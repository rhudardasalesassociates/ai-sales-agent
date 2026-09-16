from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class MessageStatus(str, Enum):
    ACTIVE = "active"
    HANDOFF = "handoff"
    CLOSED = "closed"


class LeadStatus(str, Enum):
    NEW = "new"
    QUALIFIED = "qualified"
    UNQUALIFIED = "unqualified"
    CONVERTED = "converted"
    SCHEDULED = "scheduled"


class ConversationState(str, Enum):
    GREETING = "greeting"
    QUALIFYING = "qualifying"
    RECOMMENDING = "recommending"
    HANDLING_OBJECTIONS = "handling_objections"
    CLOSING = "closing"
    SCHEDULING = "scheduling"
    HANDOFF = "handoff"


class Product(BaseModel):
    id: str
    name: str
    description: str
    price: float
    category: str
    in_stock: bool = True
    image_url: Optional[str] = None
    features: List[str] = []


class Lead(BaseModel):
    id: str
    messenger_id: str
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    status: LeadStatus = LeadStatus.NEW
    interested_products: List[str] = []
    notes: List[str] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ConversationMessage(BaseModel):
    role: str
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class Conversation(BaseModel):
    messenger_id: str
    state: ConversationState = ConversationState.GREETING
    messages: List[ConversationMessage] = []
    lead: Optional[Lead] = None
    language: str = "en"
    recommendations: List[Product] = []
    status: MessageStatus = MessageStatus.ACTIVE
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class WebhookEntry(BaseModel):
    id: str
    time: int
    messaging: List[dict]


class WebhookEvent(BaseModel):
    object: str
    entry: List[WebhookEntry]