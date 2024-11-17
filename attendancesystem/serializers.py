from django.contrib.admin import action
from rest_framework import serializers, status
from django.contrib.auth.models import User, Group
from rest_framework.fields import SerializerMethodField
from rest_framework.response import Response

from attendancesystem.models import Course, Semester, Student, Class, Lecturer, CollegeDay

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['id', 'code', 'name']


class SemesterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Semester
        fields = ['id', 'year', 'semester']


class ClassSerializer(serializers.ModelSerializer):
    semester_name = serializers.CharField(source='semester.semester', read_only=True)
    semester_year = serializers.CharField(source='semester.year', read_only=True)
    course_code = serializers.CharField(source='course.code', read_only=True)
    course_name = serializers.CharField(source='course.name', read_only=True)
    lecturer_first_name = serializers.CharField(source='lecturer.user.first_name', read_only=True)
    lecturer_last_name = serializers.CharField(source='lecturer.user.last_name', read_only=True)

    class Meta:
        model = Class
        fields = ['id', 'number', 'semester', 'semester_name', 'semester_year', 'course', 'course_code', 'course_name',
                  'lecturer', 'lecturer_first_name', 'lecturer_last_name', 'students']


class CollegeDaySerializer(serializers.ModelSerializer):
    # 添加讲师和课程相关的额外字段
    lecturer_id = serializers.IntegerField(source='class_obj.lecturer.id', read_only=True)
    lecturer_first_name = serializers.CharField(source='class_obj.lecturer.user.first_name', read_only=True)
    lecturer_last_name = serializers.CharField(source='class_obj.lecturer.user.last_name', read_only=True)
    semester_name = serializers.CharField(source='class_obj.semester.semester', read_only=True)
    semester_year = serializers.CharField(source='class_obj.semester.year', read_only=True)
    course_code = serializers.CharField(source='class_obj.course.code', read_only=True)
    course_name = serializers.CharField(source='class_obj.course.name', read_only=True)


    class Meta:
        model = CollegeDay
        fields = [
            'id', 'date', 'class_obj', 'lecturer_id', 'lecturer_first_name',
            'lecturer_last_name', 'semester_name', 'semester_year', 'course_name', 'course_code', 'students'
        ]


class StudentSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email')

    class Meta:
        model = Student
        fields = ['id', 'DOB', 'first_name', 'last_name', 'username', 'email']

    def create(self, validated_data):
        # 提取嵌套的 user 數據
        user_data = validated_data.pop('user')
        dob = validated_data.get('DOB')

        # 自動生成 username，格式為 "firstnamelastnameYYYYMMDD"
        first_name = user_data.get('first_name').lower()
        last_name = user_data.get('last_name').lower()
        dob_str = dob.strftime('%Y%m%d')
        username = f"{first_name}{last_name}{dob_str}"

        # 檢查是否存在相同的 username，避免重複
        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError({"username": "Username already exists. Please use a unique combination."})

        # 創建 User 對象，並將密碼設置為 DOB
        password = dob.strftime('%Y-%m-%d')  # 將日期轉為字符串格式，例如 '1980-01-01'
        user = User.objects.create_user(username=username, password=password, **user_data)

        student_group = Group.objects.get(name="student")
        user.groups.add(student_group)

        # 創建 Lecturer 對象，並與 User 關聯
        student = Student.objects.create(user=user, **validated_data)

        return student

    def update(self, instance, validated_data):
        # 使用 .get() 获取嵌套的 user 数据，避免 KeyError
        user_data = validated_data.get('user')

        # 如果有 user 数据，则更新 User 对象的相关字段
        if user_data:
            user = instance.user
            user.first_name = user_data.get('first_name', user.first_name)
            user.last_name = user_data.get('last_name', user.last_name)
            user.email = user_data.get('email', user.email)
            user.save()

        # 更新 Lecturer 模型的相关字段
        instance.DOB = validated_data.get('DOB', instance.DOB)
        instance.save()

        return instance

    def destroy(self, request, *args, **kwargs):
        # 獲取要刪除的 Student 實例
        instance = self.get_object()

        try:
            # 獲取 Student 關聯的 User 對象
            user = instance.user

            # 先手動刪除 User 對象，這樣關聯的 Student 也會被自動刪除（反向刪除）
            user.delete()

            # 再手動刪除 Student 對象（以防萬一）
            instance.delete()

            return Response({"message": "User and related student deleted successfully."},
                            status=status.HTTP_204_NO_CONTENT)

        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            # 捕獲其他潛在的錯誤並顯示錯誤信息
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class LecturerSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email')

    class Meta:
        model = Lecturer
        fields = ['id', 'DOB', 'first_name', 'last_name', 'username', 'email']

        # 自定義 create 方法，創建 Lecturer 並將其密碼設置為 DOB，同時自動生成 username

    def create(self, validated_data):
        # 提取嵌套的 user 數據
        user_data = validated_data.pop('user')
        dob = validated_data.get('DOB')

        # 自動生成 username，格式為 "firstnamelastnameYYYYMMDD"
        first_name = user_data.get('first_name').lower()
        last_name = user_data.get('last_name').lower()
        dob_str = dob.strftime('%Y%m%d')
        username = f"{first_name}{last_name}{dob_str}"

        # 檢查是否存在相同的 username，避免重複
        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError(
                {"username": "Username already exists. Please use a unique combination."})

        # 創建 User 對象，並將密碼設置為 DOB
        password = dob.strftime('%Y-%m-%d')  # 將日期轉為字符串格式，例如 '1980-01-01'
        user = User.objects.create_user(username=username, password=password, **user_data)

        lecturer_group = Group.objects.get(name="lecturer")
        user.groups.add(lecturer_group)

        # 創建 Lecturer 對象，並與 User 關聯
        lecturer = Lecturer.objects.create(user=user, **validated_data)

        return lecturer

    # 自定義 update 方法，實現同時更新 Lecturer 和 User
    def update(self, instance, validated_data):
        # 使用 .get() 获取嵌套的 user 数据，避免 KeyError
        user_data = validated_data.get('user')

        # 如果有 user 数据，则更新 User 对象的相关字段
        if user_data:
            user = instance.user
            user.first_name = user_data.get('first_name', user.first_name)
            user.last_name = user_data.get('last_name', user.last_name)
            user.email = user_data.get('email', user.email)
            user.save()

        # 更新 Lecturer 模型的相关字段
        instance.DOB = validated_data.get('DOB', instance.DOB)
        instance.save()

        return instance

    # 刪除User as well
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        # 先获取关联的 User 实例
        user = instance.user

        # 删除 Lecturer 实例
        self.perform_destroy(instance)

        # 删除关联的 User 实例
        if user:
            user.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class UserSerializer(serializers.ModelSerializer):
    user_group = SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'password', 'user_group']

        extra_kwargs = {
            'password': {
                'write_only': True,
                'required': True
            },
            'username': {'read_only': True},
        }

    def get_user_group(self, obj):
        # 假设每个用户只有一个组，返回第一个组的名称
        group = obj.groups.first()  # 获取第一个组
        return group.name if group else None
