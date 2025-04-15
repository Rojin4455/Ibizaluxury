# pagination.py
from rest_framework.pagination import PageNumberPagination

class PropertyPagination(PageNumberPagination):
    page_size = 9  # Number of properties per page
    page_size_query_param = 'page_size'
    max_page_size = 100


