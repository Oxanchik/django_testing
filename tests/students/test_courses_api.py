import pytest

from students.models import Course, Student


@pytest.mark.django_db
def test_retrieve_course(client, course_factory):
    course = course_factory()

    url = f"/api/v1/courses/{course.id}/"
    response = client.get(url)

    assert response.status_code == 200
    assert response.data["id"] == course.id
    assert response.data["name"] == course.name


@pytest.mark.django_db
def test_list_courses(client, course_factory):
    course_factory(_quantity=5)

    url = "/api/v1/courses/"
    response = client.get(url)

    assert response.status_code == 200
    assert len(response.data) == 5
    returned_ids = {item["id"] for item in response.data}
    expected_ids = set(Course.objects.values_list("id", flat=True))
    assert returned_ids == expected_ids


@pytest.mark.django_db
def test_filter_courses_by_id(client, course_factory):
    courses = course_factory(_quantity=5)
    target = courses[0]

    url = "/api/v1/courses/"
    response = client.get(url, data={"id": target.id})

    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]["id"] == target.id


@pytest.mark.django_db
def test_filter_courses_by_name(client, course_factory):
    course_factory(name="Python")
    course_factory(name="Django")
    course_factory(name="Django REST")

    url = "/api/v1/courses/"
    response = client.get(url, data={"name": "Django"})

    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]["name"] == "Django"


@pytest.mark.django_db
def test_create_course(client):
    payload = {"name": "Новый курс"}

    url = "/api/v1/courses/"
    response = client.post(url, data=payload)

    assert response.status_code == 201
    assert Course.objects.filter(name="Новый курс").exists()
    assert response.data["name"] == "Новый курс"


@pytest.mark.django_db
def test_update_course(client, course_factory):
    course = course_factory(name="Старое имя")

    payload = {"name": "Новое имя"}
    url = f"/api/v1/courses/{course.id}/"
    response = client.patch(url, data=payload)

    assert response.status_code == 200
    course.refresh_from_db()
    assert course.name == "Новое имя"
    assert response.data["name"] == "Новое имя"


@pytest.mark.django_db
def test_delete_course(client, course_factory):
    course = course_factory()
    course_id = course.id

    url = f"/api/v1/courses/{course_id}/"
    response = client.delete(url)

    assert response.status_code == 204
    assert not Course.objects.filter(id=course_id).exists()


@pytest.mark.django_db
@pytest.mark.parametrize(
    "max_students, students_count, expected_status",
    [
        (20, 1, 201),
        (2, 3, 400),
        (0, 1, 400),
    ],
)
def test_max_students_per_course(
    client,
    settings,
    student_factory,
    max_students,
    students_count,
    expected_status,
):
    settings.MAX_STUDENTS_PER_COURSE = max_students

    students = student_factory(_quantity=students_count)
    student_ids = [s.id for s in students]

    payload = {"name": "Курс с лимитом", "students": student_ids}
    url = "/api/v1/courses/"
    response = client.post(url, data=payload, format="json")

    assert response.status_code == expected_status
