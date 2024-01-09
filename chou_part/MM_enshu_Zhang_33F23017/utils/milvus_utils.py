from pymilvus import (
    Collection,
    CollectionSchema,
    FieldSchema,
    DataType,
    connections,
    utility,
)


def create_novel_collection(novel_id, dim):
    connections.connect(alias="default", host="chou_milvus-standalone", port="19530")
    collection_name = f"novel_{novel_id}"

    if utility.has_collection(collection_name):
        print(f"Collection {collection_name} already exists.")
        connections.disconnect(alias="default")
        return False

    # Define the schema
    id_field = FieldSchema(
        name="id", dtype=DataType.INT64, is_primary=True, auto_id=True
    )
    vector_field = FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=dim)
    page_id_field = FieldSchema(name="page_id", dtype=DataType.INT64)
    sentence_id_field = FieldSchema(name="sentence_id", dtype=DataType.INT64)

    schema = CollectionSchema(
        fields=[id_field, vector_field, page_id_field, sentence_id_field],
        description=f"Novel collection for novel ID {novel_id}",
    )

    Collection(name=collection_name, schema=schema)
    print(f"Collection {collection_name} created successfully.")
    connections.disconnect(alias="default")
    return True


def add_chunks_to_collection(
    novel_id, embedding_list, page_list, sentence_list, HNSW=False
):
    connections.connect(alias="default", host="chou_milvus-standalone", port="19530")
    data = [embedding_list, page_list, sentence_list]
    print("Adding chunks to the collection...")
    collection_name = f"novel_{novel_id}"
    collection = Collection(name=collection_name)
    collection.insert(data)
    print("Chunks added successfully.")

    if HNSW:
        print("Creating HNSW index...")
        index_params = {
            "index_type": "HNSW",
            "metric_type": "L2",
            "params": {"M": 8, "efConstruction": 10},
        }
        collection.create_index(field_name="vector", index_params=index_params)
        print("HNSW index created successfully.")
    collection.release()
    connections.disconnect(alias="default")


def search_top_chunks(collection, question_vector, current_page, top_k=20):
    search_params = {"metric_type": "L2"}
    expr = f"page_id <= {current_page-1}"
    results = collection.search(
        data=[question_vector],
        anns_field="vector",
        param=search_params,
        limit=top_k,
        expr=expr,
        consistency_level="Strong",
    )
    id_list = results[0].ids
    query_expression = f"id in {id_list}"
    results = collection.query(
        expr=query_expression, output_fields=["page_id", "sentence_id"]
    )

    return results


def drop_collection(novel_id):
    connections.connect(alias="default", host="chou_milvus-standalone", port="19530")
    collection_name = f"novel_{novel_id}"
    utility.drop_collection(collection_name)
    connections.disconnect(alias="default")
    print(f"Collection {collection_name} dropped successfully.")
