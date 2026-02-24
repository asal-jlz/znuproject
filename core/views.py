from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Article, Professor, Speaker, Student, Conference, News, Sponsor, Topic, FAQ, Payment
from .forms import ArticleUploadForm
from .forms import SignUpForm
from .forms import PaymentForm
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
import google.generativeai as genai


genai.configure(api_key="YOUR_GEMINI_API_KEY")

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            role = form.cleaned_data.get('role')
            # ایجاد پروفایل بر اساس نقش
            if role == 'student':
                Student.objects.create(user=user)
            else:
                Professor.objects.create(user=user)
            return redirect('login')
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})

def home(request):
    conf = Conference.objects.first()
    news_list = News.objects.all().order_by('-created_at')
    sponsors = Sponsor.objects.all()
    topics = Topic.objects.all()
    faqs = FAQ.objects.all() 
    speakers = Speaker.object.all() # گرفتن سوالات
    return render(request, 'core/home.html', {
        'conference': conf,
        'news': news_list,
        'sponsors': sponsors,
        'topics': topics,
        'faqs': faqs,
        'speakers': speakers,
    })

def scientific_committee(request):
    committee = Professor.objects.filter(is_scientific_committee=True).order_by('-rank')
    return render(request, 'core/committee.html', {'committee': committee})

def conference_detail(request, pk):
    conference = get_object_or_404(Conference, pk=pk)
    professors = Professor.objects.all() 
    return render(request, 'core/conference_detail.html', {
        'conference': conference,
        'professors': professors
    })   


@login_required
def dashboard(request):
    # ۱. اگر یوزر ادمین (Superuser) بود، بفرستش به پنل مدیریت اصلی
    if request.user.is_superuser:
        return redirect('/admin/')

    # ۲. چک کردن نقش استاد
    if hasattr(request.user, 'professor_profile'):
        professor = request.user.professor_profile
        articles = Article.objects.filter(advisor=professor)
        return render(request, 'core/professor_dashboard.html', {'articles': articles})
    
    # ۳. چک کردن نقش دانشجو
    elif hasattr(request.user, 'student_profile'):
        student = request.user.student_profile
        articles = Article.objects.filter(student=student)
        return render(request, 'core/student_dashboard.html', {'articles': articles})
    
    # ۴. اگر یوزر معمولی بود که هنوز پروفایل نساخته
    return render(request, 'core/home.html', {'msg': 'پروفایل شما تکمیل نشده است.'})

@login_required
def update_article_status(request, article_id, new_status):
    article = get_object_or_404(Article, id=article_id)
    
    # فقط استادی که راهنمای این مقاله است دسترسی داشته باشد
    if request.user.professor_profile == article.advisor:
        article.status = new_status
        
        # اگر استاد نظری در فرم فرستاده بود، ذخیره شود
        comment = request.POST.get('comment')
        if comment:
            article.professor_comment = comment
            
        article.save()
        messages.success(request, f"وضعیت مقاله به '{article.get_status_display()}' تغییر یافت.")
    else:
        messages.error(request, "شما اجازه دسترسی به این مقاله را ندارید.")
        
    return redirect('dashboard')

@login_required # فقط کسانی که وارد شده‌اند بتوانند آپلود کنند
def upload_article(request):
    if request.method == 'POST':
        form = ArticleUploadForm(request.POST, request.FILES)
        if form.is_valid():
            article = form.save(commit=False)
            # اینجا باید چک کنیم که کاربر حتماً پروفایل دانشجویی داشته باشد
            article.student = request.user.student_profile 
            article.save()
            return render(request, 'core/upload_success.html')
    else:
        form = ArticleUploadForm()
    return render(request, 'core/upload_article.html', {'form': form})     

@login_required
def update_article_status(request, article_id, new_status):
    if request.method == 'POST':
        article = get_object_or_404(Article, id=article_id)
        # امنیت: فقط استادی که راهنما هست بتواند تغییر دهد
        if Professor.objects.filter(user=request.user).exists() and article.advisor.user == request.user:
            article.status = new_status
            article.save()
    return redirect('dashboard')    

def professor_profile(request, pk):
    prof = get_object_or_404(Professor, pk=pk)
    return render(request, 'core/professor_profile.html', {'prof': prof})    

def home(request):
    conf = Conference.objects.first() # اولین کنفرانس را می‌گیریم
    news_list = News.objects.all().order_by('-created_at')
    return render(request, 'core/home.html', {
        'conference': conf, # این برای سایدبار base.html حیاتی است
        'news': news_list
    })
    
def contact_us(request):
    return render(request, 'core/contact.html')    

def news_detail(request, pk):
    item = get_object_or_404(News, pk=pk)
    # برای سایدبار دوباره کنفرانس را می‌فرستیم
    conf = Conference.objects.first()
    return render(request, 'core/news_detail.html', {'news_item': item, 'conference': conf})      

def global_search(request):
    query = request.GET.get('q')
    results_news = []
    results_topics = []
    results_articles = []

    if query:
        # جستجو در اخبار (عنوان و متن)
        results_news = News.objects.filter(
            Q(title__icontains=query) | Q(content__icontains=query)
        )
        # جستجو در محورهای کنفرانس
        results_topics = Topic.objects.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )
        # جستجو در مقالات (اگر کاربر لاگین بود، مقالات خودش را ببیند)
        if request.user.is_authenticated:
            results_articles = Article.objects.filter(
                Q(title__icontains=query) | Q(tracking_code__icontains=query)
            ).filter(Q(student__user=request.user) | Q(advisor__user=request.user))

    context = {
        'query': query,
        'news': results_news,
        'topics': results_topics,
        'articles': results_articles,
    }
    return render(request, 'core/search_results.html', context)

import google.generativeai as genai
from django.http import JsonResponse

# کد کپی شده از گوگل رو اینجا بذار
GOOGLE_API_KEY = "AIzaSyDUhmPSHTyxRyAI5U_TciwSXS437ZIX6iQ" 
genai.configure(api_key=GOOGLE_API_KEY)

def ai_assistant_api(request):
    user_msg = request.GET.get('msg', '')
    
    if user_msg:
        try:
            # استفاده از مدل جدیدتر و سریع‌تر
            model = genai.GenerativeModel('gemini-1.5-flash') 
            
            # کانتکست دادن به هوش مصنوعی به زبان فارسی
            context = (
                "تو دستیار هوشمند کنفرانس ZNU-ICEE 2026 در دانشگاه زنجان هستی. "
                "باید به سوالات کاربران در مورد مهلت ارسال مقالات، نحوه ثبت نام و محورهای کنفرانس "
                "با لحنی محترمانه و به زبان فارسی پاسخ دهی."
            )
            
            response = model.generate_content(f"{context}\n\nسوال کاربر: {user_msg}")
            
            return JsonResponse({'reply': response.text})
        
        except Exception as e:
            print(f"Error AI: {e}") # این خط رو توی ترمینال چک کن
            return JsonResponse({'reply': "در حال حاضر ارتباطم با سرور هوش مصنوعی قطع شده، لطفاً چند لحظه دیگه امتحان کن."})
    
    return JsonResponse({'reply': "چطور می‌تونم کمکت کنم؟"})

def upload_receipt(request, article_id):
    article = get_object_or_404(Article, id=article_id)
    
    # امنیت: چک کردن اینکه مقاله متعلق به همین کاربر باشه
    if article.student.user != request.user:
        return redirect('dashboard')

    if request.method == 'POST':
        form = PaymentForm(request.POST, request.FILES)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.student = article.student
            payment.article = article
            payment.save()
            return redirect('dashboard')
    else:
        form = PaymentForm()
    
    return render(request, 'core/upload_receipt.html', {'form': form, 'article': article})    