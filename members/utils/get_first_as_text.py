__all__ = ['get_first_as_text']


def get_first_as_text(elements):
    try:
        return elements[0].text_content().strip()
    except (IndexError, AttributeError):
        return None
