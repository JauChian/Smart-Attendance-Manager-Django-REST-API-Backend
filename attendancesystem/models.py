from django.db import models
from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse


# Lecturer模型 6個properties
class Lecturer(models.Model):
    DOB = models.DateField()
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)

    def delete(self, *args, **kwargs):
        # 删除关联的 User 对象
        if self.user:
            self.user.delete()
        super().delete(*args, **kwargs)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"

    def get_absolute_url(self):
        return f'/lecturer_detail/{self.id}/'


# Semester模型
class Semester(models.Model):
    year = models.IntegerField()
    semester = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.semester} {self.year}"  # 返回学期的名称和年份，例如“Spring 2023”

    def get_absolute_url(self):
        return reverse('semester_detail', args=[str(self.id)])


# Course模型
class Course(models.Model):
    code = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    # 跟semester多對多的關係, related_name='courses', 這樣可以反向查詢 Semester有多少 courses
    semesters = models.ManyToManyField(Semester, related_name='courses', blank=True)

    def __str__(self):
        return f"{self.code} - {self.name}"

    def get_absolute_url(self):
        return f'/course_detail/{self.id}/'


# Student模型 5個properties
class Student(models.Model):
    DOB = models.DateField()
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)

    def delete(self, *args, **kwargs):
        # 删除关联的 User 对象
        if self.user:
            self.user.delete()
        super().delete(*args, **kwargs)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"

    def get_absolute_url(self):
        return f'/student_detail/{self.id}/'


# Class模型
class Class(models.Model):
    number = models.IntegerField()
    # 當設置ForeignKey的時候, Django 會自動生成一個反向查詢名稱，格式是 模型名小寫_set. ie. course_set, semester_set, lecturer_set
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    lecturer = models.ForeignKey(Lecturer, on_delete=models.CASCADE)  # 不能為空
    # 可以反向搜尋學生在的class
    students = models.ManyToManyField(Student, related_name='enrolled_classes', blank=True)

    # enrollments = models.ManyToManyField(Enrollment, through='Enrollment', blank=True)

    # 返回班级编号、课程名称和学期
    def __str__(self):
        return f"{self.course.code} {self.course.name} ({self.semester.semester} {self.semester.year})- Class {self.number}  "

    def get_absolute_url(self):
        return f'/class_detail/{self.id}/'

class CollegeDay(models.Model):
    date = models.DateTimeField(blank=True, null=True)
    class_obj = models.ForeignKey(Class, on_delete=models.CASCADE, null=True, blank=True)  # 设置为可空
    # 當天來上課的學生 多對多的關係, related_name='attended_classes' 可以透過學生來查 所有attended classes
    students = models.ManyToManyField(Student, related_name='attended_classes', blank=True)
    #classes = models.ManyToManyField(Class, related_name='college_days', blank=True)

    def __str__(self):
        return f"{self.class_obj.course.code} {self.class_obj.course.name} Class {self.class_obj.number} on {self.date}"  # 返回班级编号和日期

    def get_absolute_url(self):
        return reverse('college_day_detail', args=[str(self.id)])




