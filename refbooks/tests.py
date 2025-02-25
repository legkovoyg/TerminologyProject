from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.utils import timezone

from .models import RefBook, RefBookVersion, RefBookElement


class RefBookAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.refbook1 = RefBook.objects.create(
            code="MS1",
            name="Специальности медработников",
            description="Пример: врачи, хирурги и т.д."
        )

        self.version1_1 = RefBookVersion.objects.create(
            refbook=self.refbook1,
            version="1.0",
            date=timezone.datetime(2022, 1, 1).date()
        )

        RefBookElement.objects.create(version=self.version1_1, code="1", value="Медсестра")
        RefBookElement.objects.create(version=self.version1_1, code="2", value="Фельдшер")

        self.version1_2 = RefBookVersion.objects.create(
            refbook=self.refbook1,
            version="2.0",
            date=timezone.datetime(2022, 6, 1).date()
        )

        RefBookElement.objects.create(version=self.version1_2, code="1", value="Врач-терапевт")
        RefBookElement.objects.create(version=self.version1_2, code="2", value="Травматолог")
        RefBookElement.objects.create(version=self.version1_2, code="3", value="Хирург")

        self.refbook2 = RefBook.objects.create(
            code="ICD-10",
            name="МКБ-10",
            description="Международная классификация болезней 10-го пересмотра"
        )

        # Версия 1.0
        self.version2_1 = RefBookVersion.objects.create(
            refbook=self.refbook2,
            version="1.0",
            date=timezone.datetime(2022, 1, 1).date()
        )

        RefBookElement.objects.create(version=self.version2_1, code="J00", value="Острый насморк")
        RefBookElement.objects.create(version=self.version2_1, code="S99", value="Тахиаритмия")


    def test_get_refbooks_list(self):
        """
        Проверка получения списка справочников (ожидаем 2)
        """
        url = reverse('refbooks-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['refbooks']), 2)

    def test_get_refbooks_by_date(self):
        """
        Проверка списка справочников по дате
        """
        url = reverse('refbooks-list')

        response = self.client.get(url, {'date': '2022-01-15'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['refbooks']), 2)

        response = self.client.get(url, {'date': '2021-12-31'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['refbooks']), 0)

    def test_get_refbook_elements(self):
        """
        Проверка элементов справочника
        """
        url = reverse('refbooks-elements', args=[self.refbook1.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['elements']), 3)

    def test_get_refbook_elements_by_version(self):
        """
        Проверка получения элементов по конкретной версии 1.0.
        """
        url = reverse('refbooks-elements', args=[self.refbook1.id])
        response = self.client.get(url, {'version': '1.0'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['elements']), 2)

    def test_check_element_valid(self):
        """
        Проверка элемента
        """
        url = reverse('refbooks-check-element', args=[self.refbook1.id])
        response = self.client.get(url, {'code': '1', 'value': 'Врач-терапевт'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['result'])

    def test_check_element_invalid(self):
        """
        Проверка элемента
        """
        url = reverse('refbooks-check-element', args=[self.refbook1.id])
        response = self.client.get(url, {'code': '1', 'value': 'Неправильное значение'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['result'])

    def test_check_element_by_version(self):
        """
        Проверка по версии
        """
        url = reverse('refbooks-check-element', args=[self.refbook1.id])

        response = self.client.get(url, {
            'code': '3',
            'value': 'Хирург',
            'version': '2.0'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['result'])

        response = self.client.get(url, {
            'code': '3',
            'value': 'Хирург',
            'version': '1.0'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['result'])
