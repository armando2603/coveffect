from whoosh import index
from whoosh.qparser import MultifieldParser, FuzzyTermPlugin, OperatorsPlugin
from whoosh.fields import Schema, TEXT, KEYWORD, ID, STORED
from whoosh.analysis import RegexTokenizer, LowercaseFilter, StopFilter

from database.model import Metadata

IX_RELATIVE_PATH = 'api/local_data/indexdir'
ANALYZER = RegexTokenizer() | LowercaseFilter() | StopFilter()
INDEX = index.open_dir(IX_RELATIVE_PATH)
SCHEMA = Schema(
    cord_uid = ID(stored=True),
    doi = ID,
    title = TEXT(analyzer=ANALYZER),
    abstract = TEXT(analyzer=ANALYZER),
    authors = TEXT,
    lemmatized = TEXT(analyzer=ANALYZER)
)

mparser = MultifieldParser(["title","abstract"], schema=SCHEMA)
mparser.add_plugin(OperatorsPlugin())


def retrieve(_query):
    query = mparser.parse(str(_query))
    with INDEX.searcher() as s:
        results = s.search(query)
        results = [elem['cord_uid'] for elem in results]
        return results

def search(_query):
    uids = retrieve(_query)
    results = [Metadata.query.filter(Metadata.cord_uid == uid).first() for uid in uids]
    results = [md.serialize() for md in results]
    return results

if __name__ == '__main__':
    import os
    cwd = os.getcwd()
    print(cwd)
    print("You are in a testing environment")
