from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
# Create your views here.


from refbooks.models import RefBook, RefBookVersion, RefBookElement
from refbooks.serializers import RefBookSerializer, RefBookElementSerializer


class RefBookListAPIView(APIView):
    """
    Получение списка справочников.

    Описание:
      Этот эндпоинт возвращает список справочников. Опционально можно передать параметр `date` (в формате ГГГГ-ММ-ДД),
      чтобы получить только те справочники, у которых есть версия с датой начала действия меньше или равной указанной дате.

    Параметры запроса:
      - date (string, формат: ГГГГ-ММ-ДД, опционально): Если передан, фильтрует справочники по наличию активной версии на указанную дату

    В случае неверного формата даты возвращается HTTP 400 с сообщением об ошибке.
    """

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'date',
                openapi.IN_QUERY,
                description="Дата начала действия в формате ГГГГ-ММ-ДД",
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_DATE
            )
        ],
        responses={
            200: openapi.Response('Список справочников', schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'refbooks': openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        items=openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'id': openapi.Schema(type=openapi.TYPE_STRING),
                                'code': openapi.Schema(type=openapi.TYPE_STRING),
                                'name': openapi.Schema(type=openapi.TYPE_STRING),
                            }
                        )
                    )
                }
            ))
        }
    )
    def get(self, request):
        date_param = request.query_params.get('date')

        queryset = RefBook.objects.all()

        if date_param:
            try:
                specified_date = timezone.datetime.strptime(date_param, '%Y-%m-%d').date()
                # Фильтруем справочники, у которых есть версии с датой начала <= указанной даты
                refbooks_ids = RefBookVersion.objects.filter(
                    date__lte=specified_date
                ).values_list('refbook_id', flat=True).distinct()

                queryset = queryset.filter(id__in=refbooks_ids)
            except ValueError:
                return Response(
                    {"error": "Неверный формат даты. Используйте ГГГГ-ММ-ДД"},
                    status=status.HTTP_400_BAD_REQUEST
                )

        serializer = RefBookSerializer(queryset, many=True)

        return Response({"refbooks": serializer.data})


class RefBookElementsAPIView(APIView):
    """
    Получение элементов заданного справочника.

    Описание:
      Этот эндпоинт позволяет получить элементы для конкретного справочника.
      Идентификатор справочника передается в URL. Опционально можно указать параметр `version` для выбора конкретной версии.
      Если параметр `version` не указан, выбирается текущая активная версия (по дате).

    Параметры запроса:
      - version (string, опционально): номер версии справочника, для которой необходимо получить элементы.

    Если справочник с указанным идентификатором не найден, возвращается HTTP 404.
    """


    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'version',
                openapi.IN_QUERY,
                description="Версия справочника",
                type=openapi.TYPE_STRING
            )
        ],
        responses={
            200: openapi.Response('Элементы справочника', schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'elements': openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        items=openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'code': openapi.Schema(type=openapi.TYPE_STRING),
                                'value': openapi.Schema(type=openapi.TYPE_STRING),
                            }
                        )
                    )
                }
            )),
            404: openapi.Response('Справочник не найден')
        }
    )
    def get(self, request, id):
        refbook = get_object_or_404(RefBook, id=id)
        version_param = request.query_params.get('version')

        if version_param:
            # Получаем конкретную версию
            version = get_object_or_404(RefBookVersion, refbook=refbook, version=version_param)
        else:
            # Получаем текущую версию
            current_date = timezone.now().date()
            version = RefBookVersion.objects.filter(
                refbook=refbook,
                date__lte=current_date
            ).order_by('-date').first()

            if not version:
                return Response(
                    {"error": "У справочника нет активной версии"},
                    status=status.HTTP_404_NOT_FOUND
                )

        elements = RefBookElement.objects.filter(version=version)
        serializer = RefBookElementSerializer(elements, many=True)

        return Response({"elements": serializer.data})


class RefBookElementCheckAPIView(APIView):
    """
    Валидация элементов справочника.

    Описание:
      Этот эндпоинт проверяет, существует ли элемент справочника с заданными параметрами.
      Идентификатор справочника передается в URL.
      Обязательные параметры запроса: `code` (код элемента) и `value` (значение элемента).
      Опционально можно указать `version` для проверки в конкретной версии справочника.
      Если параметр `version` не указан, проверка проводится для текущей активной версии.

    Параметры запроса:
      - code (string, обязательный): код элемента справочника.
      - value (string, обязательный): значение элемента справочника.
      - version (string, опционально): номер версии справочника.

    Если обязательные параметры отсутствуют, возвращается HTTP 400.
    Если справочник не найден — HTTP 404.
    """
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'code',
                openapi.IN_QUERY,
                description="Код элемента",
                type=openapi.TYPE_STRING,
                required=True
            ),
            openapi.Parameter(
                'value',
                openapi.IN_QUERY,
                description="Значение элемента",
                type=openapi.TYPE_STRING,
                required=True
            ),
            openapi.Parameter(
                'version',
                openapi.IN_QUERY,
                description="Версия справочника",
                type=openapi.TYPE_STRING
            )
        ],
        responses={
            200: openapi.Response('Результат проверки', schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'result': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                }
            )),
            400: openapi.Response('Отсутствует обязательный параметр'),
            404: openapi.Response('Справочник не найден')
        }
    )
    def get(self, request, id):
        code = request.query_params.get('code')
        value = request.query_params.get('value')

        if not code or not value:
            return Response(
                {"error": "Параметры code и value обязательны"},
                status=status.HTTP_400_BAD_REQUEST
            )

        refbook = get_object_or_404(RefBook, id=id)
        version_param = request.query_params.get('version')

        if version_param:
            # Получаем конкретную версию
            version = get_object_or_404(RefBookVersion, refbook=refbook, version=version_param)
        else:
            # Получаем текущую версию
            current_date = timezone.now().date()
            version = RefBookVersion.objects.filter(
                refbook=refbook,
                date__lte=current_date
            ).order_by('-date').first()

            if not version:
                return Response(
                    {"error": "У справочника нет активной версии"},
                    status=status.HTTP_404_NOT_FOUND
                )

        # Проверяем существование элемента
        element_exists = RefBookElement.objects.filter(
            version=version,
            code=code,
            value=value
        ).exists()

        return Response({"result": element_exists})