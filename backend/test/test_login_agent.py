import os
import time
import logging
from datetime import datetime
import pytz
import threading
from pymilvus import connections, Collection
from sentence_transformers import CrossEncoder
from dotenv import load_dotenv
import torch
from concurrent.futures import ThreadPoolExecutor, as_completed
import numpy as np  # ✅ For score normalization

from Chatbot.LLMClient import OpenAIClient  # ✅ OpenAI client

load_dotenv(override=True)

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# ======================================================
# 1️⃣ Lazy Milvus Connect (connect once, reuse globally)
# ======================================================
_MILVUS_LOCK = threading.RLock()
_MILVUS_COLLECTION = None

def get_milvus_collection():
    """
    Lazily connects to Milvus only once and reuses the collection instance.
    """
    global _MILVUS_COLLECTION
    with _MILVUS_LOCK:
        if _MILVUS_COLLECTION is not None:
            return _MILVUS_COLLECTION
        MILVUS_HOST = os.getenv("MILVUS_HOST")
        MILVUS_PORT = os.getenv("MILVUS_PORT")
        MILVUS_COLLECTION_NAME = os.getenv("MILVUS_COLLECTION")
        try:
            connections.connect("default", host=MILVUS_HOST, port=MILVUS_PORT)
            _MILVUS_COLLECTION = Collection(MILVUS_COLLECTION_NAME)
            _MILVUS_COLLECTION.load()
            logger.info(f"[LazyConnect] Connected to Milvus at {MILVUS_HOST}:{MILVUS_PORT}, collection: {MILVUS_COLLECTION_NAME}")
        except Exception as e:
            logger.error(f"Failed to connect to Milvus or load collection: {e}")
            raise
        return _MILVUS_COLLECTION


# ======================================================
# 2️⃣ Cached CrossEncoder (load once, reuse)
# ======================================================
_CACHED_ENCODER = None
_ENCODER_LOCK = threading.RLock()

def get_cross_encoder():
    """
    Loads CrossEncoder once and caches it for reuse.
    """
    global _CACHED_ENCODER
    with _ENCODER_LOCK:
        if _CACHED_ENCODER is not None:
            return _CACHED_ENCODER

        model_name = os.getenv("CROSS_ENCODER_MODEL", "cross-encoder/ms-marco-MiniLM-L-6-v2")
        device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"[CachedEncoder] Loading CrossEncoder model: {model_name} on {device}")
        _CACHED_ENCODER = CrossEncoder(model_name, device=device)
        return _CACHED_ENCODER


# ======================================================
# Milvus Query (unchanged, except using lazy connection)
# ======================================================
def run_milvus_query(milvus_expr: str) -> list:
    """
    Executes attribute-based Milvus query (no vector search).
    """
    try:
        collection = get_milvus_collection()
        output_fields = [
            "raw_log", "log_level", "tool", "application_id", "path", "tags", "timestamp_ms", "servicename"
        ]
        logger.info(f"Executing Milvus query: {milvus_expr}")
        results = collection.query(
            expr=milvus_expr,
            output_fields=output_fields,
            limit=1000
        )
        return [dict(record) for record in results]
    except Exception as e:
        logger.error(f"Error during Milvus query: {e}")
        raise


# ======================================================
# 3️⃣ Batched Predict + 4️⃣ Ordered Parallel Rerank + ✅ Normalization
# ======================================================
def _predict_batch(cross_encoder, pairs, batch_size):
    """
    Runs batched prediction for faster transformer inference.
    """
    all_scores = []
    for i in range(0, len(pairs), batch_size):
        batch = pairs[i:i + batch_size]
        scores = cross_encoder.predict(batch)
        all_scores.extend(scores)
    return all_scores


def crossencoder_rerank(query: str, records: list, batch_size: int = 32, num_workers: int = 0) -> list:
    """
    Optimized CrossEncoder reranking:
    - Cached model
    - Batched prediction
    - Ordered parallel rerank (fixes mismatch)
    - Global score normalization (ensures fair ranking)
    """
    if not records:
        return []

    cross_encoder = get_cross_encoder()
    pairs = [(query, r.get("raw_log", "")) for r in records]
    total = len(pairs)
    logger.info(f"CrossEncoder rerank: {total} pairs")

    # Auto decide parallelization
    use_cpu = not torch.cuda.is_available()
    if num_workers <= 0:
        num_workers = min(4, os.cpu_count() or 4)

    # === Ordered Parallel Execution (preserves batch sequence) ===
    if num_workers > 1:
        logger.info(f"[ParallelRerank] Using {num_workers} threads on CPU")
        chunk_size = max(1, len(pairs) // num_workers)
        chunks = [pairs[i:i + chunk_size] for i in range(0, len(pairs), chunk_size)]
        results = [None] * len(chunks)

        with ThreadPoolExecutor(max_workers=num_workers) as executor:
            future_to_idx = {executor.submit(_predict_batch, cross_encoder, c, batch_size): idx for idx, c in enumerate(chunks)}
            for future in as_completed(future_to_idx):
                idx = future_to_idx[future]
                results[idx] = future.result()

        # Flatten scores in correct order
        all_scores = [score for batch_scores in results for score in batch_scores]
    else:
        # Single-thread / GPU path
        all_scores = _predict_batch(cross_encoder, pairs, batch_size)

    # === ✅ Global Score Normalization ===
    all_scores_np = np.array(all_scores)
    if len(all_scores_np) > 0:
        norm_scores = (all_scores_np - all_scores_np.min()) / (all_scores_np.max() - all_scores_np.min() + 1e-8)
    else:
        norm_scores = all_scores_np

    # === Global Sort & Select Top K ===
    top_k = int(os.getenv("TOP_K_CROSS_ENCODER", "10"))
    scored_records = sorted(zip(norm_scores, records), key=lambda x: x[0], reverse=True)
    top_records = [record for score, record in scored_records[:top_k]]

    # Debug: show top few results
    for i, (score, rec) in enumerate(scored_records[:10]):
        logger.info(f"[RERANK] #{i+1}: {score:.4f} | {rec.get('application_id','N/A')} | {rec.get('raw_log','')[:120]}")

    return top_records


# ======================================================
# Context Builder (unchanged)
# ======================================================
def build_context(records: list) -> str:
    context_parts = []
    for i, record in enumerate(records):
        log_content = record.get("raw_log", "N/A")
        log_level = record.get("log_level", "N/A")
        tool = record.get("tool", "N/A")
        servicename = record.get("servicename", "N/A")
        component = record.get("component", "N/A")
        app_id = record.get("application_id", "N/A")
        timestamp_ms = record.get("timestamp_ms", "N/A")

        try:
            if timestamp_ms != "N/A":
                dt = datetime.fromtimestamp(timestamp_ms / 1000, tz=pytz.timezone("Asia/Kolkata"))
                formatted_time = dt.strftime("%Y-%m-%d %H:%M:%S %Z")
            else:
                formatted_time = "N/A"
        except Exception:
            formatted_time = "Invalid Timestamp"

        context_parts.append(f"--- Log Entry {i+1} ---")
        context_parts.append(f"Timestamp     : {formatted_time}")
        context_parts.append(f"Tool          : {tool}")
        context_parts.append(f"Service Name  : {servicename}")
        context_parts.append(f"Component     : {component}")
        context_parts.append(f"Log Level     : {log_level}")
        context_parts.append(f"Application ID: {app_id}")
        context_parts.append(f"Log Content   : {log_content}\n")

    return "\n".join(context_parts)


# ======================================================
# LLM Call (unchanged)
# ======================================================
def call_openai_llm(query: str, context: str) -> str:
    """
    Uses OpenAIClient to generate natural language responses
    based on retrieved log context.
    """
    messages = [
        {
            "role": "system",
            "content": """
    You are an expert log analytics assistant specializing in big data systems,
    particularly in understanding and explaining cluster operations and management (like Cloudera).

    Your job is to provide clear, natural, and precise answers based only on the given log entries.

    **Guidelines:**
    1. Use natural, human-like explanations — avoid overly technical jargon.
    2. Be concise if summarizing; detailed if the user asks for analysis.
    3. Maintain a professional tone and clarity in all answers.
    """,
        },
        {
            "role": "user",
            "content": f"Here are the relevant log entries:\n\n{context}\n\nUser Question: {query}\n\nAnswer:",
        },
    ]

    logger.info("Calling LLM via OpenAIClient...")
    start_time = time.time()
    try:
        client = OpenAIClient()
        response = client.chat_completion(messages)

        elapsed = time.time() - start_time
        logger.info(f"LLM call successful in {elapsed:.2f}s")

        return response or "No answer generated."
    except Exception as e:
        logger.error(f"LLM call failed: {e}")
        return "Sorry, I'm unable to process this request at the moment."
