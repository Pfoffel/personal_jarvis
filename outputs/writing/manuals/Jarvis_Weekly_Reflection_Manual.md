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
    *   Jarvis will **always** calculate the start and end dates for the previous week as Monday to Sunday.
        *   If the report is initialized on a Sunday, the date range will be from the previous Monday to the current Sunday.
        *   If the report is initialized on a Monday, the date range will be from the previous Monday to the previous Sunday.
    *   For each day of the specified week, Jarvis will:
        *   Use the `get_notion_journaling_day` tool to retrieve the Notion journal entry for that day.
        *   If no entry exists for a particular day, Jarvis will note that in the report.
    *   Jarvis will compile all retrieved journal entries for analysis.

3.  **Analyze Journal Entries and Answer Reflection Questions:**
    *   Jarvis will analyze the compiled journal entries, focusing on identifying key events, accomplishments, challenges, and insights, paying particular attention to the "Primary Task," "Secondary Task," "Journaling Time," and "Notes / Ideas" sections.
    *   Based on the analysis, Jarvis will answer the following questions, writing the answers in the first person ("I" format) as if Henoch were answering:
        *   **What were the main accomplishments of the week?** (Identify successes, positive outcomes, and moments of progress, especially related to the "Primary Tasks.")
        *   **What were the main challenges or obstacles?** (Identify challenges, setbacks, and areas where improvement is needed, considering both "Primary" and "Secondary Tasks.")
        *   **What did I learn this week?** (Summarize key learnings, insights, and new knowledge gained from various experiences and activities.)
        *   **How well did I stick to my goals?** (Assess progress towards Q2 goals, website updates, calisthenics, and other side quests.)
        *   **What could I have done better?** (Identify areas where performance could have been improved, considering time management, communication, and other factors.)
        *   **What am I grateful for?** (Reflect on positive aspects, support from others, and opportunities experienced during the week.)
        *   **What are the main priorities for next week?** (Outline key tasks, projects, and goals to focus on in the coming week.)

4.  **Provide Personalized Feedback:**
    *   In addition to answering the reflection questions, Jarvis will provide the following personalized feedback:
        *   **Summary of Reflections:** A concise overview of the week's key events, accomplishments, and challenges.
        *   **Recurring Themes:** Identification of any recurring patterns or trends in the user's successes and challenges.
        *   **Suggestions for Improvement:** Specific and actionable recommendations for addressing the identified challenges and enhancing future performance.
        *   **Progress Tracking:** Assessment of the user's progress toward their Q2 goals, highlighting any significant achievements or areas where further effort is needed.
        *   **Alignment with Q2 Goals:** Evaluation of how well the week's activities contributed to the user's main quests and side quests, with suggestions for improving alignment in the future. Special attention will be given to how the "Primary Tasks" align with the user's goals.
        *   **Work-Life Balance:** Assess the balance between work and personal life, suggesting adjustments to prioritize rest, relationships, and personal well-being.
        *   **Relationship:** Provide feedback on the user's relationship with Mat, suggesting ways to improve communication, support, and connection.
        *   **Spontaneity:** Encourage the user to incorporate more spontaneous activities into their routine to break free from rigid planning.
        *   **Vlogging:** Offer encouragement and suggestions for the user's vlogging endeavors.
        *   **Climbing/Calisthenics:** Provide feedback on the user's physical activities, suggesting ways to align them more closely with their calisthenics goals.
        *   **Curiosity:** Encourage the user to continue exploring their curiosity and sharing their insights with others.

5.  **Save the Detailed Report:**
    *   Jarvis will save the detailed report, including the answers to the reflection questions and the personalized feedback, as a markdown file.
    *   The file name will follow the format: `Weekly_Reflection_Report_YYYY-MM-DD.md` (where YYYY-MM-DD is the Sunday date of the week being reflected upon).
    *   Jarvis will save the file in the `writing/reports` directory.

6.  **Upload the Report to Google Drive:**
    *   Jarvis will upload the saved report to the 'reports' folder within the 'Jarvis Content' folder on Google Drive.
        *   Jarvis will first use the `list_google_drive_files_and_folders` tool to confirm the existence of the "Jarvis Content" and "reports" folders and obtain their IDs.
    *   Jarvis will then use the `upload_file_to_google_drive` tool to upload the report to the "reports" folder.
        *   Jarvis will set the `convert_to_google_doc` parameter to `True` to convert the file to a Google Docs document.
        *   Jarvis will use the same file name as the local file (Weekly_Reflection_Report_YYYY-MM-DD.md), but without the extension (.md).
        *   Jarvis will set the `mime_type` parameter to `text/markdown`.
        *   Jarvis will set the `parent_folder_id` parameter to the ID of the "reports" folder obtained in the previous step.

**Important Considerations:**

*   **Data Privacy:** Jarvis will handle the user's journal entries with the utmost confidentiality and will only use them for the purpose of generating the weekly reflection report.
*   **Continuous Improvement:** This instruction manual is a living document and can be updated and refined based on the user's feedback and evolving needs.