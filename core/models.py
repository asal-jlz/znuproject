from django.db import models
from django.contrib.auth.models import User
import uuid

# پروفایل دانشجو
class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    student_number = models.CharField(max_length=20, verbose_name="شماره دانشجویی", null=True, blank=True)
    field_of_study = models.CharField(max_length=100, verbose_name="رشته تحصیلی")

    def __str__(self):
        return f"دانشجو: {self.user.get_full_name()}"

class Professor(models.Model):
    RANK_CHOICES = [
        ('prof', 'استاد تمام'),
        ('assoc_prof', 'دانشیار'),
        ('assist_prof', 'استادیار'),
        ('lecturer', 'مربی'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='professor_profile')
    rank = models.CharField(max_length=20, choices=RANK_CHOICES, verbose_name="رتبه علمی", default='assist_prof')
    university = models.CharField(max_length=200, verbose_name="دانشگاه", blank=True)
    is_scientific_committee = models.BooleanField(default=False, verbose_name="عضو کمیته علمی")
    expertise = models.CharField(max_length=200, verbose_name="تخصص")
    bio = models.TextField(verbose_name="بیوگرافی", blank=True)
    image = models.ImageField(upload_to='professors/', null=True, blank=True)

    def __str__(self):
        return f"{self.get_rank_display()} {self.user.get_full_name()}"

class Conference(models.Model):
    title = models.CharField(max_length=200)
    location = models.CharField(max_length=255)
    hold_date = models.DateField()
    poster = models.ImageField(upload_to='posters/')
    # فیلدهای مشابه ICEE
    topics = models.TextField(verbose_name="محورهای کنفرانس", help_text="هر محور را با خط تیره جدا کنید", null=True, blank=True)
    submission_deadline = models.DateField(null=True, blank=True, verbose_name="مهلت ارسال مقاله")
    acceptance_notification = models.DateField(null=True, blank=True, verbose_name="اعلام نتایج")
    registration_deadline = models.DateField(null=True, blank=True, verbose_name="ثبت‌نام نهایی")
    guide_file = models.FileField(upload_to='guides/', null=True, blank=True, verbose_name="فایل راهنمای نگارش")

    def __str__(self):
        return self.title

class News(models.Model):
    conference = models.ForeignKey(Conference, on_delete=models.CASCADE, related_name='news')
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "News"
    def __str__(self):
        return self.title    

# مدل مقاله (حالا به دانشجو و استاد وصل می‌شود)
class Article(models.Model):
    STATUS_CHOICES = [
        ('pending', 'در حال بررسی'),
        ('revised', 'نیاز به اصلاح'),
        ('accepted', 'پذیرفته شده'),
        ('rejected', 'مردود'),
    ]
    
    title = models.CharField(max_length=255)
    # اتصال به مدل دانشجو
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='articles')
    # اتصال به مدل استاد (به عنوان راهنما یا داور)
    advisor = models.ForeignKey(Professor, on_delete=models.SET_NULL, null=True, related_name='advised_articles')
    file = models.FileField(upload_to='articles/')
    status = models.CharField(
        max_length=20, 
        choices=[('pending', 'در حال داوری'), ('accepted', 'پذیرفته شده'), ('rejected', 'نیاز به اصلاح')],
        default='pending'
    )
    professor_comment = models.TextField(verbose_name="نظر استاد", blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    tracking_code = models.CharField(
        max_length=12, 
        unique=True, 
        editable=False, 
        verbose_name="کد رهگیری",
        null=True, # این را اضافه کن
        blank=True # این را اضافه کن
    )

    def save(self, *args, **kwargs):
        if not self.tracking_code:
            # ایجاد یک کد تصادفی شبیه ZNU-12345
            self.tracking_code = "ZNU-" + str(uuid.uuid4().hex[:5].upper())
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

class Sponsor(models.Model):
    name = models.CharField(max_length=200, verbose_name="نام سازمان/شرکت")
    logo = models.ImageField(upload_to='sponsors/', verbose_name="لوگو")
    link = models.URLField(blank=True, null=True, verbose_name="لینک وب‌سایت حامی")

    class Meta:
        verbose_name = "حامی"
        verbose_name_plural = "حامیان"

    def __str__(self):
        return self.name    

class Topic(models.Model):
    title = models.CharField(max_length=100, verbose_name="عنوان محور (مثلاً هوش مصنوعی)")
    icon_code = models.CharField(max_length=50, verbose_name="کد آیکون (مثلاً cpu یا network)", help_text="از نام‌های Lucide یا Emoji استفاده کنید")
    description = models.TextField(verbose_name="توضیحات کوتاه", blank=True)

    class Meta:
        verbose_name = "محور تخصصی"
        verbose_name_plural = "محورهای تخصصی"

    def __str__(self):
        return self.title    

class FAQ(models.Model):
    question = models.CharField(max_length=255, verbose_name="سوال")
    answer = models.TextField(verbose_name="پاسخ")

    class Meta:
        verbose_name = "سوال متداول"
        verbose_name_plural = "سوالات متداول"

    def __str__(self):
        return self.question     

class Speaker(models.Model):
    name = models.CharField(max_length=200, verbose_name="نام سخنران")
    designation = models.CharField(max_length=200, verbose_name="عنوان علمی/شغلی")
    university = models.CharField(max_length=200, verbose_name="دانشگاه/موسسه")
    image = models.ImageField(upload_to='speakers/', verbose_name="تصویر")
    topic = models.CharField(max_length=255, verbose_name="موضوع سخنرانی")

    def __str__(self):
        return self.name    

class Payment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'در انتظار بررسی'),
        ('verified', 'تایید شده'),
        ('rejected', 'رد شده'),
    ]
    student = models.ForeignKey('Student', on_delete=models.CASCADE)
    article = models.OneToOneField('Article', on_delete=models.CASCADE)
    amount = models.BigIntegerField(verbose_name="مبلغ (ریال)")
    receipt_image = models.ImageField(upload_to='receipts/', verbose_name="تصویر فیش")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    admin_description = models.TextField(blank=True, null=True, verbose_name="توضیحات مدیر")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"فیش {self.student.user.get_full_name()} - مقاله {self.article.tracking_code}"                     