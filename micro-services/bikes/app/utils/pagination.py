def parse_pagination(args):
    """Extract pagination parameters from request args.

    Returns (page, page_size, offset).
    """
    page = max(1, args.get("page", 1, type=int))
    page_size = min(100, max(1, args.get("page_size", 20, type=int)))
    offset = (page - 1) * page_size
    return page, page_size, offset
