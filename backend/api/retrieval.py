from whoosh import index
from whoosh.qparser import MultifieldParser
from whoosh.fields import Schema, TEXT, KEYWORD, ID, STORED
from whoosh.analysis import RegexTokenizer, LowercaseFilter, StopFilter

IX_RELATIVE_PATH = 'backend/api/local_data/indexdir'
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

def retrieve(_query):
    mparser = MultifieldParser(["title","abstract"], schema=SCHEMA)
    query = mparser.parse(str(_query))
    with INDEX.searcher() as s:
        results = s.search(query)
        return results

#if __name__ == '__main__':
#    import os
#    cwd = os.getcwd()
#    print(cwd)
#    print(retrieve("COVID"))
