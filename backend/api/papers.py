from semanticscholar import SemanticScholar
from flask import jsonify
from database.model import Metadata

def get_paper(doi):
    sch = SemanticScholar(timeout=3)
    paper = sch.paper(doi)
    fields = [
        'title',
        'authors',
        'doi',
        'abstract',
        'year',
        'venue',
        'numCitedBy'
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

def get_cord_paper(doi):
    sch = SemanticScholar(timeout=3)
    paper = sch.paper(doi)
    try:
        numCitedBy = paper['numCitedBy']
    except KeyError as e:
        numCitedBy = 0
    try:
        res = Metadata.query.filter_by(doi=str(doi)).first()
        if res is None:
            return {'found':False,'metadata': ''}
        elif res.abstract == '':
            return {'found':False,'metadata': ''}
        response = {'found':True,'metadata':res.serialize()}
        response['metadata']['numCitedBy'] = numCitedBy
        return response
    except Exception as e:
        print(f'The following error occurs: {e.__class__}')
        return {'found': False, 'metadata': ''}