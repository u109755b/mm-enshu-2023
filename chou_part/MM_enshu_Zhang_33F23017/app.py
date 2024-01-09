from flask import Flask, jsonify, request, render_template
from utils.pg_utils import connect_pg_DB, search_novel_by_title, search_novel_by_id
from utils.novel_format_utils import get_cache_file_from_gutenberg
from utils.milvus_utils import (
    create_novel_collection,
    add_chunks_to_collection,
    search_top_chunks,
    drop_collection,
)
from sentence_transformers import SentenceTransformer
from transformers import AutoModelForCausalLM, AutoTokenizer
import os
from flashrank import Ranker, RerankRequest
from pymilvus import connections, Collection
from utils.constants import MODEL2PATH, MODEL2TEPLATE, TASK2PROMPT
import logging
from vllm import LLM, SamplingParams

app = Flask(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
file_handler = logging.FileHandler("app.log")
app.logger.addHandler(file_handler)
app.logger.info("Initializing the app...")

conn, cur = connect_pg_DB()
app.logger.info("Loading the models, might take a while...")
embd_model = SentenceTransformer("sentence-transformers/all-MiniLM-L12-v2").to("cuda:1")
embedding_model2 = SentenceTransformer("BAAI/bge-base-en-v1.5").to("cuda:1")
ranker = Ranker(model_name="rank-T5-flan", cache_dir="/workspace/models")
model = LLM(model=MODEL2PATH["openhermes"])
sampling_params = SamplingParams(temperature=0.7, top_p=0.9, max_tokens=800)
template = MODEL2TEPLATE["openhermes"]
app.logger.info("Models loaded.")


def search_function(input_string, topk=10):
    input_vector = embd_model.encode(input_string)
    results = search_novel_by_title(conn, cur, input_vector, top_k=topk)
    results = [
        {"title": row[1], "author": row[2], "genre": row[3], "id": row[4]}
        for row in results
    ]
    return results


def read_cache():
    def get_cached_list():
        indices = []
        for entry in os.listdir("/workspace/OU_Courses/MM/cache/Gutenberg"):
            if entry.isdigit():  # Check if the folder name is all digits
                indices.append(int(entry))
        return indices

    list = get_cached_list()
    results = search_novel_by_id(conn, cur, list)
    results = [
        {"title": row[1], "author": row[2], "genre": row[3], "id": row[4]}
        for row in results
    ]
    return results


def set_up_Vdatabase(book_id):
    save_dir = os.path.join("/workspace/OU_Courses/MM/cache/Gutenberg", str(book_id))
    info, body_chapters, body_pages = get_cache_file_from_gutenberg(save_dir, book_id)
    if create_novel_collection(book_id, dim=768):
        embedding_list = []
        page_list = []
        sentence_list = []
        for i, page in enumerate(body_pages):
            i
            for j, sentence in enumerate(page):
                if len(sentence.split()) < 10:
                    continue
                sentence_embedding = embedding_model2.encode(
                    sentence, normalize_embeddings=True
                )
                page_list.append(i)
                sentence_list.append(j)
                embedding_list.append(sentence_embedding)
            print(f"\rPage {i+1} embedded.", end="")
        add_chunks_to_collection(book_id, embedding_list, page_list, sentence_list)


def chat(input_string, book_id, current_progress):
    connections.connect(alias="default", host="chou_milvus-standalone", port="19530")
    collection = Collection(name=f"novel_{book_id}")
    collection.load()
    save_dir = os.path.join("/workspace/OU_Courses/MM/cache/Gutenberg", str(book_id))
    info, body_chapters, body_pages = get_cache_file_from_gutenberg(save_dir, book_id)
    user_input_vector = embedding_model2.encode(
        "Represent this sentence for searching relevant passages: " + input_string,
        normalize_embeddings=True,
    )
    top_results = search_top_chunks(collection, user_input_vector, current_progress)
    top_text = [
        body_pages[result["page_id"]][result["sentence_id"]] for result in top_results
    ]
    passages = [{"text": text} for text in top_text]
    try:
        ranker.rerank(RerankRequest(query=input_string, passages=passages))
    except:
        app.logger.info(
            "Ranker failed to rerank the passages. The original order is kept."
        )
        if len(passages) == 0:
            app.logger.info(
                "Something wrong with the collection in the database. Rebuilding required."
            )
            collection.release()
            connections.disconnect(alias="default")
            drop_collection(book_id)
            set_up_Vdatabase(book_id)
            return "Collection rebuilt. Please refresh the page."

    user_message = TASK2PROMPT["copliot_answering"].format(
        contents="\n".join([d["text"] for d in passages][:5]), question=input_string
    )
    prompt = template.format(user_message=user_message)
    outputs = model.generate(prompt, sampling_params)
    generated_text = outputs[0].outputs[0].text
    collection.release()
    connections.disconnect(alias="default")
    app.logger.info(prompt)
    return generated_text.strip()


@app.route("/")
def index():
    return render_template("search.html")


@app.route("/search", methods=["POST"])
def search():
    query = request.json.get("query")
    return jsonify(search_function(query))


@app.route("/library", methods=["GET"])
def library():
    return jsonify(read_cache())


@app.route("/reading.html")
def readingpage():
    return render_template("reading.html")


@app.route("/get_book_content")
def get_book_content():
    book_id = request.args.get("book_id")
    save_dir = os.path.join("/workspace/OU_Courses/MM/cache/Gutenberg", str(book_id))
    info, body_chapters, body_pages = get_cache_file_from_gutenberg(save_dir, book_id)
    set_up_Vdatabase(book_id)
    return jsonify(
        book_title=info["Title"], book_author=info["Author"], book_content=body_pages
    )


@app.route("/book-viewer")
def book_viewer():
    book_id = request.args.get("bookId")
    return render_template("book_viewer.html", book_id=book_id)


@app.route("/total-paragraphs", methods=["GET"])
def total_paragraphs(book_content):
    return jsonify({"total": len(book_content)})


@app.route("/chat", methods=["POST"])
def handle_chat():
    input_data = request.json
    output_string = chat(
        input_data["message"], input_data["book_id"], input_data["page_id"]
    )
    return jsonify({"response": output_string})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=False)
