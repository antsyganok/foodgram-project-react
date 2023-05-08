from rest_framework.pagination import PageNumberPagination


class RecipePagination(PageNumberPagination):
    page_size = 6
    page_size_query_param = 'limit'  # 'page_size'
    max_page_size = page_size
    # page_query_param = 'strantitsa'  # 'page'
