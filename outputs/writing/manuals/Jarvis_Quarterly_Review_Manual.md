# Jarvis Quarterly Review Manual

## I. Introduction

*   **Purpose of the Quarterly Review:** To assess progress towards quarterly goals, identify key insights, and plan for the upcoming quarter.
*   **Integration with Newsletter:** Leveraging the review as content for "The Journey" newsletter.
*   **Reliance on User Input:** Acknowledging that the user will provide a clear understanding of the goals and their outcomes.

## II. Data Retrieval and Preparation

*   **Goal Retrieval:**
    *   Action: Use `get_q2_2025_goals` to retrieve the quarterly goals. (This will be adjusted to retrieve the relevant quarter's goals in future iterations).
*   **Journaling Data Retrieval:**
    *   Action: Use `get_date` to determine the current month and year.
    *   Action: Use `get_notion_journaling_month` to retrieve all journaling entries for each month of the quarter. The current quarter's months will be dynamically determined.
*   **Idea Retrieval:**
    *   Action: Use `get_notion_ideas` to retrieve any relevant ideas from the Notion database.
    *   Memory: Save the ideas to memory for future reference using `add_new_memory`.

## III. Analysis and Insight Generation

*   **Goal Progress Assessment:**
    *   Compare the initial quarterly goals with the user-provided outcomes.
    *   Identify areas of success, areas needing improvement, and any deviations from the original plan.
    *   Assess whether deviations from the plan were positive (leading to greater progress) or negative (hindering progress).
*   **Journaling Entry Analysis:**
    *   Analyze journaling entries for recurring themes, key insights, and significant events.
    *   Identify lessons learned, challenges faced, and strategies employed.
    *   Include key journaling entries that underline the statements made in the review.
*   **Additional Achievements:**
    *   Include a section highlighting general achievements beyond the main quests, providing a more comprehensive picture of the user's progress.
*   **Idea Integration:**
    *   Review retrieved ideas for relevance to the goals and insights.
    *   Identify any ideas that were implemented or could be implemented in the future.
*   **Reflection Questions (Examples - To be filled in during the review):**
    *   What were the biggest wins of the quarter? (Based on goal achievements and positive outcomes)
    *   What were the biggest challenges? (Based on recurring themes in journaling entries)
    *   What key lessons were learned? (Based on insights from journaling entries)
    *   What could have been done differently? (Based on challenges and areas needing improvement)
    *   What are the top priorities for the next quarter? (Based on current goals and identified areas for improvement)
    *   How well did I manage my time and energy? (Based on journaling entries and task completion)
    *   What new skills did I acquire? (Based on journaling entries and project progress)
    *   How can I improve my focus and productivity? (Based on challenges and areas needing improvement)
    *   What steps can I take to better align my actions with my goals? (Based on goal progress and deviations)
*   **Satisfaction Score:**
    *   Assign a score from 1-10 to broadly assess satisfaction with the quarter's progress.

## IV. Newsletter Draft Generation

*   **Structure:** Follow the established structure of "The Journey" newsletter:
    *   Welcome & Introduction: A brief welcome message and introduction to the newsletter's purpose. Mention your passion for AI, automation, and personal growth. State the goal of sharing insights, ideas, challenges, and discoveries. Emphasize collaboration and community.
    *   This Quarter in Review: Key Events: Highlight 2-3 significant events from the month. Wins to Celebrate: List accomplishments and successes. Challenges & Setbacks: Acknowledge difficulties and obstacles faced. Behind the Scenes: Share details about ongoing projects and habits.
    *   Lessons & Insights: What I Learned: Summarize key learnings related to AI, automation, or personal growth. "Aha!" Moment: Describe a significant realization or breakthrough. Resource Corner: Recommend helpful tools or resources.
    *   Looking Ahead: Next Month's Goals: Outline upcoming projects and objectives. One Big Question: Pose a thought-provoking question related to AI, technology, or personal development. Personal Challenge for You!: Suggest a challenge for the reader to encourage engagement.
    *   Community Corner: Invitation for Feedback: Ask for feedback on the newsletter. Questions for Engagement: Pose questions to stimulate discussion. How to Connect: Include links to your website, social media profiles, and email address.
    *   Sign-off: Thank the reader for joining you on the journey. Express excitement for sharing future discoveries. Include your name and the date of the next issue.
*   **Content:**
    *   Use the insights generated in Section III to populate the newsletter sections.
    *   Write in the first person ("I" form) to reflect the user's personal voice.
    *   Ensure the newsletter is engaging, personal, and of appropriate length, referencing previous newsletters for style and tone. Pay close attention to the length, structure, and level of detail in previous newsletters to ensure consistency.
    *   Ensure the newsletter is profound with a personal touch where subscribers get to know more of the user's life as well. obviously don't mention names or anything but go more into the details, they are there because they want to know about the user and his life's progress.
    *   Maintain a positive and engaging tone.
    *   Focus on providing value to subscribers.

## V. Review Output and Saving

*   Action: Use `get_date` to determine the current year and quarter.
*   Action: Use `save_output` to save the generated quarterly review as a Markdown file in the "writing/reports" subfolder.
*   File Name: "Quarterly\_Review\_Q[Quarter Number]\_[Year].md" (e.g., Quarterly\_Review\_Q3\_2025.md)

## VI. Newsletter Draft Output and Saving

*   Action: Use `get_date` to determine the current year and quarter.
*   Action: Use `save_output` to save the generated newsletter draft as a Markdown file in the "writing/newsletters" subfolder.
*   File Name: "Quarterly\_Review\_Newsletter\_Draft\_Q[Quarter Number]\_[Year].md" (e.g., Quarterly\_Review\_Newsletter\_Draft\_Q3\_2025.md)

## VII. Google Drive Upload and Conversion

*   Action: List all files and folders in the 'Jarvis Content' folder in Google Drive using `list_google_drive_files_and_folders` to identify the ideal subfolders for the review and newsletter draft.
*   Based on the listing, the 'writing' folder seems most appropriate. Within it, 'reports' for the review and 'newsletters' for the draft.
*   Action: Upload the review to the 'writing/reports' folder and newsletter draft to the 'writing/newsletters' folder in Google Drive, converting them to Google Docs format using `upload_file_to_google_drive` with `convert_to_google_doc=True`.

## VIII. Memory Saving

*   Action: Use `add_new_memory` to save the newly added ideas to memory.

## IX. Refinement and Feedback

*   Present the manual and newsletter draft to the user for review and feedback.
*   Incorporate any feedback to improve the process.
