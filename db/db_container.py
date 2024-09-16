from sqlalchemy import create_engine, Table, Column, MetaData, String, Date, Text, inspect
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import insert
import psycopg2


class DBContainer:
    def __init__(self, user, password, host, port, database):
        self.engine = create_engine(f'postgresql://{user}:{password}@{host}:{port}/{database}')
        self.metadata = MetaData()
        self.Session = sessionmaker(bind=self.engine)
        self.inspector = inspect(self.engine)
        self.create_schemas()

    def create_schemas(self):
        # Define the news_links schema
        self.news_links = Table('news_links', self.metadata,
                                Column('topic', String),
                                Column('date', Date),
                                Column('news_link', String, primary_key=True))

        # Define the news schema
        self.news = Table('news', self.metadata,
                          Column('topic', String),
                          Column('date', Date),
                          Column('news_link', String, primary_key=True),
                          Column('title', String),
                          Column('body', Text))

        # Check if the tables already exist before creating them
        if not self.inspector.has_table('news_links'):
            self.metadata.create_all(self.engine, tables=[self.news_links])

        if not self.inspector.has_table('news'):
            self.metadata.create_all(self.engine, tables=[self.news])

    def insert_news_link(self, topic, date, news_link):
        session = self.Session()
        try:
            insert_stmt = insert(self.news_links).values(topic=topic, date=date, news_link=news_link)
            session.execute(insert_stmt)
            session.commit()
        except IntegrityError:
            session.rollback()  # Handle duplicate entry
        finally:
            session.close()

    def batch_insert_news_links(self, news_links_data):
        session = self.Session()
        try:
            # Insert batch of news_links
            session.execute(insert(self.news_links), news_links_data)
            session.commit()
        except IntegrityError as e:
            print(f"Error during batch insert: {e}")
            session.rollback()
        finally:
            session.close()

    def insert_news(self, topic, date, news_link, title, body):
        session = self.Session()
        try:
            insert_stmt = insert(self.news).values(topic=topic, date=date, news_link=news_link, title=title, body=body)
            session.execute(insert_stmt)
            session.commit()
        except IntegrityError:
            session.rollback()  # Handle duplicate entry
        finally:
            session.close()

    def get_news_links(self):
        session = self.Session()
        try:
            result = session.query(self.news_links).all()
            return [dict(row) for row in result]
        finally:
            session.close()

    def get_news(self, topic=None, date=None):
        session = self.Session()
        try:
            query = session.query(self.news)
            if topic:
                query = query.filter_by(topic=topic)
            if date:
                query = query.filter_by(date=date)
            result = query.all()
            return [dict(row) for row in result]
        finally:
            session.close()
