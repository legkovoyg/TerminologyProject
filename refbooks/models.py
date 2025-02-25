from django.db import models

# Create your models here.

class RefBook(models.Model):

    """
    Справочник:
        - Идентификатор
        - Код (строка, 100 символов, обязательно для заполнения)
        - Наименование (строка, 300 символов, обязательно для заполнения)
        - Описание (текст произвольной длины)
    """
    code = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Код"
    )
    name = models.CharField(
        max_length=300,
        verbose_name="Наименование"
    )
    description = models.TextField(
        blank=True,
        verbose_name="Описание"
    )

    class Meta:
        verbose_name = "Справочник"
        verbose_name_plural = "Справочники"

    def __str__(self):
        return f"{self.code} - {self.name} - {self.description[:20]}..."


class RefBookVersion(models.Model):

    """
    Версия справочника:
        - Идентификатор
        - Идентификатор справочника (обязательно для заполнения)
        - Версия (строка, 50 символов, обязательно для заполнения)
        - Дата начала действия версии (дата)
    """
    refbook = models.ForeignKey(
        RefBook,
        on_delete=models.CASCADE,
        related_name='versions',
        verbose_name="Справочник"
    )

    version = models.CharField(
        max_length=50,
        verbose_name="Версия"
    )

    date = models.DateField(
        verbose_name="Дата начала действия версии"
    )

    class Meta:
        verbose_name = "Версия справочника"
        verbose_name_plural = "Версии справочника"

    def __str__(self):
        return f"{self.refbook.name} - {self.version} - {self.date}..."

class RefBookElement(models.Model):

    """
    "Элемент справочника":
        - Идентификатор
        - Идентификатор Версии справочника (обязательно для заполнения)
        - Код элемента (строка, 100 символов, обязательно для заполнения)
        - Значение элемента (строка, 300 символов, обязательно для заполнения)
    """

    version = models.ForeignKey(
        RefBookVersion,
        on_delete=models.CASCADE,
        related_name='elements',
        verbose_name="Версия справочника"
    )
    code = models.CharField(
        max_length=100,
        verbose_name="Код элемента"
    )
    value = models.CharField(
        max_length=300,
        verbose_name="Значение элемента"
    )

    class Meta:
        verbose_name = "Элемент справочника"
        verbose_name_plural = "Элементы справочника"
        unique_together = [('version', 'code')]

    def __str__(self):
        return f"{self.code} - {self.value}"