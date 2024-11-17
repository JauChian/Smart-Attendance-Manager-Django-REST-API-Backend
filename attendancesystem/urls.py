from rest_framework.routers import DefaultRouter
from attendancesystem.viewsets import UserViewSet, StudentViewSet, LecturerViewSet, SemesterViewSet, CourseViewSet, ClassViewSet, CollegeDayViewSet

router = DefaultRouter()
router.register('semesters',SemesterViewSet, 'semesters')
router.register('courses', CourseViewSet, 'courses')
router.register('students',StudentViewSet, 'students')
router.register('lecturers',LecturerViewSet, 'lecturers')
router.register('classes',ClassViewSet, 'classes')
router.register('users',UserViewSet, 'users')
router.register('collegeDays',CollegeDayViewSet, 'collegeDays')
urlpatterns = router.urls