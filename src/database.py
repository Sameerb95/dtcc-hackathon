from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from tabulate import tabulate
from sqlalchemy import DateTime
from datetime import datetime, timezone

Base = declarative_base()
engine = create_engine('sqlite:///DB.db', echo=True)
Session = sessionmaker(bind=engine)
session = Session()



class Summary(Base):
    __tablename__ = 'Summaries'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    path = Column(String)
    regulations = relationship('Regulations', back_populates='summary')
    created_at =  Column(DateTime(timezone=True), default=datetime.now)


class Regulations(Base):
    __tablename__ = 'Regulations'
    upload_id = Column(Integer, primary_key=True)
    name_of_regulation = Column(String, unique=True)
    latest_version = Column(Integer, ForeignKey('Summaries.id'))
    created_at =  Column(DateTime(timezone=True), default=datetime.now)
    updated_at = Column( DateTime(timezone=True), default=datetime.now , onupdate=datetime.now)
    summary = relationship('Summary', back_populates='regulations')


class Graph(Base):
    __tablename__ = 'Graphs'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    path = Column(String)
    created_at =  Column(DateTime(timezone=True), default=datetime.now)


Base.metadata.create_all(engine)


def insert(name_of_regulation, new_summary_path, new_graph_path):
    existing_upload = session.query(Regulations).filter_by(name_of_regulation=name_of_regulation).first()


    new_summary = Summary(name=name_of_regulation,path=new_summary_path)
    session.add(new_summary)
    session.flush()

    new_graph = Graph(name=name_of_regulation,path=new_graph_path)
    session.add(new_graph)

    if existing_upload:
        existing_upload.latest_version = new_summary.id
    else:
        new_upload = Regulations(
            name_of_regulation=name_of_regulation,
            latest_version=new_summary.id
        )
        session.add(new_upload)

    session.commit()



def select(name_of_regulation):
    existing_upload = session.query(Regulations).filter_by(name_of_regulation=name_of_regulation).first()

    if existing_upload:
        current_summary = session.query(Summary).filter_by(id=existing_upload.latest_version).first()
        current_graph = session.query(Graph).filter_by(id=existing_upload.latest_version).first()

        table_data = [[
            name_of_regulation,
            current_summary.path if current_summary else 'Not Found',
            current_graph.path if current_graph else 'Not Found'
        ]]
        headers = ["Regulation", "Summary Path", "Graph Path"]
        print(tabulate(table_data, headers=headers, tablefmt="grid"))
    else:
        print(f"No paths with given regulation name found")


def select_all(name_of_regulation):
    summaries = session.query(Summary).filter_by(name=name_of_regulation).all()
    graphs = session.query(Graph).filter_by(name=name_of_regulation).all()
    table_data=[]
    for i in range(len(graphs)):
        summary_path = summaries[i].path
        graph_path = graphs[i].path
        table_data.append([summary_path, graph_path])

    headers = ["Summary Path", "Graph Path"]
    print(tabulate(table_data, headers=headers, tablefmt="grid"))

insert("GDPR2","A","a")