from sqlalchemy import Column, String, Text, Date, DateTime, Integer
from database.database import Base

class Metadata(Base):
    __tablename__ = 'metadata'
    cord_uid        = Column(String(30), primary_key=True)
    sha             = Column(String(800))
    source_x        = Column(String(100))
    title           = Column(String(2000))
    doi             = Column(String(100))
    pmcid           = Column(String(100))
    pubmed_id       = Column(String(100))
    license         = Column(String(100))
    abstract        = Column(Text)
    publish_time    = Column(Date)
    authors         = Column(Text)
    journal         = Column(String(500))
    mag_id          = Column(String(100))
    who_covidence_id= Column(String(100))
    arxiv_id        = Column(String(100))
    pdf_json_files  = Column(String(1000))
    pmc_json_files  = Column(String(1000))
    url             = Column(String(1000))
    s2_id           = Column(String(100))
    added_by        = Column(String(100))
    last_updated    = Column(DateTime)
    label           = Column(String(30))
    label_name      = Column(String(100))
    citescore_journal= Column(String(200))
    annoy_id        = Column(Integer)

    def __repr__(self):
        return f'<Paper {self.cord_uid}, title: \'{self.title}\'>'
    
    def serialize(self):
        return {
            'cord_uid': self.cord_uid,
            'doi': self.doi,
            'title': self.title,
            'abstract': self.abstract,
            'authors': self.authors,
            'journal': self.citescore_journal,
            'publish_time' : self.publish_time,
            'label' : self.label_name
        }