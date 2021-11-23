from semanticscholar import SemanticScholar
from flask import jsonify

def get_paper(doi):
    sch = SemanticScholar(timeout=3)
    paper = sch.paper(doi)
    fields = [
        'title',
        'authors',
        'doi',
        'abstract',
        'year'
    ]
    try:
        response = {}
        for field in fields:
            if field == 'authors':
                authors = [author['name'] for author in paper['authors']]
                response[field] = '; '.join(authors)
                # print(', '.join(authors))
            else:
                response[field] = paper[field]

        if 'abstract' in paper.keys():
            return {'found': True, 'metadata': response}
        else:
            return {'found': False, 'metadata': ''}
    except Exception as e:
        print(f'The following error occurs: {e.__class__}')
        return {'found': False, 'metadata': ''}