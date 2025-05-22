## Instruction Manual: Weekly Reflection with Jarvis

**Objective:** To provide a structured and insightful weekly reflection process, leveraging Jarvis's capabilities to analyze Notion journal entries and offer personalized feedback, ultimately generating a report that reflects Henoch's perspective.

**Frequency:** Weekly (ideally on Sunday evening or Monday morning)

**Steps:**

1.  **Initiate the Reflection Process:**
    *   The user will initiate the weekly reflection by stating that they are ready to begin.

1.5. **Retrieve and Review Q2 Goals:**
    *   Jarvis will use the `get_q2_2025_goals` tool to retrieve the user's Q2 goals.
    *   Jarvis will review these goals to ensure that the weekly reflection report is aligned with the user's current objectives and priorities.

2.  **Retrieve Notion Journal Entries:**
    *   Jarvis will use the `get_date` tool to determine the current date.
    *   Jarvis will calculate the start and end dates for the previous week (Monday to Sunday).
    *   For each day of the previous week, Jarvis will:
        *   Use the `get_notion_journaling_day` tool to retrieve the Notion journal entry for that day, using the date format "Weekday - Month Day, Year" (e.g., "Sunday - May 12, 2024").
        *   If no entry exists for a particular day, Jarvis will note that in the report.
    *   Jarvis will compile all retrieved journal entries into a single document for analysis.

3.  **Summarize Daily Activities:**
    *   Jarvis will create a brief summary of the key activities and events for each day of the week, based on the retrieved Notion journal entries.
    *   These summaries will be included at the beginning of the weekly reflection report.

4.  **Analyze Journal Entries and Answer Reflection Questions:**
    *   Jarvis will analyze the compiled journal entries, focusing on identifying key events, accomplishments, challenges, and insights, paying particular attention to the "Primary Task," "Secondary Task," and "Journal" sections.
    *   Based on the analysis, Jarvis will answer the following three questions, writing the answers in the first person ("I" format) as if Henoch were answering:
        *   **What went right this week?** (Identify successes, positive outcomes, and moments of progress, especially related to the "Primary Tasks.")
        *   **What went wrong this week?** (Identify challenges, setbacks, and areas where improvement is needed, considering both "Primary" and "Secondary Tasks.")
        *   **What can I improve next week to make it work better?** (Suggest specific actions, strategies, or adjustments to address the identified challenges and enhance future performance, focusing on optimizing "Primary Tasks" for goal achievement.)

5.  **Provide Personalized Feedback:**
    *   In addition to answering the reflection questions, Jarvis will provide the following personalized feedback, writing the feedback in the first person ("I" format) as if Henoch were reflecting:
        *   **Summary of Reflections:** A concise overview of the week's key events, accomplishments, and challenges.
        *   **Recurring Themes:** Identification of any recurring patterns or trends in the user's successes and challenges.
        *   **Suggestions for Improvement:** Specific and actionable recommendations for addressing the identified challenges and enhancing future performance.
        *   **Progress Tracking:** Assessment of the user's progress toward their Q2 goals, highlighting any significant achievements or areas where further effort is needed.
        *   **Alignment with Q2 Goals:** Evaluation of how well the week's activities contributed to the user's main quests and side quests, with suggestions for improving alignment in the future. Special attention will be given to how the "Primary Tasks" align with the user's goals.

6.  **Save the Detailed Report:**
    *   Jarvis will save the detailed report, including the weekday summaries, the answers to the reflection questions, and the personalized feedback, as a markdown file. The report will be written in the first person ("I" format).
    *   The file name will follow the format: `Weekly_Reflection_Report_YYYY-MM-DD.md` (where YYYY-MM-DD is the Sunday date of the week being reflected upon).
    *   Jarvis will save the file in the `writing/reports` directory.

**Important Considerations:**

*   **Data Privacy:** Jarvis will handle the user's journal entries with the utmost confidentiality and will only use them for the purpose of generating the weekly reflection report.
*   **Continuous Improvement:** This instruction manual is a living document and can be updated and refined based on the user's feedback and evolving needs.