from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker
from config import settings
from models import Base, Topic, Question, TestResult, Cohort, Difficulty
from ai_extractor import generate_questions

engine=create_engine(settings.database_url,pool_pre_ping=True)
SessionLocal=sessionmaker(bind=engine)

@asynccontextmanager
async def lifespan(app):
    Base.metadata.create_all(engine)
    yield

app=FastAPI(title="JEE Mock Test API",version="2.0.0",lifespan=lifespan)
app.add_middleware(CORSMiddleware,allow_origins=settings.cors_origins.split(","),allow_credentials=False,allow_methods=["*"],allow_headers=["*"])

def db():
    s=SessionLocal()
    try: yield s
    finally: s.close()

class GenerateRequest(BaseModel):
    cohort:Cohort
    topic_ids:list[int]=Field(min_length=1)
    difficulty:Difficulty=Difficulty.MEDIUM
    count:int=Field(default=10,ge=1,le=50)

class SubmitRequest(BaseModel):
    cohort:Cohort
    answers:dict[str,list[str]]
    duration_seconds:int|None=None

@app.get("/health")
def health(): return {"status":"ok","service":"jee-mock-api"}

@app.get("/api/topics")
def topics(class_level:Cohort,session:Session=Depends(db)):
    rows=session.scalars(select(Topic).where(Topic.cohort==class_level).order_by(Topic.subject,Topic.name)).all()
    return [{"id":x.id,"name":x.name,"subject":x.subject.value,"cohort":x.cohort.value} for x in rows]

@app.post("/api/generate-test")
async def generate_test(p:GenerateRequest,session:Session=Depends(db)):
    rows=session.scalars(select(Topic).where(Topic.id.in_(p.topic_ids))).all()
    if not rows: raise HTTPException(404,"No valid topics found")
    per=max(1,p.count//len(rows)); out=[]
    for i,t in enumerate(rows):
        remaining=p.count-len(out)
        if remaining<=0: break
        n=min(per if i<len(rows)-1 else remaining,remaining)
        qs=await generate_questions(t.name,t.subject.value,p.difficulty.value,n)
        for q in qs:
            obj=Question(topic_id=t.id,question_text=q["question_text"],options=q["options"],
                correct_answer=q["correct_answer"],explanation=q.get("explanation"),
                difficulty=p.difficulty,question_type=q.get("question_type","single"),
                rag_confidence=.90,rag_errors=[],is_rag_verified=False)
            session.add(obj); session.flush()
            out.append({"id":str(obj.id),"topic":t.name,"subject":t.subject.value,
                        "question_text":obj.question_text,"options":obj.options,
                        "question_type":obj.question_type})
    session.commit()
    return {"count":len(out),"questions":out}

@app.post("/api/submit-test")
def submit_test(p:SubmitRequest,session:Session=Depends(db)):
    ids=list(p.answers)
    if not ids: return {"score":0,"correct":0,"wrong":0,"unanswered":0}
    qs=session.scalars(select(Question).where(Question.id.in_(ids))).all()
    correct=wrong=0
    for q in qs:
        selected=set(p.answers.get(str(q.id),[])); expected=set(q.correct_answer)
        if not selected: continue
        if selected==expected: correct+=1
        else: wrong+=1
    unanswered=max(0,len(qs)-correct-wrong)
    score=correct*4-wrong
    r=TestResult(cohort=p.cohort,score=score,correct_count=correct,wrong_count=wrong,
        unanswered_count=unanswered,total_questions=len(qs),duration_seconds=p.duration_seconds)
    session.add(r); session.commit()
    return {"score":score,"correct":correct,"wrong":wrong,"unanswered":unanswered,"total":len(qs),"result_id":str(r.id)}
