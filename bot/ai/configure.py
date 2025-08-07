from general import settings


def configure_ai():
    if settings.ai.use:
        from .client import RAGSystem

        ai = RAGSystem()
        ai.create_faiss_if_not_exist()
        ai.load_vectorstore()
        return ai
    return None
