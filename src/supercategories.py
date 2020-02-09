def get_super_categories(field):
	params = {
        "action": "query",
        "format": "json",
        "prop": "categories",
        "titles": field
    }

    session = requests.Session()
    return session.get(url='https://en.wikipedia.org/w/api.php', params=params)
