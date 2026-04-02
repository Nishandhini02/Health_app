import os

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings


def build_vector_db():

    pdf_folder = "pdf_data"

    docs = []

    for file in os.listdir(pdf_folder):

        if file.endswith(".pdf"):

            loader = PyPDFLoader(
                os.path.join(pdf_folder, file)
            )

            pages = loader.load()
            docs.extend(pages)

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=400,
        chunk_overlap=80
    )

    split_docs = splitter.split_documents(docs)

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    vectorstore = FAISS.from_documents(
        split_docs,
        embeddings
    )

    # SAVE VECTOR DATABASE
    vectorstore.save_local("vector_db")

    print("RAG Vector Database Created Successfully")


if __name__ == "__main__":

    build_vector_db()


