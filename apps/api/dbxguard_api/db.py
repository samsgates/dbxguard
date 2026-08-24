from datetime import datetime,timezone
from sqlalchemy import DateTime,String,Text,create_engine
from sqlalchemy.orm import DeclarativeBase,Mapped,mapped_column,sessionmaker
from .settings import get_settings

class Base(DeclarativeBase): pass
class AnalysisRecord(Base):
    __tablename__="analyses"
    id:Mapped[str]=mapped_column(String(64),primary_key=True); organization_id:Mapped[str]=mapped_column(String(64),index=True,default="default")
    environment:Mapped[str]=mapped_column(String(64)); decision:Mapped[str]=mapped_column(String(32)); risk_score:Mapped[str]=mapped_column(String(16)); payload:Mapped[str]=mapped_column(Text)
    created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=lambda:datetime.now(timezone.utc))
settings=get_settings(); connect_args={"check_same_thread":False} if settings.database_url.startswith("sqlite") else {}
engine=create_engine(settings.database_url,connect_args=connect_args,pool_pre_ping=True); SessionLocal=sessionmaker(bind=engine,autoflush=False,autocommit=False)
def init_db()->None: Base.metadata.create_all(bind=engine)
def get_db():
    with SessionLocal() as session: yield session
