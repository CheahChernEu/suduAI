from langchain import PromptTemplate
from langchain.llms import CTransformers
from langchain.chains import RetrievalQA
from langchain.llms import LlamaCpp
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

from config import *
from vectordb import VectorDB
from pdfloader import PDFLoader
from ingest import Ingest
# from ensemble_retriever import retriever_creation

class SuduBotCreator:

    def __init__(self, db_path: str, collection_name: str, folder_path: str):
        # Initialize PDFLoader, Ingest, and VectorDB
        self.pdf_loader = PDFLoader()
        self.vector_db = VectorDB(db_path=db_path, collection_name=collection_name)
        self.ingest = Ingest(db_path=db_path, collection_name=collection_name)
        self.load_documents = self.ingest.run(folder_path)

        # Other initializations...
        self.callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])
        self.prompt_temp = PROMPT_TEMPLATE
        self.input_variables = INP_VARS
        self.chain_type = CHAIN_TYPE
        self.temperature = TEMPERATURE
        self.gpu_layers = GPU_LAYERS
        self.model_path = MODEL_PATH
        self.temperature = TEMPERATURE
        self.max_tokens = MAX_TOKENS
        self.n_ctx = N_CTX
        self.top_p = TOP_P
        self.verbose = VERBOSE


    def load_retriever(self):
        # Get retriever from VectorDB
        return self.vector_db.get_retriever()
    
    def create_custom_prompt(self):
        custom_prompt_temp = PromptTemplate(template=self.prompt_temp,
                            input_variables=self.input_variables)
        return custom_prompt_temp
    
    def load_llm(self):
        # llm = CTransformers(
        #         model = self.model_ckpt,
        #         model_type=self.model_type,
        #         max_new_tokens = self.max_new_tokens,
        #         temperature = self.temperature,
        #         gpu_layers= self.gpu_layers
        #     )
        # return llm

        llm = LlamaCpp(
            model_path=self.model_path,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            n_ctx=self.n_ctx,
            top_p=self.top_p,
            callback_manager=self.callback_manager,
            verbose=self.verbose, 
            n_gpu_layers=self.gpu_layers 
        )

        return llm


    def create_bot(self, custom_prompt, retriever, llm):
        retrieval_qa_chain = RetrievalQA.from_chain_type(
                                llm=llm,
                                chain_type=self.chain_type,
                                retriever= retriever,
                                return_source_documents=True,
                                chain_type_kwargs={"prompt": custom_prompt}
                            )
        return retrieval_qa_chain
    
    def create_sudu_bot(self):
        self.custom_prompt = self.create_custom_prompt()
        self.retriever = self.load_retriever()
        self.llm = self.load_llm()
        self.bot = self.create_bot(self.custom_prompt, self.retriever, self.llm)


    def infer_sudu_bot(self, prompt):
        model_out = self.bot(prompt)
        answer = model_out['result']
        source_documents = model_out['source_documents']
        metadata = [doc.metadata for doc in source_documents]

        # Create a structured string for the output
        output = f"{answer}"
        for i, meta in enumerate(metadata):
            output += f"\nSource Document {i+1}:\n"
            output += f"Page: {meta['page']}\n"
            output += f"Source: {meta['source']}\n"

        return output

if __name__ == "__main__":
    # Initialize SuduBotCreator with the parsed arguments
    sudu_bot_creator = SuduBotCreator(db_path=DB_PATH, collection_name=COLLECTION_NAME, folder_path=FOLDER_PATH)

    # Create the bot
    sudu_bot_creator.create_sudu_bot()

    # Now you can call the infer_sudu_bot method
    output = sudu_bot_creator.infer_sudu_bot({'query': 'Who are the investors press person?'})
    print(output)
