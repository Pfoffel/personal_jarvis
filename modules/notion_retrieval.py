import os
from datetime import datetime
from notion_client import Client
from dotenv import load_dotenv
from langchain.tools import tool
from langchain_community.tools import DuckDuckGoSearchResults

load_dotenv()
notion = Client(auth="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")

# helpers

def get_notion_db(id: str):
    return notion.databases.query(database_id=id)

def get_monthly_pages(selected_month: int, selected_year: int, db_id: str, db = None) -> list:
    """ Get's you the full list of journaling entries from the specified month and year 
    including everyday's Primary and Seconday Tasks, a journal section and notes and ideas if available """

    if db_id:
        db = get_notion_db(db_id)
    if not db:
        return []
    pages = []
    for results in db["results"]:
        page_date = results["properties"]["Date"]["date"]["start"]
        if datetime.strptime(page_date, "%Y-%m-%d").month == selected_month and datetime.strptime(page_date, "%Y-%m-%d").year == selected_year:
            pages.append({
                "page_id": results["id"],
                "title": results["properties"]["Day"]["title"][0]["text"]["content"]
            })
    return pages
    
def get_page(selected_date: str, db_id: str, db = None) -> list:
    """ Get's you the full list of journaling entries from the specified month and year 
    including everyday's Primary and Seconday Tasks, a journal section and notes and ideas if available """

    if db_id:
        db = get_notion_db(db_id)
    if not db:
        return []
    pages = []
    for results in db["results"]:
        page_date = results["properties"]["Date"]["date"]["start"]
        if datetime.strptime(page_date, "%Y-%m-%d") == datetime.strptime(selected_date, "%Y-%m-%d"):
            pages.append({
                "page_id": results["id"],
                "title": results["properties"]["Day"]["title"][0]["text"]["content"]
            })
            break
    return pages

def get_block_children(block_id):
    """Retrieve all children blocks of a given block ID, handling pagination."""
    all_children = []
    cursor = None

    while True:
        response = notion.blocks.children.list(
            block_id=block_id,
            start_cursor=cursor,
            page_size=100
        )
        all_children.extend(response["results"])
        cursor = response.get("next_cursor")
        if not cursor:
            break

    return all_children

def extract_rich_text(block, ignore: list = []):
    """
    Extracts and returns a list of plain text from any block
    that has a rich_text property (paragraphs, headings, lists, etc.).
    """
    texts = []
    # Each block type has its own key, e.g. 'paragraph', 'heading_1', etc.
    block_type = block["type"]
    content = block.get(block_type, {})

    # Many types include a 'rich_text' array
    for rt in content.get("rich_text", []):
        text = rt.get("plain_text", "")
        if text in ignore:
            continue
        texts.append(text)

    return texts

def traverse_blocks(blocks, ignore = []):
    """
    Given a list of block objects, recursively traverse them:
    - Extract text from the block itself
    - If the block has children, fetch and traverse those
    Returns a flat list of strings.
    """
    collected = []

    for block in blocks:
        # 1. Extract from this block
        collected.extend(extract_rich_text(block, ignore))

        # 2. If it has children, recurse
        if block.get("has_children", False):
            child_blocks = get_block_children(block["id"])
            collected.extend(traverse_blocks(child_blocks, ignore))

    return collected

def get_page_text(page_id, ignore: list = [], format: list = []):
    """
    Fetches and returns every piece of plain text on the given Notion page.
    """
    # Top-level blocks of the page
    top_blocks = get_block_children(page_id)
    # Traverse and collect
    all_text_list = traverse_blocks(top_blocks, ignore)
    for i, text in enumerate(all_text_list):
        if text in format:
            all_text_list[i] = f"**{text}**:"
            
    all_text = "\n".join(all_text_list)
    return all_text

# -----------------------------------------------------

# tools

@tool
def get_env_variables() -> dict:
    """ Get all relevant envirenmental variables for API calls """
    NOTION_KEY = "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"
    DB_ID = "1c7cbfc5adbc80d4b29adec457d46ca3"

    return {
        "NOTION_KEY": NOTION_KEY,
        "DB_ID": DB_ID
    }

@tool
def get_date():
    """ Get the current date """
    return datetime.now()

@tool
def search_internet(query: str) -> list:
    """ Get internet search results in a list containing the following:
    - snippet
    - title
    - link """
    search = DuckDuckGoSearchResults(output_format="list")
    return search.invoke(query)

@tool
def get_notion_journaling_month(selected_month: int, selected_year: int ) -> list:
    """ Get's you the full list of journaling entries from the specified month and year 
    including everyday's Primary and Seconday Tasks, a journal section and notes and ideas if available """

    db_id = "1c7cbfc5adbc80d4b29adec457d46ca3"

    to_ignore = [
        "Week Sub Tasks",
        # "Primary Task",
        "Most needle moving task for today",
        "Aligns with current quest",
        # "Secondary Task",
        "Do onlny when primary task is completed",
        # "Journaling Time",
        "What happened today",
        # "Notes / Ideas",
        "Leave any insights, ideas or doubts to follow up on here.",
        "Untitled"
    ]

    to_format = [
        "Primary Task",
        "Secondary Task",
        "Journaling Time",
        "Highlight of the Day",
        "Notes / Ideas"
    ]

    monthly_pages = get_monthly_pages(selected_month=selected_month, selected_year=selected_year, db_id=db_id)

    results = []
    for page in monthly_pages:
        print(page["title"])
        result = {
            "id": page["page_id"],
            "title": page["title"],
            "notes": get_page_text(page["page_id"], to_ignore, to_format)
        }
        results.append(result)

    return results

@tool
def get_notion_journaling_day(selected_day: int, selected_month:int, selected_year: int) -> list:
    """ Get's you the journaling entries from the specified date 
    including everyday's Primary and Seconday Tasks, a journal section and notes and ideas if available """

    db_id = "1c7cbfc5adbc80d4b29adec457d46ca3"
    selected_date = f"{int(selected_year)}-{int(selected_month):02d}-{int(selected_day):02d}"

    to_ignore = [
        "Week Sub Tasks",
        # "Primary Task",
        "Most needle moving task for today",
        "Aligns with current quest",
        # "Secondary Task",
        "Do onlny when primary task is completed",
        # "Journaling Time",
        "What happened today",
        # "Notes / Ideas",
        "Leave any insights, ideas or doubts to follow up on here.",
        "Untitled"
    ]

    to_format = [
        "Primary Task",
        "Secondary Task",
        "Journaling Time",
        "Highlight of the Day",
        "Notes / Ideas"
    ]

    monthly_pages = get_page(selected_date=selected_date, db_id=db_id)

    results = []
    for page in monthly_pages:
        print(page["title"])
        result = {
            "id": page["page_id"],
            "title": page["title"],
            "notes": get_page_text(page["page_id"], to_ignore, to_format)
        }
        results.append(result)

    return results

# -----------------------------------------------------


if __name__ == "__main__":
    db_id = "1c7cbfc5adbc80d4b29adec457d46ca3"

    monthly_pages = get_monthly_pages(4, 2025, get_notion_db(db_id))
    to_ignore = [
        "Week Sub Tasks",
        # "Primary Task",
        "Most needle moving task for today",
        "Aligns with current quest",
        # "Secondary Task",
        "Do onlny when primary task is completed",
        # "Journaling Time",
        "What happened today",
        # "Notes / Ideas",
        "Leave any insights, ideas or doubts to follow up on here.",
        "Untitled"
    ]

    to_format = [
        "Primary Task",
        "Secondary Task",
        "Journaling Time",
        "Highlight of the Day",
        "Notes / Ideas"
    ]

    results = []
    for page in monthly_pages:
        print(page["title"])
        result = {
            "id": page["page_id"],
            "title": page["title"],
            "notes": get_page_text(page["page_id"], to_ignore, to_format)
        }
        results.append(result)
    for result in results:
        print(result)
