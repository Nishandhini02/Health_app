# from langchain_community.vectorstores import FAISS
# from langchain_community.embeddings import HuggingFaceEmbeddings
# # run from langchain_huggingface import HuggingFaceEmbeddings
# from langchain_core.prompts import ChatPromptTemplate
# from langchain_core.output_parsers import StrOutputParser

# from langchain_google_genai import ChatGoogleGenerativeAI
# from dotenv import load_dotenv; load_dotenv()
# import os
# API_KEY = os.getenv("GEMINI_API_KEY")
# import os
# #s.environ["HF_HOME"] = "D:/hf_cache"

# def create_rag(api_key):

#     embeddings = HuggingFaceEmbeddings(
#         model_name="sentence-transformers/all-MiniLM-L6-v2",
#         cache_folder="D:/hf_cache"
#     )

#     vectorstore = FAISS.load_local(
#         "vector_db",
#         embeddings,
#         allow_dangerous_deserialization=True
#     )

#     llm = ChatGoogleGenerativeAI(
#         model="gemini-2.5-flash",
#         google_api_key=API_KEY
#     )

#     prompt = ChatPromptTemplate.from_template(
#         """
# You are a medical assistant.

# Use the context to answer the question.

# If the answer is not in the context, use your medical knowledge to give a helpful answer.
# Context:
# {context}

# Question:
# {question}

# Answer:
# """
#     )

#     # --------------------------------------------------
#     # Custom RAG Function (with similarity score)
#     # --------------------------------------------------

#     def rag_with_score(question):

#         docs_with_scores = vectorstore.similarity_search_with_score(
#             question,
#             k=3
#         )

#         context = ""
#         scores = []

#         for doc, score in docs_with_scores:

#             context += doc.page_content + "\n\n"

#             scores.append(score)

#         final_prompt = prompt.format(
#             context=context,
#             question=question
#         )

#         response = llm.invoke(final_prompt)

#         return {
#             "answer": response.content,
#             "similarity_scores": scores,
#             "context": context
#         }

#     return rag_with_score



import os
import re
import pickle

from langchain_community.vectorstores import FAISS
#from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")


# ─────────────────────────────────────────────────────────────────────────────
# QUERY FILTER — runs BEFORE retrieval
# ─────────────────────────────────────────────────────────────────────────────
_NON_MEDICAL_PATTERNS = [
    r"\b(what is your name|who are you|your name|tell me your name)\b",
    r"\b(who made you|who created you|who built you|who developed you)\b",
    r"\b(are you (a |an )?(ai|bot|robot|human|real|chatgpt|gemini))\b",
    r"^(hi+|hello+|hey+|howdy|yo+|sup|what'?s up)[!\s.?]*$",
    r"^(good (morning|afternoon|evening|night))[!\s.?]*$",
    r"^(how are you|how r u|how do you do)[?\s!.]*$",
    r"^(thanks?|thank you|thx|ty|ok|okay|sure|cool|great|nice)[!\s.?]*$",
    r"^(bye|goodbye|see you|cya)[!\s.?]*$",
    r"\b(write (me )?(a |an )?(poem|song|story|joke|essay|code|program))\b",
    r"\b(recommend (a |an )?(movie|film|show|book|game|restaurant|hotel))\b",
    r"\b(weather|stock (price|market)|crypto|bitcoin|news today)\b",
    r"\b(username|password|login|account|email address|phone number)\b",
    r"\b(give (me )?(my |the )?(user|account|personal) (name|info|details|data))\b",
    r"\b(how to (kill|hurt|harm|poison|overdose|suicide|self.?harm))\b",
    r"\b(drug (abuse|trafficking|dealing)|illegal (drugs?|substances?))\b",
]

_MEDICAL_KEYWORDS = [
    "symptom","disease","diagnos","treatment","medicine","medication",
    "drug","dose","dosage","blood","sugar","glucose","pressure",
    "diabetes","hypertension","cardiac","heart","kidney","liver",
    "cancer","infection","fever","pain","headache","chest","breath",
    "insulin","cholesterol","bmi","obesity","diet","nutrition",
    "vitamin","mineral","hormone","thyroid","allergy","asthma",
    "surgery","vaccine","hospital","doctor","physician","nurse",
    "prescription","side effect","risk","prevention","exercise",
    "mental health","anxiety","depression","therapy","sleep",
    "pregnancy","period","menstrual","bone","muscle","joint",
    "stroke","seizure","nerve","skin","rash","wound","injury",
]

_COMPILED_PATTERNS = [re.compile(p, re.IGNORECASE) for p in _NON_MEDICAL_PATTERNS]


def _is_too_short(query: str) -> bool:
    return len(query.strip()) < 3


def _has_medical_keyword(query: str) -> bool:
    q = query.lower()
    return any(kw in q for kw in _MEDICAL_KEYWORDS)


def filter_query(query: str):
    """Returns (cleaned_query, error_message | None)."""
    cleaned = re.sub(r"\s+", " ", query.strip())

    if _is_too_short(cleaned):
        return cleaned, "Please type a medical question so I can help you."

    if _has_medical_keyword(cleaned):
        return cleaned, None

    for pattern in _COMPILED_PATTERNS:
        if pattern.search(cleaned):
            p_str = pattern.pattern
            if any(x in p_str for x in ["kill","hurt","harm","poison",
                                          "overdose","suicide","self.?harm",
                                          "trafficking","illegal"]):
                return cleaned, (
                    "⚠️ I'm a medical assistant and cannot help with that. "
                    "If someone is in crisis, please contact emergency services."
                )
            if any(x in p_str for x in ["username","password","account",
                                          "email","phone","personal"]):
                return cleaned, (
                    "🔒 I don't have access to personal or account information. "
                    "I can only answer medical and health-related questions."
                )
            if any(x in p_str for x in ["poem","song","story","joke","movie",
                                          "book","game","weather","stock",
                                          "crypto","news"]):
                return cleaned, (
                    "I'm a medical assistant — I can only help with health questions. "
                    "Try asking about symptoms, medications, or general wellness."
                )
            return cleaned, (
                "👋 Hello! I'm your medical assistant. Ask me anything about "
                "symptoms, diseases, medications, or general health advice."
            )

    return cleaned, None


# ─────────────────────────────────────────────────────────────────────────────
# CROSS-ENCODER RERANKER
# ─────────────────────────────────────────────────────────────────────────────
class CrossEncoderReranker:
    def __init__(self, model_name="cross-encoder/ms-marco-MiniLM-L-6-v2", top_n=3):
        try:
            from sentence_transformers import CrossEncoder
            self.model = CrossEncoder(model_name)
            self.top_n = top_n
            self.available = True
        except Exception as e:
            print(f"⚠️ CrossEncoder not available: {e}")
            self.available = False
            self.top_n = top_n

    def rerank(self, query: str, docs: list) -> list:
        if not docs:
            return docs
        if not self.available:
            # Fallback: return top_n docs as-is
            return docs[:self.top_n]
        try:
            pairs  = [(query, doc.page_content) for doc in docs]
            scores = self.model.predict(pairs)
            scored = sorted(zip(scores, docs), key=lambda x: x[0], reverse=True)
            return [doc for _, doc in scored[:self.top_n]]
        except Exception:
            return docs[:self.top_n]


# ─────────────────────────────────────────────────────────────────────────────
# HYBRID RETRIEVER — FAISS + BM25 combined manually
# Avoids EnsembleRetriever import path issues across langchain versions
# ─────────────────────────────────────────────────────────────────────────────
class HybridRetriever:
    """
    Combines FAISS dense retrieval + BM25 sparse retrieval.
    Uses Reciprocal Rank Fusion (RRF) to merge results instead of
    EnsembleRetriever — works regardless of langchain version.
    """
    def __init__(self, dense_retriever, bm25_retriever=None,
                 dense_k=6, bm25_k=6, rrf_k=60):
        self.dense     = dense_retriever
        self.bm25      = bm25_retriever
        self.dense_k   = dense_k
        self.bm25_k    = bm25_k
        self.rrf_k     = rrf_k   # RRF constant (60 is standard)

    def invoke(self, query: str) -> list:
        # Dense results
        try:
            dense_docs = self.dense.invoke(query)
        except Exception:
            dense_docs = []

        if self.bm25 is None:
            return dense_docs

        # BM25 results
        try:
            bm25_docs = self.bm25.invoke(query)
        except Exception:
            bm25_docs = []

        # Reciprocal Rank Fusion
        scores = {}
        def doc_id(doc):
            return doc.page_content[:120]   # use content prefix as ID

        for rank, doc in enumerate(dense_docs):
            did = doc_id(doc)
            scores[did] = scores.get(did, 0) + 1.0 / (self.rrf_k + rank + 1)

        for rank, doc in enumerate(bm25_docs):
            did = doc_id(doc)
            scores[did] = scores.get(did, 0) + 1.0 / (self.rrf_k + rank + 1)

        # Collect all unique docs, sort by fused score
        all_docs = {doc_id(d): d for d in dense_docs + bm25_docs}
        ranked   = sorted(all_docs.keys(),
                          key=lambda x: scores.get(x, 0), reverse=True)
        return [all_docs[did] for did in ranked]


# ─────────────────────────────────────────────────────────────────────────────
# MAIN FACTORY
# ─────────────────────────────────────────────────────────────────────────────
def create_rag(api_key: str):
    """
    4-stage RAG pipeline:
      Stage 1 — Query filter      : blocks non-medical / harmful input
      Stage 2 — Hybrid retrieval  : FAISS (dense) + BM25 (sparse) via RRF
      Stage 3 — Reranking         : cross-encoder ms-marco MiniLM
      Stage 4 — Generation        : Gemini 2.5 Flash
    """

    # ── Embeddings ────────────────────────────────────────────────────────
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        cache_folder="D:/hf_cache"
    )

    # ── Dense retriever (FAISS) ───────────────────────────────────────────
    vectorstore    = FAISS.load_local(
        "vector_db", embeddings, allow_dangerous_deserialization=True
    )
    dense_retriever = vectorstore.as_retriever(search_kwargs={"k": 6})

    # ── Sparse retriever (BM25) ───────────────────────────────────────────
    bm25_retriever = None
    bm25_path = "vector_db/bm25_docs.pkl"
    if os.path.exists(bm25_path):
        try:
            with open(bm25_path, "rb") as f:
                split_docs = pickle.load(f)

            # Try langchain_community first, then langchain.retrievers
            try:
                from langchain_community.retrievers import BM25Retriever
            except ImportError:
                from langchain_community.retrievers import BM25Retriever

            bm25_retriever   = BM25Retriever.from_documents(split_docs)
            bm25_retriever.k = 6
            print("✅ BM25 retriever loaded")
        except Exception as e:
            print(f"⚠️ BM25 load failed: {e} — using FAISS only")
            bm25_retriever = None
    else:
        print("⚠️ BM25 index not found. Run build_rag_db.py for hybrid search.")

    # ── Hybrid retriever (RRF fusion — no EnsembleRetriever needed) ───────
    hybrid_retriever = HybridRetriever(
        dense_retriever = dense_retriever,
        bm25_retriever  = bm25_retriever,
        dense_k=6, bm25_k=6
    )

    # ── Cross-encoder reranker ────────────────────────────────────────────
    reranker = CrossEncoderReranker(
        model_name="cross-encoder/ms-marco-MiniLM-L-6-v2",
        top_n=3
    )

    # ── LLM ──────────────────────────────────────────────────────────────
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=api_key or API_KEY
    )

    # ── Prompt ────────────────────────────────────────────────────────────
    prompt = ChatPromptTemplate.from_template("""
You are a knowledgeable and empathetic medical assistant.

Use the provided context to answer the question accurately.
If the context does not fully cover the question, supplement with your medical knowledge.
Always be clear, concise, and patient-friendly.

Context:
{context}

Question:
{question}

Answer:
""")

    # ── RAG callable ──────────────────────────────────────────────────────
    def rag_with_score(question: str) -> dict:

        # Stage 1: Query filter
        cleaned_query, block_msg = filter_query(question)
        if block_msg:
            return {"answer": block_msg, "context": "", "blocked": True}

        # Stage 2: Hybrid retrieval (FAISS + BM25 via RRF)
        candidate_docs = hybrid_retriever.invoke(cleaned_query)

        # Stage 3: Cross-encoder reranking
        reranked_docs = reranker.rerank(cleaned_query, candidate_docs)

        # Stage 4: Generate answer
        context      = "\n\n".join(doc.page_content for doc in reranked_docs)
        final_prompt = prompt.format(context=context, question=cleaned_query)
        response     = llm.invoke(final_prompt)

        return {
            "answer":         response.content,
            "context":        context,
            "blocked":        False,
            "num_candidates": len(candidate_docs),
            "num_reranked":   len(reranked_docs),
        }

    return rag_with_score