import sqlalchemy as sa
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# CONN_STR = "mariadb+mariadbconnector://retriever:VeryDifficult@geco.gotdns.ch:65500/cord19"
CONN_STR = "mysql+pymysql://retriever:VeryDifficult@geco.gotdns.ch:65500/production"
# CONN_STR = "mysql+pymysql://retriever:VeryDifficult@geco.gotdns.ch:65500/cord19"
# CONN_STR = "mysql+pymysql://retriever:VeryDifficult@muteffstage-db:3306/production"
# CONN_STR = "mysql+pymysql://retriever:VeryDifficult@3.21.240.22:3306/production"
### docker-compose connection string
# CONN_STR = "mysql+pymysql://retriever:VeryDifficult@database:3306/production"
engine = sa.create_engine(CONN_STR)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))

Base = declarative_base()
Base.query = db_session.query_property()
