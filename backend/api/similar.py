import annoy

from database.model import Metadata

INDEX_FILE = 'api/local_data/annoy/embeddings.ann'
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
    for paper in similar_papers[1:]:
        results.append(Metadata.query.filter(Metadata.annoy_id == paper).first())
    results = [md.serialize() for md in results]
    return results