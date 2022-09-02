import annoy

from database.model import Metadata

INDEX_FILE = '/storage/annoy/embeddings.ann'
#INDEX_FILE = 'local_data/annoy/embeddings.ann'
DISTANCE = 'angular'
FEATURES = 100

index = annoy.AnnoyIndex(FEATURES,DISTANCE)
index.load(INDEX_FILE)

def similar_by_cord(cord_uid):
    # Get the complete row
    original = Metadata.query.filter(Metadata.cord_uid == cord_uid).first()
    # Get similar papers by annoy_id using the index
    similar_papers = index.get_nns_by_item(original.annoy_id, 11)
    # Get the complete description for each similar paper
    results = []
    
    # Exclude the starting paper
    results = Metadata.query.filter(Metadata.annoy_id.in_(similar_papers[1:])).all()
    results = [md.serialize() for md in results]
    return results

### Attention: Right now it only checks the DOIs available in CORD19
def similar_by_doi(doi):
    # Get the complete row
    original = Metadata.query.filter(Metadata.doi == doi).first()
    # Get similar papers by annoy_id using the index
    similar_papers = index.get_nns_by_item(original.annoy_id, 11)
    # Get the complete description for each similar paper
    results = []
    
    # Exclude the starting paper
    results = Metadata.query.filter(Metadata.annoy_id.in_(similar_papers[1:])).all()
    results = [md.serialize() for md in results]
    return results
