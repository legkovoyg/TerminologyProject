from django.urls import path
from refbooks.views import RefBookListAPIView, RefBookElementsAPIView, RefBookElementCheckAPIView

urlpatterns = [
    path('refbooks/', RefBookListAPIView.as_view(), name='refbooks-list'),
    path('refbooks/<int:id>/elements', RefBookElementsAPIView.as_view(), name='refbooks-elements'),
    path('refbooks/<int:id>/check_element', RefBookElementCheckAPIView.as_view(), name='refbooks-check-element'),
]