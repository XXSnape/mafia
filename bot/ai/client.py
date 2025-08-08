import asyncio
import os

import torch
from general import settings
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import (
    UnstructuredMarkdownLoader,
)
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI
from loguru import logger


class RAGSystem:
    def __init__(self):
        logger.info(f"Инициализация эмбеддингов")
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
            model_kwargs={
                "device": (
                    "cuda" if torch.cuda.is_available() else "cpu"
                ),
            },
            encode_kwargs={"normalize_embeddings": True},
        )

        logger.info("Инициализация языковой модели...")
        self.llm = ChatOpenAI(
            api_key=settings.ai.deepseek_api_key,
            base_url=settings.ai.base_url,
            model=settings.ai.deepseek_model_name,
        )
        self.vectorstore = None
        self.is_loaded = False
        logger.info(
            "Настройка разделителя документов (размер чанка: {}, перекрытие: {})...",
            settings.ai.max_chunk_size,
            settings.ai.chunk_overlap,
        )
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.ai.max_chunk_size,
            chunk_overlap=settings.ai.chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""],
        )

        self.prompt_template = """Ты — помощник бота для игры в "Мафию" онлайн. Отвечаешь по делу без лишних вступлений.

    Правила:
    1. Сразу переходи к сути, БЕЗ ФРАЗ типа "На основе контекста"
    2. Используй только факты. Если точных данных нет — отвечай общими фразами о Мафии, но не придумывай конкретику
    3. ИСПОЛЬЗУЙ ОБЫЧНЫЙ ТЕКСТ БЕЗ КАКОГО-ЛИБО ФОРМАТИРОВАНИЯ! Используй символы "«»" вместо "**", не выделяй цитаты!!!
    4. Говори от первого лица множественного числа: "Мы предоставляем", "У нас есть"
    5. На приветствия отвечай доброжелательно, на негатив — с легким юмором
    6. Можешь при ответах использовать общую информацию из открытых источников по Мафии, но опирайся на контекст
    7. Если пользователь спрашивает о ценах, планах или технических характеристиках — давай конкретные ответы из контекста
    8. При технических вопросах предлагай практические решения

    Будь краток, информативен и полезен.

    Контекст из документации:
    {context}

    Вопрос пользователя:
    {question}

    """

        self.prompt = PromptTemplate(
            template=self.prompt_template,
            input_variables=["context", "question"],
        )

    @classmethod
    def _load_document(cls, file_path: str) -> list[Document]:
        """Загрузка документа из файла"""
        logger.info("Загрузка документа: {}", file_path)
        loader = UnstructuredMarkdownLoader(file_path)

        try:
            documents = loader.load()
            logger.success(
                "Загружено {} страниц/частей из {}",
                len(documents),
                file_path,
            )
            return documents
        except Exception:
            logger.exception(
                "Ошибка при загрузке документа {}", file_path
            )
            return []

    def _process_documents(self, documents: list[Document]) -> None:
        """Обработка и создание векторного хранилища из документов"""
        if not documents:
            logger.warning("Нет документов для обработки!")
            return

        logger.info("Разделение документов на чанки...")

        chunks = self.text_splitter.split_documents(documents)
        logger.success("Создано {} чанков", len(chunks))

        logger.info("Создание векторного хранилища...")

        self.vectorstore = FAISS.from_documents(
            chunks, self.embeddings
        )
        logger.success("Векторное хранилище создано")
        self.is_loaded = True

    def _save_vectorstore(
        self,
    ) -> None:
        """Сохранение векторного хранилища на диск"""
        logger.info("Сохраняем хранилище...")
        settings.ai.faiss_path.mkdir(exist_ok=True)
        self.vectorstore.save_local(settings.ai.faiss_path)
        logger.success(
            "Векторное хранилище сохранено в {}",
            settings.ai.faiss_path,
        )

    def create_faiss_if_not_exist(self):
        path = settings.ai.faiss_path
        if path.exists() and len(os.listdir(path)) > 0:
            logger.info(
                "Векторная база {} уже существует и не пуста", path
            )
            return
        path.mkdir(exist_ok=True)
        docs = self._load_document(settings.ai.md_path)
        self._process_documents(docs)
        self._save_vectorstore()

    def load_vectorstore(
        self,
    ) -> None:
        """Загрузка векторного хранилища с диска"""
        logger.info("Начинаем выгрузку хранилища...")
        if not settings.ai.faiss_path.exists():
            logger.warning(
                "Директория {} не существует!",
                settings.ai.faiss_path,
            )
            return

        self.vectorstore = FAISS.load_local(
            settings.ai.faiss_path,
            self.embeddings,
            allow_dangerous_deserialization=True,
        )
        logger.success(
            "Векторное хранилище выгружено из {}",
            settings.ai.faiss_path,
        )
        self.is_loaded = True

    async def query(self, question: str) -> str:
        """Запрос к системе"""
        if not self.is_loaded:
            logger.warning(
                "Попытка сделать запрос без загруженной базы"
            )
            return settings.ai.unavailable_message

        try:
            retriever = self.vectorstore.as_retriever(
                search_kwargs={"k": 10}
            )
            qa_chain = RetrievalQA.from_chain_type(
                llm=self.llm,
                chain_type="stuff",
                retriever=retriever,
                return_source_documents=True,
                chain_type_kwargs={"prompt": self.prompt},
            )
            result = await qa_chain.ainvoke({"query": question})
            answer = result["result"]
            return answer

        except Exception:
            logger.exception("Ошибка при выполнении запроса к AI")
            return settings.ai.unavailable_message


async def main():
    r = RAGSystem()
    r.create_faiss_if_not_exist()
    r.load_vectorstore()
    result = await r.query("Что за ставки?")
    print("result", result)


if __name__ == "__main__":
    asyncio.run(main())
