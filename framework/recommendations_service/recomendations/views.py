from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .simple import recommend_by_last_category


class RecomendationsView(APIView):
    def get(self, request):
        return recommend_by_last_category(self, request, last_product=5)
