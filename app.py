import json
import traceback
import streamlit as st
import os
from langchain import OpenAI
from langchain.document_loaders import DirectoryLoader

from langchain.llms import OpenAI
import looker_sdk
from indexer import Indexer
from looker_query_runner import LookerQueryRunner

from query_converter import QueryConverter

sdk = looker_sdk.init40("looker.ini")
model_name = os.environ.get("LOOKER_MODEL_NAME")
lookml_dir = os.environ.get("LOOKML_DIR")

# error if the model name and lookml_dir is not set
if model_name is None or lookml_dir is None:
    raise Exception("Please set LOOKER_MODEL_NAME and LOOKML_DIR")

llm = OpenAI(model_name="text-davinci-003", temperature=0)


@st.cache_resource
def create_index():
    loader = DirectoryLoader(lookml_dir)
    docs = loader.load()

    return Indexer(docs, llm).run()


docsearch = create_index()

query_converter = QueryConverter(model_name, docsearch, llm)


looker_query_runner = LookerQueryRunner(sdk)

# This example shows how to make a simple question in natural language and get the result back from the Looker API.
st.title("GPT + Looker")

text = "Show me latest 10 pets."
question = st.text_area("question", placeholder=text)

if st.button("Send"):
    try:
        with st.spinner('Wait for it...'):
            write_query = query_converter.run(question)
            st.markdown("## Query")
            st.markdown(f"```json\n{json.dumps(write_query, indent=2)}\n```")
            st.markdown("## Query Result")
            query_result_df = looker_query_runner.run_query(write_query)
            st.table(query_result_df)
    except Exception as e:
        # print error and traceback
        print(f"error: {e}")
        print(traceback.format_exc())
        st.error(e)
