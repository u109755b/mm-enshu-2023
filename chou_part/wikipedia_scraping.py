import wikipedia
import spacy
import contextualSpellCheck
import re


nlp = spacy.load("en_core_web_lg")
contextualSpellCheck.add_to_pipe(nlp)
seperate_line = "-" * 40


def PrintWiki(wikipage):
    print(seperate_line)
    print(wikipage)
    print(wikipage.summary.rstrip() + "\n" + seperate_line)


def limit_words(string: str, limit: int) -> str:
    words = re.findall(r"\b\w+\b|\s+", string)
    if len([word for word in words if word.strip()]) > limit:
        count = 0
        last_word_index = 0
        for i, word in enumerate(words):
            if word.strip():
                count += 1
            if count == limit:
                last_word_index = i
                break
        string = (
            "".join(words[: last_word_index + 1])
            + f" ......\nWords limit ({limit}) reached.\n"
        )
    return string


def SpellingCheck(title: str) -> str:
    doc = nlp(title)
    if doc._.performed_spellCheck:
        correction = (doc._.outcome_spellCheck).lower()
        response = input(
            f"It seems like there are some errors in your input.\nDo you mean {correction}? (yes/no): "
        ).lower()
        if response == "yes" or response == "y":
            title = correction
        else:
            title = input("The title you are looking for is not found, try another:\n")
    return title


def WikiSearch(title: str):
    searchresults = wikipedia.search(title)
    print("Here is a list of potentially related topics:")
    for i in range(len(searchresults)):
        print(f"{i}: {searchresults[i]}")
    user_message = input(
        "Is the correct title in this list? (enter the index number if it was)\n"
    )
    if user_message.isnumeric() and int(user_message) in range(len(searchresults)):
        title = searchresults[int(user_message)]
        print(f'User chose "{title}".')
        return WikiContente(title)
    else:
        if user_message.lower() == "no":
            user_message = input(
                "The title you are looking for is not found, try another:\n"
            )
        return WikiContente(user_message)


def WikiContente(title: str):
    try:
        wikipage = wikipedia.page(title, auto_suggest=False)
        PrintWiki(wikipage)
        user_message = input(
            "Is this the Wikipedia Page you are looking for? (yes/no)\n"
        )
        while user_message.lower() != "no" and user_message.lower() != "yes":
            user_message = input("Input not recognised, try again (yes/no):\n")

        if user_message.lower() == "no":
            return WikiSearch(user_message)

        text = str(wikipage) + "\nSummary:\n" + wikipage.summary.rstrip() + "\n"
        new_text = (
            str(wikipage)
            + "\nSummary:\n"
            + limit_words(wikipage.summary, 100).rstrip()
            + "\n"
        )

        useful_sections = [
            "Plot",
            "Plot summary",
            "Synopsis",
            "Story",
            "Fairy tale",
            "Legend",
        ]
        use_new_text_flag = 0
        for section in useful_sections:
            article = wikipage.section(section)
            if article:
                use_new_text_flag = 1
                article = limit_words(article, 800)
                new_text = f"{new_text}\n{section}:\n{article.rstrip()}\n"
        if use_new_text_flag:
            text = new_text
        title = str(wikipage).replace("<WikipediaPage '", "").replace("'>", "")
        return text, title

    except wikipedia.exceptions.PageError as PE:
        title = SpellingCheck(title)
        return WikiSearch(title)

    except wikipedia.exceptions.DisambiguationError as DE:
        return WikiSearch(title)
