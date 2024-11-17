from rest_framework import permissions


# 只有admin可以進入###
class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.groups.filter(name='admin').exists():
            return True
        return False


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    管理员具有完全权限，其他人只允许只读访问
    """

    def has_permission(self, request, view):
        # 如果用户是管理员，允许所有操作
        if request.user.is_authenticated and request.user.groups.filter(name='admin').exists():
            return True

        # 允许所有其他用户进行只读操作
        if request.method in permissions.SAFE_METHODS:
            return True

        # 对于非管理员用户，非只读请求拒绝访问
        return False


class IsLecturerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # 如果请求方法是安全的，则允许
        if request.method in permissions.SAFE_METHODS:
            if request.user.is_authenticated and request.user.groups.filter(name='admin').exists():
                return True

                # 如果用户是讲师，允许访问其教授的班级
            if request.user.is_authenticated and request.user.groups.filter(name='lecturer').exists() :
                return obj.class_obj.lecturer.user == request.user

                # 如果用户是学生，只允许访问他们注册的班级的 CollegeDay
            if hasattr(request.user, 'student'):
                # 检查该学生是否在该课程中
                return request.user.student in obj.class_obj.students.all()

        # 如果用户是管理员，允许所有操作
        if request.user.is_authenticated and request.user.groups.filter(name='admin').exists():
            return True

        # 仅允许该课程的讲师修改对象
        return obj.class_obj.lecturer.user == request.user


class IsLecturerInClass(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # 如果请求方法是安全的，则允许
        if request.method in permissions.SAFE_METHODS:
            return True

        # 如果用户是管理员，允许所有操作
        if request.user.is_authenticated and request.user.groups.filter(name='admin').exists():
            return True

        # 仅允许该课程的讲师修改对象
        return obj.lecturer.user == request.user


def isAdmin(request):
    if 'admin' in request.user.groups.all().values_list('name', flat=True):
        return True
    return False


def isLecturer(request):
    if 'admin' in request.user.groups.all().values_list('name', flat=True):
        return True
    return False
