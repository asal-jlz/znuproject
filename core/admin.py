from django.contrib import admin
from .models import Student, Professor, Conference, Article, News, Sponsor, Topic, FAQ, Speaker

admin.site.register(Student)
admin.site.register(Professor)
admin.site.register(Conference)
admin.site.register(Article)
admin.site.register(Sponsor)
admin.site.register(Topic)
admin.site.register(FAQ)
admin.site.register(Speaker)
admin.site.register(News)