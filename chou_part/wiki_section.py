import mwclient
import re


def get_wikipedia_section(page_title, section_title):
    site = mwclient.Site("en.wikipedia.org")
    page = site.pages[page_title]
    content = page.text()
    # Adjusted regex pattern to match the section and its subsections
    section_pattern = rf"==\s*{re.escape(section_title)}\s*==\n(.*?)(?=\n==[^=])"
    section_content = re.search(section_pattern, content, re.S)
    if section_content:
        return section_content.group(1)
    else:
        return "Section not found"
