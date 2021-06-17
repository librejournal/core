from rest_framework import pagination
from rest_framework.response import Response

PAGE_SIZE = 100
MAX_PAGE_SIZE = 200


class CustomLimitOffsetPagination(pagination.LimitOffsetPagination):
    default_limit = PAGE_SIZE
    max_limit = MAX_PAGE_SIZE
    limit_header = "HTTP_X_PAGINATION_LIMIT"
    offset_header = "HTTP_X_PAGINATION_OFFSET"

    def get_limit(self, request):
        try:
            return pagination._positive_int(
                request.META[self.limit_header],
                strict=False,
                cutoff=self.max_limit,
            )
        except KeyError:
            return self.default_limit

    def get_offset(self, request):
        try:
            return pagination._positive_int(
                request.META[self.offset_header],
            )
        except KeyError:
            return 0

    def get_paginated_response(self, data):
        headers = {
            "X-Pagination-Offset": str(self.offset),
            "X-Pagination-Limit": str(self.limit),
            "X-Pagination-Count": str(self.count),
        }

        return Response(data, headers=headers)
