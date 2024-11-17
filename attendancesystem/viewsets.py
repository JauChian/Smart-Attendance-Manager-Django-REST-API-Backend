from django.contrib.auth.models import User
from rest_framework import viewsets, permissions, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from attendancesystem.models import Course, Semester, Class, CollegeDay, Student, Lecturer
from attendancesystem.permissions import IsAdmin, isAdmin, IsLecturerOrReadOnly, IsLecturerInClass, IsAdminOrReadOnly
from attendancesystem.serializers import UserSerializer, CourseSerializer, SemesterSerializer, ClassSerializer, \
    CollegeDaySerializer, StudentSerializer, LecturerSerializer
from django_filters.rest_framework import DjangoFilterBackend


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminOrReadOnly]


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAdminOrReadOnly]


class SemesterViewSet(viewsets.ModelViewSet):
    queryset = Semester.objects.all()
    serializer_class = SemesterSerializer
    permission_classes = [IsAdminOrReadOnly]


class ClassViewSet(viewsets.ModelViewSet):
    queryset = Class.objects.all()
    serializer_class = ClassSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['course__name']
    permission_classes = [IsLecturerInClass]


class CollegeDayViewSet(viewsets.ModelViewSet):
    queryset = CollegeDay.objects.all()
    serializer_class = CollegeDaySerializer
    permission_classes = [IsLecturerOrReadOnly]

    def get_queryset(self):
        user = self.request.user

        # 如果用户是学生，只返回该学生注册的班级的 CollegeDay
        if hasattr(user, 'student'):
            return CollegeDay.objects.filter(class_obj__students=user.student)

        # 如果用户是讲师，只返回该讲师负责的班级的 CollegeDay
        if hasattr(user, 'lecturer'):
            return CollegeDay.objects.filter(class_obj__lecturer=user.lecturer)

        # 如果用户是管理员，返回所有 CollegeDay
        return CollegeDay.objects.all()

    def create(self, request, *args, **kwargs):
        # 如果用户已认证且是管理员
        if request.user.is_authenticated and isAdmin(request):
            # 创建一个可修改的副本
            data = request.data.copy()

            # 打印请求数据（调试用）
            print(data)

            # 调用父类的 create 方法来执行实际的创建逻辑
            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

        # 如果用户不是管理员，返回 403 禁止访问错误
        return Response("You have to be an admin first", status=status.HTTP_403_FORBIDDEN)

    def destroy(self, request, *args, **kwargs):
        # 如果用户已认证且是管理员
        if request.user.is_authenticated and isAdmin(request):
            # 调用父类的 destroy 方法来执行删除逻辑
            return super().destroy(request, *args, **kwargs)

        # 如果用户不是管理员，返回 403 禁止访问错误
        return Response({"detail": "You have to be an admin to delete this."}, status=status.HTTP_403_FORBIDDEN)

class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [IsAdminOrReadOnly]


class LecturerViewSet(viewsets.ModelViewSet):
    queryset = Lecturer.objects.all()
    serializer_class = LecturerSerializer
    permission_classes = [IsAdminOrReadOnly]


