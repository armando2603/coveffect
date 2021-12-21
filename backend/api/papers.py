from semanticscholar import SemanticScholar
from flask import jsonify

def get_paper(doi):
    sch = SemanticScholar(timeout=3)
    paper = sch.paper(doi)
    print(paper['venue'])
    fields = [
        'title',
        'authors',
        'doi',
        'abstract',
        'year',
        'venue'
    ]
    try:
        response = {}
        for field in fields:
            if field == 'authors':
                authors = [author['name'] for author in paper['authors']]
                response[field] = '; '.join(authors)
                # print(', '.join(authors))
            elif field == 'venue':
                response['journal'] = paper[field]
            else:
                response[field] = paper[field]
        response['cord_uid'] = ''
        if 'abstract' in paper.keys():
            return {'found': True, 'metadata': response}
        else:
            return {'found': False, 'metadata': ''}
    except Exception as e:
        print(f'The following error occurs: {e.__class__}')
        return {'found': False, 'metadata': ''}