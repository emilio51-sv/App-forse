import pysqlite3
import sys
sys.modules['sqlite3'] = pysqlite3
import os
import pandas as pd
import json
from crewai import Crew, Agent, Task, Process

import streamlit as st

import os

openai_api_key = st.secrets["OPENAI_API_KEY"]
# Load environment variables

# Streamlit UI setup
st.title('German AI Startup Research Assistant')
st.write("""
This app is designed to help you conduct in-depth research on the German AI Startup Ecosystem. 
It parses an Excel file of startups, analyzes the data, and answers user queries based on agent collaboration.
""")

# File input for the Excel file
uploaded_file = st.file_uploader("Upload your Excel file with company data", type=['xlsx'])
if uploaded_file:
    # Load and parse the Excel file
    df = pd.read_excel(uploaded_file)
    json_data = df.to_json(orient='records')
    startups = json.loads(json_data)

    # Display the parsed data
    st.write("Parsed Data Preview:")
    st.dataframe(df)

    # Input from user for the query
    query = st.text_input("What do you want to know about the German AI Startup Ecosystem?")

    if st.button("Start Research"):
        # Define agents
        researcher_agent = Agent(
            role="Startup Data Researcher",
            goal="Analyze and extract relevant startups matching user queries.",
            backstory="""You are a skilled researcher with expertise in analyzing datasets to extract insights.""",
            verbose=True,
            memory=True,
        )

        summarizer_agent = Agent(
            role="Summary Generator",
            goal="Create a concise summary based on research findings.",
            backstory="""You excel at distilling complex research into clear and actionable summaries.""",
            verbose=True,
            memory=True,
        )

        # Define tasks
        research_task = Task(
            description=f"""
            Based on the provided dataset of startups, identify relevant organizations that match the user's query:
            "{query}". Include their names, descriptions, and any insights about their role in the ecosystem.
            """,
            expected_output="A detailed list of relevant startups and insights in JSON format.",
            agent=researcher_agent,
        )

        summary_task = Task(
            description=f"""
            Summarize the findings from the research task into a concise, easy-to-read format for the user.
            Ensure the summary captures the most important information relevant to the query: "{query}".
            """,
            expected_output="A brief, user-friendly summary of the findings.",
            agent=summarizer_agent,
        )

        # Form the crew
        crew = Crew(
            agents=[researcher_agent, summarizer_agent],
            tasks=[research_task, summary_task],
            process=Process.sequential,
            full_output=True,
        )

        # Kickoff the crew process
        results = crew.kickoff(inputs={"dataset": startups, "query": query})

        # Display the results
        st.subheader("Research Results")
        st.json(research_task.output.raw)

        st.subheader("Summary")
        st.write(summary_task.output.raw)
else:
    st.write("Please upload a file to proceed.")
