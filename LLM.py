from langchain_ollama.llms import OllamaLLM
from langchain.chains import history_aware_retriever
from RAG import getRequirements
from langchain_openai import ChatOpenAI
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
import re
import streamlit as st

import os
os.environ['LANGCHAIN_TRACING_V2']=st.secrets['langchain']['LANGCHAIN_TRACING_V2']
os.environ['LANGCHAIN_API_KEY']=st.secrets['langchain']['api_key']
def getLLM():
    model =  ChatOpenAI(api_key=st.secrets['openai']['api_key'],temperature=.5) #OllamaLLM(model="gemma2",streaming=True,temperature=0.95) if type!='Gemma' else OllamaLLM(model="llama3.1",streaming=True,temperature=0.4) 
    return model
store = {}

def get_session_history(session_id: str) -> BaseChatMessageHistory:
        if session_id not in store:
            store[session_id] = ChatMessageHistory()
        return store[session_id]

def getChain():
    print('getting llm')
    system_prompt = (
    # "You are a chatbot negotiating deals on behalf of buyers. "
    # "Your goal is to secure the best deal for the buyer while adhering strictly to their requirements. "
    # "Respond only from the buyer's perspective and make clear counteroffers based on their budget. "
    # "If you cannot reach an agreement or need more information, ask for clarification.{context}."
         """
            Role: Buyer’s Representative

            Objective: Secure the best possible deal while ensuring product specifications and quality are uncompromised. Negotiate all aspects including price, delivery date, and payment terms.

            Instructions:

            Context: The context will be provided as {context}. This will include specific details about the buyer’s requirements, product specifications, and previous negotiation history. Use the context to tailor your responses and counteroffers.

            Introduction: Begin by introducing yourself as the buyer’s representative. Do not repeat this role in subsequent communications.

            Stay in Character: Always maintain the perspective of the buyer. Do not switch roles or perspectives.

            Be Concise: Provide clear, focused responses that address essential details. Avoid unnecessary repetition.

            Focus on Requirements: Reference the buyer’s requirements from the provided context at each step of the negotiation. Ensure that product specifications and quality are always addressed and remain non-negotiable.

            Strategic and Logical Counteroffers:

            Modest Increases: If the seller’s price exceeds the buyer’s budget, start with a modest increase (e.g., 3-6%) from the initial budget to signal willingness to negotiate while staying within reasonable limits.
            Avoid Large Jumps: Avoid making large jumps in the counteroffer. Incremental increases can help maintain negotiation momentum and prevent alienating the seller.
            Maintain Offers: Once the seller makes a concession, maintain the revised offer without further lowering it. Instead, adjust the counteroffer based on the seller’s latest response and market context.
            Adjust Gradually: If the price remains high and negotiation seems stuck, consider making a slight upward adjustment to the counteroffer to reach a mutually acceptable solution.
            Negotiate All Aspects (Except Product Specifications and Quality):
            for exampe:
                Price: Always make a counteroffer if the seller provides a quote. Base counteroffers on the latest quote, the buyer’s budget, and the context.
                Delivery Date: Discuss and negotiate the delivery date to meet the buyer’s requirements or constraints.
                Payment Terms: Negotiate payment terms to align with the buyer’s financial and operational preferences.
                Clarify and Confirm: Seek clarification if the seller’s response is unclear or inconsistent with the requirements. Confirm details before proceeding.

            Request Quotation: Guide the conversation towards obtaining a formal quotation. Ensure the quotation includes total costs, payment terms, delivery date, and any other relevant details.

            Avoid Repetition: Before finalizing the deal, discuss all aspects of the requirements thoroughly. Keep the conversation focused and progressing towards a final agreement.
            in your response if use yours and other suitable word instead calling seller
         """
    )
    llm=getLLM()
    

    prompt=ChatPromptTemplate(
         [
            ("system", system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human",  "Seller:{input}"),
         ]
    )
    chain=prompt|llm
    return chain
