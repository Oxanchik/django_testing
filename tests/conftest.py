import pytest
from rest_framework.test import APIClient
from model_bakery import baker

from students.models import Course, Student


@pytest.fixture
def client():
    """Тестовый клиент DRF."""
    return APIClient()


@pytest.fixture
def course_factory():
    """Фабрика курсов."""
    def factory(*args, **kwargs):
        return baker.make(Course, *args, **kwargs)
    return factory


@pytest.fixture
def student_factory():
    """Фабрика студентов."""
    def factory(*args, **kwargs):
        return baker.make(Student, *args, **kwargs)
    return factory