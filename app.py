import streamlit as st
from streamlit_feedback import streamlit_feedback
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.tracers.context import collect_runs
from langsmith import Client
from streamlit_star_rating import st_star_rating
import itertools
from LLM import getChain
from RAG import getRequirements
from streamlit_pdf_viewer import pdf_viewer
import time
from threading import Thread
import toml
import os
os.environ['LANGCHAIN_TRACING_V2']=st.secrets['langchain']['LANGCHAIN_TRACING_V2']
os.environ['LANGCHAIN_API_KEY']=st.secrets['langchain']['api_key']

def sayhi():
    """
    Initialize the chain with the selected model name.
    """
    st.session_state.chain = getChain(st.session_state.model_name)
    print(st.session_state.model_name)
client = Client()
st.session_state.file_path = st.sidebar.file_uploader('Please upload the requirements in PDF format', type='pdf')

if st.session_state.file_path is not None and st.session_state.file_path is not 'False':
    print('hi')
    with open('Requirements.pdf', 'wb') as f:
        f.write(st.session_state.file_path.read())
        st.success('File uploaded successfully')
    with st.sidebar:
        st.sidebar.subheader('Requirements')
        pdf_viewer(input='Requirements.pdf',
                   width=1200)
    st.session_state.file_path='False'
    st.session_state.context = getRequirements()
    st.session_state.chain = getChain()
    
        
if 'context' not in st.session_state:
    st.session_state.context = getRequirements()
if 'chain' not in st.session_state:
    st.session_state.chain = getChain()
if 'history' not in st.session_state:
    st.session_state.history = []
if 'run_id' not in st.session_state:
    st.session_state.run_id = None
if 'form' not in st.session_state:
    st.session_state.form = None
if 'isfirst' not in st.session_state:
    st.session_state.isfirst = False

# Sidebar content

# Initial chat message
if st.session_state.file_path is "False":
    with st.chat_message('ai'):
        st.write('Hello, I’m interested in discussing a potential purchase. Can we chat? \n\nPlease refer to the requirements listed in the sidebar.')

# Retrieve the chain, history, and context from session state
chain = st.session_state.chain
history = st.session_state.history
context = st.session_state.context

def show_run():
    """
    Display the list of root runs from Langsmith.
    """
    root_runs = client.list_runs(project_name="default", is_root=True)
    st.write(root_runs)

def get_last_message():
    """
    Get the content of the last message in the history.
    """
    if len(history) > 0:
        return history[-1].content

def show_messages():
    """
    Display messages from history in the chat.
    """
    for message in history:
        if isinstance(message, HumanMessage):
            with st.chat_message('human'):
                st.write(message.content)
        else:
            with st.chat_message('ai'):
                st.write(message.content)

def disable_chat():
    """
    Disable the chat input field.
    """
    st.markdown(
        """
        <style>
        .stChatInput {
            pointer-events: none;
            opacity: 0.5;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

def enable_chat():
    """
    Enable the chat input field.
    """
    st.markdown(
        """
        <style>
        .stChatInput {
            pointer-events: auto;
            opacity: 1;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

def show_form():
    """
    Show the feedback form.
    """
    st.session_state.form = True

def hide_form():
    """
    Hide the feedback form.
    """
    st.markdown(
        """
        <style>
        .my_form {
            display: none;
            opacity: 1;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    st.session_state.form = False

# Main chat loop
if st.session_state.file_path is 'False':
    with collect_runs() as cb:
        with st.spinner("Processing..."):
            if question := st.chat_input('Start chatting'):
                hide_form()
                disable_chat()
                with st.chat_message('user'):
                    st.write(question)
                    history.append(HumanMessage(question))
                with st.chat_message('ai'):
                    res = chain.stream({'input': question, 'chat_history': history, 'context': context})
                    res1, res2 = itertools.tee(res)
                    st.write_stream(res2)
                    ans = ''
                    for v in res1:
                        ans += v.content
                    history.append(AIMessage(ans))
                enable_chat()
                st.session_state.run_id = cb.traced_runs[0].id
                st.session_state.form = False
elif st.session_state.file_path is None :
    st.warning('please upload the Requirements Docs in PDF format')

# Handle feedback form display and submission
run_id = st.session_state.run_id
if st.session_state.form is not None:
    if not st.session_state.form:
        st.button('Feedback', on_click=show_form, type='primary')
    else:
        st.button('Hide Form', on_click=hide_form)
        with st.form(key="my_form"):
            col1, col2 = st.columns([5, 3])
            st.session_state.form = True
            with col1:
                score = st_star_rating("Please rate your experience", maxValue=5, defaultValue=3, key="rating")
            with col2:
                comment = st.text_area("Type Comment")
            submitted = st.form_submit_button("Submit", type='primary')
            if submitted:
                with st.spinner('Submitting feedback...'):
                    client.create_feedback(
                        run_id=run_id,
                        score=score,
                        comment=comment,
                        key=str(run_id),
                    )
                    st.success('Thank you for your feedback.')

# Uncomment the line below to see chat history (debugging purpose)
# st.button('see chat', on_click=show_run)
