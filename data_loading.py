import os
import sys
import io
import glob

# Suppress warnings
sys.stderr = io.StringIO()
os.environ["USER_AGENT"] = "Mozilla/5.0 (compatible; SierraLeoneAI/1.0)"
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import TextLoader
import warnings
import logging

warnings.filterwarnings("ignore", category=UserWarning)
logging.getLogger("transformers").setLevel(logging.ERROR)


class SierraLeoneDataLoader:
    def __init__(self, base_data_dir='data'):
        self.base_data_dir = base_data_dir
        self.categories = ['history', 'culture', 'politics', 'economy', 'general']
        self.embeddings = self.create_embeddings()
        self.vectorstores = {}

    def create_embeddings(self):
        """Create embedding model"""
        print("🔧 Loading embedding model...")
        return HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-V2",
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )

    def load_documents_from_category(self, category):
        """Load all text documents from a category folder"""
        category_path = os.path.join(self.base_data_dir, category)

        if not os.path.exists(category_path):
            print(f"⚠️  Category folder not found: {category_path}")
            return []

        # Get all .txt files (skip JSON metadata files)
        txt_files = glob.glob(os.path.join(category_path, "*.txt"))

        if not txt_files:
            print(f"⚠️  No text files found in {category}/")
            return []

        all_docs = []
        for file_path in txt_files:
            try:
                loader = TextLoader(file_path, encoding='utf-8')
                docs = loader.load()
                # Add category metadata
                for doc in docs:
                    doc.metadata['category'] = category
                all_docs.extend(docs)
            except Exception as e:
                print(f"  ❌ Error loading {file_path}: {str(e)}")

        return all_docs

    def chunk_documents(self, documents, chunk_size=1500, chunk_overlap=300):
        """Split documents into chunks"""
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        return text_splitter.split_documents(documents)

    def create_vectorstore_for_category(self, category):
        """Create FAISS vector store for a specific category"""
        print(f"\n📚 Processing {category.upper()} category...")

        # Load documents
        documents = self.load_documents_from_category(category)

        if not documents:
            print(f"  ⚠️  No documents found, skipping {category}")
            return None

        print(f"  ✅ Loaded {len(documents)} documents")

        # Chunk documents
        chunks = self.chunk_documents(documents)
        print(f"  ✅ Created {len(chunks)} chunks")

        # Create vector store
        print(f"  🔧 Creating vector store...")
        vectorstore = FAISS.from_documents(chunks, self.embeddings)

        # Save vector store
        save_path = f"vectorstores/{category}_faiss"
        os.makedirs("vectorstores", exist_ok=True)
        vectorstore.save_local(save_path)
        print(f"  💾 Saved to {save_path}/")

        return vectorstore

    def load_all_categories(self):
        """Load and process all categories"""
        print("=" * 80)
        print("🇸🇱 SIERRA LEONE AI - DATA LOADING")
        print("=" * 80)

        total_chunks = 0

        for category in self.categories:
            vectorstore = self.create_vectorstore_for_category(category)
            if vectorstore:
                self.vectorstores[category] = vectorstore

        print("\n" + "=" * 80)
        print("✅ DATA LOADING COMPLETE!")
        print("=" * 80)
        print(f"\n📊 Summary:")
        print(f"   Categories processed: {len(self.vectorstores)}")
        for category in self.vectorstores:
            print(f"   - {category}: ✅")
        print(f"\n🚀 Next step: Run 'python main.py' to start the AI assistant")
        print("=" * 80)

        return self.vectorstores


def main():
    loader = SierraLeoneDataLoader()
    vectorstores = loader.load_all_categories()

    if not vectorstores:
        print("\n❌ No vector stores created. Please run data collection first:")
        print("   python data_collection.py")


if __name__ == "__main__":
    main()