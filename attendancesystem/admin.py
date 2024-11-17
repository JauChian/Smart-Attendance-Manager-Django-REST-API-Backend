from django.contrib import admin
from attendancesystem.models import Semester, Course, Class, CollegeDay, Student, Lecturer

# Register your models here.
admin.site.register(Semester)
admin.site.register(Course)
admin.site.register(Class)
admin.site.register(CollegeDay)
admin.site.register(Lecturer)
admin.site.register(Student)