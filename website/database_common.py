def search_string_highlight(search_string, text):
    search_strings = search_string.split(' וגם ')
    for s in search_strings:
        if s.strip():
            text = text.replace(s, f'<b><u>{s}</u></b>')
    return text