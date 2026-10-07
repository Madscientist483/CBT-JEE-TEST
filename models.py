import enum
import uuid
from datetime import datetime
from sqlalchemy import String, Text, Integer, Boolean, Float, ForeignKey, DateTime, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase): pass
class Cohort(str, enum.Enum):
    ELEVENTH="11th"; TWELFTH="12th"; DROPPER="dropper"
class Subject(str, enum.Enum):
    PHYSICS="Physics"; CHEMISTRY="Chemistry"; MATHEMATICS="Mathematics"
class Difficulty(str, enum.Enum):
    EASY="Easy"; MEDIUM="Medium"; HARD="Hard"

class Topic(Base):
    __tablename__="topics"
    id: Mapped[int]=mapped_column(primary_key=True)
    name: Mapped[str]=mapped_column(String(200))
    subject: Mapped[Subject]=mapped_column(SAEnum(Subject,name="subject_type",create_type=False))
    cohort: Mapped[Cohort]=mapped_column(SAEnum(Cohort,name="cohort_level",create_type=False))
    description: Mapped[str|None]=mapped_column(Text)

class Question(Base):
    __tablename__="questions"
    id: Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4)
    topic_id: Mapped[int|None]=mapped_column(ForeignKey("topics.id",ondelete="SET NULL"))
    question_text: Mapped[str]=mapped_column(Text)
    options: Mapped[dict]=mapped_column(JSONB)
    correct_answer: Mapped[list]=mapped_column(JSONB)
    explanation: Mapped[str|None]=mapped_column(Text)
    difficulty: Mapped[Difficulty]=mapped_column(SAEnum(Difficulty,name="difficulty_level",create_type=False))
    question_type: Mapped[str]=mapped_column(String(30),default="single")
    rag_confidence: Mapped[float]=mapped_column(Float,default=0)
    rag_errors: Mapped[list]=mapped_column(JSONB,default=list)
    is_rag_verified: Mapped[bool]=mapped_column(Boolean,default=False)
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),default=datetime.utcnow)

class TestResult(Base):
    __tablename__="test_results"
    id: Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4)
    cohort: Mapped[Cohort]=mapped_column(SAEnum(Cohort,name="cohort_level",create_type=False))
    score: Mapped[int]=mapped_column(Integer)
    correct_count: Mapped[int]=mapped_column(Integer)
    wrong_count: Mapped[int]=mapped_column(Integer)
    unanswered_count: Mapped[int]=mapped_column(Integer)
    total_questions: Mapped[int]=mapped_column(Integer)
    duration_seconds: Mapped[int|None]=mapped_column(Integer)
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),default=datetime.utcnow)
