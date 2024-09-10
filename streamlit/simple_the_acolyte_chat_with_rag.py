from textwrap import dedent
from typing import List

import streamlit as st
from snowflake.core import Root
from snowflake.snowpark.context import get_active_session

MODELS = [
    "llama3.1-70b",
    "mistral-large2",
    "llama3.1-8b",
    "mixtral-8x7b",
]
SERVICE_DB = "ACOLYTE_DB"
SERVICE_SCHEMA = "SERVICES"
SERVICE_DB_SCHEMA = f"{SERVICE_DB}.{SERVICE_SCHEMA}"


def init_messages():
    """
    Initialize the session state for chat messages.
    If the session state indicates that the conversation
    should be cleared or if the "messages" key is not
    in the session state, initialize it as an empty list.
    """
    if st.session_state.clear_conversation or "messages" not in st.session_state:
        st.session_state.messages = []


def init_service_metadata():
    """
    Initialize the session state for cortex search service metadata.
    Query the available cortex search services from the Snowflake session
    and store their names and search columns in the session state.
    """
    if "service_metadata" not in st.session_state:
        service_metadata = []

        for s in session.sql(
            f"SHOW CORTEX SEARCH SERVICES IN SCHEMA {SERVICE_DB_SCHEMA};"
        ).collect():
            svc_name = s["name"]
            svc_search_col = session.sql(
                f"DESC CORTEX SEARCH SERVICE {SERVICE_DB_SCHEMA}.{svc_name};"
            ).collect()[0]["search_column"]
            service_metadata.append({"name": svc_name, "search_column": svc_search_col})
        st.session_state.service_metadata = service_metadata


def init_config_options():
    """
    Initialize the configuration options in the Streamlit sidebar.
    Allow the user to select a cortex search service, clear the conversation,
    toggle debug mode, and toggle the use of chat history. Also provide advanced
    options to select a model, the number of context chunks,
    and the number of chat messages to use in the chat history.
    """
    st.sidebar.selectbox(
        "Select cortex search service:",
        [s["name"] for s in st.session_state.service_metadata],
        key="selected_cortex_search_service",
    )

    st.sidebar.button("Clear conversation", key="clear_conversation")
    st.sidebar.toggle("Debug", key="debug", value=True)
    st.sidebar.toggle("Use chat history", key="use_chat_history", value=True, disabled=False)

    with st.sidebar.expander("Advanced options"):
        st.markdown("### Select model:")
        st.selectbox("Generic model:", MODELS, key="model_name__generic", index=0)
        st.selectbox("Model for RAG:", MODELS, key="model_name__service", index=0, disabled=False)
        st.selectbox(
            "Aggregation of answers:",
            MODELS,
            key="model_name__aggregation",
            index=1,
            disabled=False,
        )
        st.selectbox("Summary of chat:", MODELS, key="model_name__summary", index=1, disabled=False)

        st.number_input(
            "Select number of context chunks",
            value=50,
            key="num_retrieved_chunks",
            min_value=1,
            max_value=200,
            disabled=False,
        )
        st.number_input(
            "Select number of messages to use in chat history",
            value=20,
            key="num_chat_messages",
            min_value=1,
            max_value=50,
            disabled=False,
        )

    st.sidebar.expander("Session State").write(st.session_state)


def query_cortex_search_service(query):
    """
    Query the selected cortex search service with the given
    query and retrieve context documents.
    Display the retrieved context documents in the sidebar if debug
    mode is enabled. Return the
    context documents as a string.

    Args:
        query (str): The query to search the cortex search service with.

    Returns:
        str: The concatenated string of context documents.
    """
    cortex_search_service = (
        root.databases[SERVICE_DB]
        .schemas[SERVICE_SCHEMA]
        .cortex_search_services[st.session_state.selected_cortex_search_service]
    )

    context_documents = cortex_search_service.search(
        query, columns=[], limit=st.session_state.num_retrieved_chunks
    )
    results = context_documents.results

    service_metadata = st.session_state.service_metadata
    search_col = [
        s["search_column"]
        for s in service_metadata
        if s["name"] == st.session_state.selected_cortex_search_service
    ][0]

    context_str = ""
    for i, r in enumerate(results):
        context_str += f"Context document {i+1}: {r[search_col]} \n" + "\n"

    if st.session_state.debug:
        st.sidebar.text_area("Context documents", context_str, height=500)

    return context_str


def get_chat_history() -> List[str]:
    """
    Retrieve the chat history from the session state limited
    to the number of messages specified by the user
    in the sidebar options.

    Returns:
        list: The list of chat messages from the session state.
    """
    start_index = max(0, len(st.session_state.messages) - st.session_state.num_chat_messages)
    return st.session_state.messages[start_index : len(st.session_state.messages) - 1]


def complete(model: str, prompt: str) -> str:
    """
    Generate a completion for the given prompt using the specified model.

    Args:
        model (str): The name of the model to use for completion.
        prompt (str): The prompt to generate a completion for.

    Returns:
        str: The generated completion.
    """
    return session.sql("SELECT snowflake.cortex.complete(?,?)", (model, prompt)).collect()[0][0]


def make_chat_history_summary(chat_history: str, question: str) -> str:
    """
    Generate a summary of the chat history combined with the current
    question to extend the query
    context. Use the language model to generate this summary.

    Args:
        chat_history (str): The chat history to include in the summary.
        question (str): The current user question to extend with the chat history.

    Returns:
        str: The generated summary of the chat history and question.
    """
    prompt = dedent(
        f"""
        Based on the chat history below and the question, generate
        a query that extend the question with the chat history provided.
        The query should be in natural language.
        Answer with only the query. Do not add any explanation.

        <chat_history>
        {chat_history}
        </chat_history>
        <question>
        {question}
        </question>
    """
    )

    summary = complete(st.session_state.model_name__summary, prompt)

    if st.session_state.debug:
        st.sidebar.text_area("Chat history summary", summary.replace("$", "\$"), height=150)

    return summary


def create_specialized_prompt(user_question: str) -> str:
    """
    Create a prompt for the language model by combining the user question
    with context retrieved from the cortex search service
    and chat history (if enabled). Format the prompt according to
    the expected input format of the model.

    Args:
        user_question (str): The user's question to generate a prompt for.

    Returns:
        str: The generated prompt for the language model.
    """
    if st.session_state.use_chat_history:
        chat_history = get_chat_history()
        if chat_history != []:
            question_summary = make_chat_history_summary(chat_history, user_question)
            prompt_context = query_cortex_search_service(question_summary)
        else:
            prompt_context = query_cortex_search_service(user_question)
    else:
        prompt_context = query_cortex_search_service(user_question)
        chat_history = ""

    prompt = dedent(
        f"""
        You are a helpful AI chat assistant with RAG capabilities.

        Use chat history provided between <chat_history>
        and </chat_history> tags.
        Question is between <question> and </question> tags.
        The context is between <context> and </context> tags.

        You will be working with data from wikipedia.
        The data contains plot of a series 'The Acolyte'.

        Don't saying things like "according to the provided context".
        If you don't know the answer just say: "I do not know the answer".


        <chat_history>
        {chat_history}
        </chat_history>
        <context>
        {prompt_context}
        </context>
        <question>
        {user_question}
        </question>

        Answer:
        """
    )
    return prompt


def create_generic_prompt(user_question: str):
    """
    Create a prompt for the language model using chat history (if enabled).
    Format the prompt according to the expected input format of the model.
    Don't use any additional context.

    Args:
        user_question (str): The user's question to generate a prompt for.

    Returns:
        str: The generated prompt for the language model.
    """
    if st.session_state.use_chat_history:
        chat_history = get_chat_history()
    else:
        chat_history = ""

    prompt = dedent(
        f"""
        You are a helpful AI chat assistant.

        Use chat history provided between <chat_history>
        and </chat_history> tags.
        Question is between <question> and </question> tags.

        If you don't know the answer just say: "I do not know the answer".


        <chat_history>
        {chat_history}
        </chat_history>
        <question>
        {user_question}
        </question>

        Answer:
        """
    )
    return prompt


def create_aggregation_prompt(user_question: str, answer_a: str, answer_b: str):
    """
    Create a prompt for the language model to combine two answers
    provided as an input. It is also using question that was asked
    and chat history (if enabled). Format the prompt according to
    the expected input format of the model.

    Args:
        user_question (str): The user's question to generate a prompt for.
        answer_a (str): First answer to evaluate and merge.
        answer_b (str): Second answer to evaluate and merge.

    Returns:
        str: The generated prompt for the language model.
    """
    if st.session_state.use_chat_history:
        chat_history = get_chat_history()
    else:
        chat_history = ""

    prompt = dedent(
        f"""
        You are a helpful AI chat assistant.
        You are evaluating two answers to a question provided
        between <question> and </question> tags.

        Provided answers can be found
        between <answer_a> and </answer_a> for the first answer,
        and <answer_b> and </answer_b> for second answer.

        Use history of the chat so far that is provided
        between <chat_history> and </chat_history> tags.

        Merge both answers into one, and return it.
        Ignore the answer that means "I don't know".

        Don't saying things like "according to the provided context".

        <chat_history>
        {chat_history}
        </chat_history>
        <answer_a>
        {answer_a}
        </answer_a>
        <answer_b>
        {answer_b}
        </answer_b>
        <question>
        {user_question}
        </question>

        Answer:
        """
    )
    return prompt


def main():
    st.title(f":speech_balloon: The Acolyte")

    init_service_metadata()
    init_config_options()
    init_messages()

    icons = {"assistant": "❄️", "user": "☃"}

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"], avatar=icons[message["role"]]):
            st.markdown(message["content"])

    disable_chat = (
        "service_metadata" not in st.session_state or len(st.session_state.service_metadata) == 0
    )
    if question := st.chat_input("Ask a question...", disabled=disable_chat):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": question})
        # Display user message in chat message container
        with st.chat_message("user", avatar=icons["user"]):
            st.markdown(question.replace("$", "\$"))

        # Display assistant response in chat message container
        with st.chat_message("assistant", avatar=icons["assistant"]):
            message_placeholder = st.empty()
            question = question.replace("'", "")
            with st.spinner("Thinking..."):

                response_generic = complete(
                    st.session_state.model_name__generic, create_generic_prompt(question)
                )
                response_service = complete(
                    st.session_state.model_name__service, create_specialized_prompt(question)
                )

                response_aggregation = complete(
                    st.session_state.model_name__aggregation,
                    create_aggregation_prompt(question, response_generic, response_service),
                )

                message_placeholder.markdown(response_aggregation)

        st.session_state.messages.append({"role": "assistant", "content": response_aggregation})


if __name__ == "__main__":
    session = get_active_session()
    root = Root(session)
    main()
