from rest_framework import pagination

PAGINATION_PAGE_SIZE = 10


class BasePagination(pagination.PageNumberPagination):
    page_size = PAGINATION_PAGE_SIZE
    page_size_query_param = 'limit'
