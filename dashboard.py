#Step 4: Part B - Building The Dashboard
import streamlit as st
import pandas as pd
import sqlite3
#I used streamlit to turn plain Python Script into a working web dashboard with very little code.
#Display the Title of the dashboard
st.markdown(
    """
    <h1 style="text-align: center; font-size: 45px; color: #1E90FF;">
        NEXTGEN PROGRAM PERFORMANCE DASHBOARD
    </h1>
    """,
    unsafe_allow_html=True
)

conn = sqlite3.connect('nextgen.db')
applicants = pd.read_sql("SELECT * FROM applicants;", conn)
interns = pd.read_sql("SELECT * FROM interns;", conn)
hackathon_scores = pd.read_sql("SELECT * FROM hackathon_scores;", conn)

#Add a domain filter.This creates a dropdown menu at the top of the dashboard.
domain_list = ['ALL'] + sorted(applicants["Domain_Applied"].unique().tolist())
selected_domain = st.selectbox("Filter by Domain_Applied", domain_list)

if selected_domain != 'All':
    applicants_filtered = applicants[applicants["Domain_Applied"] == selected_domain]
    interns_filtered = hackathon_scores[hackathon_scores["Domain_Applied"] == selected_domain]
else:
    applicants_filtered = applicants
    interns_filtered = hackathon_scores

#Show the required elements
#Funnel(total applicants vs total interns):

col1, col2, col3 = st.columns(3)#Display the Numbers Side By Side
col1.metric("Total Applicants", f"{len(applicants):,}")
col2.metric("Total Applicants Per Domain", f"{len(applicants_filtered ):,}")#Number of applicants per domain
col3.metric("Completed Interns", f"{len(interns_filtered) :,}")

#Completion rate per domain: Reuse your Querry 4 logic and display it as a bar chart using
# Reuse  SQL query 4 to calculate conversion rate
query = """
SELECT 
    a.Domain_Applied,
    COUNT(DISTINCT a.applicant_id) AS total_applicants,
    COUNT(DISTINCT i.intern_id) AS total_completed,
    ROUND(
        100.0 * COUNT(DISTINCT i.intern_id) / COUNT(DISTINCT a.applicant_id),
        2
    ) AS conversion_rate_pct
FROM applicants a
LEFT JOIN interns i
    ON a.Applicant_ID = i.Applicant_ID
    AND i.Completion_status = 'Completed'
GROUP BY a.Domain_Applied
ORDER BY conversion_rate_pct DESC;
"""

conversion_rate = pd.read_sql_query(query, conn)
#Display the title of the barchart
st.subheader("Completion Rate by Domain")
#Display the completion rate bar chart
st.bar_chart(
    conversion_rate,
    x="Domain_Applied",
    y="conversion_rate_pct"
)

#Average hackathon score per domain: Reuse Querry 2's logic, displayed as another
query = """
-- Calculates the average hackathonscore for each domain
SELECT Domain_Applied, ROUND(AVG(score), 2) AS Average_Score
FROM hackathon_scores
GROUP BY Domain_Applied
ORDER BY  Average_Score DESC;
"""
average_hackathon_score = pd.read_sql_query(query, conn)

#Display the title of the bar chart
st.subheader("Average Hackathon Score per Domain")
#Display the bar chart
st.bar_chart(
    average_hackathon_score,
    x = "Domain_Applied",
    y = "Average_Score"
)

#Leaderboard of top 10 performers
query = """
-- Lists the top 10 performing interns 
SELECT i.intern_id, i.Domain_Applied, h.Score
FROM interns i
JOIN hackathon_scores h ON i.intern_id = h.intern_id
ORDER BY h.Score DESC
LIMIT 10;
"""
top_performers = pd.read_sql_query(query, conn)

#Display the title of the table for the top 10 perming interns
st.subheader("Top 10 Performers")
#Creates the dataframe containing top the top performers
st.dataframe(top_performers)
#Step 5: Record The Demo
#The dashboard's default view(all domains)
#Selecting a specific domain from the dropdown/filter and showing the numbers/charts update
#The leaderboard of top performers clearly visible