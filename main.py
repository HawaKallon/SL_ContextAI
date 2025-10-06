"""
Sierra Leonean Context AI - Main Application
Multi-domain RAG system with context-aware responses
"""

import os
from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

load_dotenv()

# Sierra Leone Context Prompt
SIERRA_LEONE_CONTEXT = """
You are an AI assistant with deep expertise in Sierra Leone. You understand:

- **History**: The civil war (1991-2002), independence (1961), colonial period, and post-war recovery
- **Ethnic Diversity**: Temne, Mende, Limba, Krio, and other ethnic groups with their unique cultures
- **Languages**: English (official), Krio (lingua franca), and various tribal languages
- **Politics**: Multi-party democracy, paramount chiefs, chiefdom governance, current political landscape
- **Economy**: Mining (diamonds, iron ore), agriculture, fishing, challenges and opportunities
- **Culture**: Traditional practices, music, food, religious diversity (Islam, Christianity, traditional beliefs)
- **Geography**: Provinces, major cities (Freetown, Bo, Kenema, Makeni), regions
- **Current Issues**: Development challenges, education, healthcare, infrastructure

Always provide answers that are:
1. **Culturally sensitive** and contextually accurate for Sierra Leone
2. **Aware** of Sierra Leone's unique history and circumstances
3. **Practical** and relevant to Sierra Leoneans' daily lives
4. **Respectful** of local customs, traditions, and perspectives
5. **Simple** - explain in everyday language, not academic jargon
"""


class SierraLeoneAI:
    def __init__(self):
        self.categories = ['history', 'culture', 'politics', 'economy', 'general']
        self.vectorstores = {}
        self.embeddings = self.create_embeddings()
        self.llm = self.initialize_llm()
        self.load_vectorstores()

    def create_embeddings(self):
        """Create embedding model"""
        return HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-V2",
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )

    def initialize_llm(self):
        """Initialize Hugging Face LLM"""
        base_llm = HuggingFaceEndpoint(
            repo_id="mistralai/Mixtral-8x7B-Instruct-v0.1",
            huggingfacehub_api_token=os.getenv("HUGGINGFACEHUB_API_TOKEN"),
            temperature=0.2,
            max_new_tokens=512,
        )
        return ChatHuggingFace(llm=base_llm)

    def load_vectorstores(self):
        """Load all category vector stores"""
        print("🔧 Loading knowledge bases...")

        for category in self.categories:
            path = f"vectorstores/{category}_faiss"
            if os.path.exists(path):
                self.vectorstores[category] = FAISS.load_local(
                    path,
                    self.embeddings,
                    allow_dangerous_deserialization=True
                )
                print(f"  ✅ Loaded {category}")
            else:
                print(f"  ⚠️  {category} not found")

        if not self.vectorstores:
            print("\n❌ No vector stores found!")
            print("Please run: python data_loading.py")
            exit(1)

    def classify_question(self, question):
        """Simple keyword-based classification"""
        question_lower = question.lower()

        keywords = {
            'history': ['war', 'civil war', 'independence', 'colonial', 'past', 'history',
                        'british', 'revolution', 'ruf', 'special court'],
            'culture': ['tradition', 'custom', 'language', 'krio', 'ethnic', 'tribe',
                        'mende', 'temne', 'limba', 'music', 'food', 'religion', 'festival'],
            'politics': ['government', 'president', 'election', 'parliament', 'party',
                         'apc', 'slpp', 'chief', 'vote', 'democracy', 'political'],
            'economy': ['business', 'trade', 'economy', 'jobs', 'market', 'mining',
                        'diamond', 'agriculture', 'fishing', 'money', 'leone', 'bank'],
        }

        scores = {}
        for category, kws in keywords.items():
            score = sum(1 for kw in kws if kw in question_lower)
            scores[category] = score

        # Get category with highest score
        best_category = max(scores, key=scores.get)

        # If no strong match, use general
        if scores[best_category] == 0:
            return 'general'

        return best_category

    def search_all_categories(self, question, k=3):
        """Search across all categories"""
        all_results = []

        for category, vectorstore in self.vectorstores.items():
            try:
                results = vectorstore.similarity_search(question, k=k)
                for doc in results:
                    doc.metadata['retrieved_from'] = category
                all_results.extend(results)
            except:
                continue

        # Sort by relevance (basic - just take first k*len(categories))
        return all_results[:k * 3]  # Return top 9 results across all categories

    def create_rag_chain(self, primary_category):
        """Create RAG chain with context-aware prompt"""

        prompt_template = f"""
{SIERRA_LEONE_CONTEXT}

You are answering a question about Sierra Leone, specifically related to {primary_category}.

Use the following information from Sierra Leone sources:

{{context}}

Question: {{question}}

Instructions:
- Provide a nuanced answer that demonstrates deep understanding of Sierra Leone
- Explain in simple, everyday language that anyone can understand
- Break down any complex terms in parentheses
- Use specific examples from Sierra Leone when helpful
- If mentioning historical events, provide brief context
- If you're unsure or the sources don't fully answer, say so honestly

Answer:
"""

        prompt = PromptTemplate(
            template=prompt_template,
            input_variables=["context", "question"]
        )

        # Use primary category vectorstore
        if primary_category in self.vectorstores:
            retriever = self.vectorstores[primary_category].as_retriever(
                search_type="similarity",
                search_kwargs={"k": 3}
            )
        else:
            # Fallback to general
            retriever = self.vectorstores['general'].as_retriever(
                search_type="similarity",
                search_kwargs={"k": 3}
            )

        qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=retriever,
            chain_type_kwargs={"prompt": prompt},
            return_source_documents=True
        )

        return qa_chain

    def query(self, question):
        """Main query function"""

        # Classify question
        category = self.classify_question(question)

        print(f"\n🔍 Detected topic: {category.upper()}")
        print(f"🔍 Searching Sierra Leone knowledge base...")

        # Create and run chain
        chain = self.create_rag_chain(category)
        result = chain({"query": question})

        return result, category


def format_source_display(doc, index):
    """Format source documents"""
    metadata = doc.metadata

    source = metadata.get('source', 'Unknown')
    category = metadata.get('category', 'Unknown')
    retrieved_from = metadata.get('retrieved_from', category)

    # Clean up source path
    if 'data/' in source:
        source = source.split('data/')[-1]
    source = source.replace('.txt', '')

    print(f"\n📄 Source {index} ({retrieved_from}):")
    print(f"   Document: {source}")
    print(f"   Preview: {doc.page_content[:250].replace(chr(10), ' ')}...")
    print()


def show_welcome_message():
    """Display welcome message"""
    print("\n" + "=" * 80)
    print("🇸🇱 SIERRA LEONEAN CONTEXT AI")
    print("=" * 80)
    print("\nWelcome! I'm an AI assistant with deep knowledge of Sierra Leone.")
    print("I can help you understand our history, culture, politics, and more.\n")
    print("Example questions you can ask:")
    print("  • Why did the civil war start and how did it end?")
    print("  • What is the role of paramount chiefs in Sierra Leone?")
    print("  • How does the Krio language work?")
    print("  • What are the main ethnic groups and their cultures?")
    print("  • What are Sierra Leone's biggest economic challenges?")
    print("  • Tell me about Sierra Leone's independence")
    print("  • What is life like in Freetown?")
    print("\n💡 Type 'exit', 'quit', or 'q' anytime to leave.\n")
    print("=" * 80)


def main():
    show_welcome_message()

    # Initialize AI
    print("\n🚀 Starting Sierra Leonean Context AI...")
    ai = SierraLeoneAI()
    print("✅ Ready!\n")

    while True:
        question = input("\n💬 Ask your question (or 'exit' to quit): ").strip()

        if not question:
            print("⚠️  Please enter a question.")
            continue

        if question.lower() in ["exit", "quit", "q"]:
            print("\n👋 Thank you for using Sierra Leonean Context AI. Goodbye!")
            break

        print("\n" + "=" * 80)

        try:
            result, category = ai.query(question)

            print(f"\n❓ Your Question:")
            print(f"   {question}")
            print(f"\n💡 Answer:")
            print(f"   {result['result']}")

            # Show sources
            if result.get('source_documents'):
                print(f"\n📚 This answer is based on {len(result['source_documents'])} source(s):")
                print("-" * 80)

                for i, doc in enumerate(result['source_documents'], 1):
                    format_source_display(doc, i)
            else:
                print("\n⚠️  No specific sources found for this answer.")

        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            print("Please try rephrasing your question.")


if __name__ == "__main__":
    main()