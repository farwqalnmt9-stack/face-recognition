from django.db import models


class TimestampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Product(TimestampedModel):
    slug = models.SlugField(unique=True)
    name_ar = models.CharField("الاسم بالعربية", max_length=120)
    name_en = models.CharField("الاسم بالإنكليزية", max_length=120)
    summary_ar = models.TextField("الوصف المختصر")
    summary_en = models.TextField("English summary", blank=True)
    category = models.CharField("التصنيف", max_length=80, default="Business software")
    accent = models.CharField("لون العرض", max_length=20, default="#1ca84b")
    is_active = models.BooleanField("نشط", default=True)

    class Meta: verbose_name = "منتج"; verbose_name_plural = "المنتجات"
    def __str__(self): return self.name_ar


class Customer(TimestampedModel):
    name = models.CharField("اسم العميل", max_length=160)
    contact_name = models.CharField("جهة الاتصال", max_length=120, blank=True)
    phone = models.CharField("الهاتف", max_length=30, blank=True)
    city = models.CharField("المدينة", max_length=80, blank=True)

    class Meta: verbose_name = "عميل"; verbose_name_plural = "العملاء"
    def __str__(self): return self.name


class License(TimestampedModel):
    class Status(models.TextChoices): ACTIVE = "active", "نشط"; TRIAL = "trial", "تجريبي"; EXPIRED = "expired", "منتهي"; SUSPENDED = "suspended", "موقوف"
    key = models.CharField("مفتاح التفعيل", max_length=80, unique=True)
    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name="المنتج")
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, verbose_name="العميل")
    status = models.CharField("الحالة", max_length=16, choices=Status.choices, default=Status.TRIAL)
    expires_at = models.DateField("تاريخ الانتهاء", null=True, blank=True)

    class Meta: verbose_name = "ترخيص"; verbose_name_plural = "التراخيص"
    def __str__(self): return self.key


class Partner(TimestampedModel):
    name = models.CharField("اسم الوكيل", max_length=160)
    region = models.CharField("المنطقة", max_length=100)
    commission_rate = models.DecimalField("العمولة %", max_digits=5, decimal_places=2, default=0)
    is_active = models.BooleanField("نشط", default=True)

    class Meta: verbose_name = "وكيل"; verbose_name_plural = "الوكلاء"
    def __str__(self): return self.name


class Lead(TimestampedModel):
    class Stage(models.TextChoices): LEAD = "lead", "عميل محتمل"; CONTACTED = "contacted", "تم التواصل"; DEMO = "demo", "عرض تجريبي"; CUSTOMER = "customer", "عميل"
    name = models.CharField("الاسم", max_length=120)
    phone = models.CharField("الهاتف", max_length=30)
    stage = models.CharField("المرحلة", max_length=16, choices=Stage.choices, default=Stage.LEAD)
    notes = models.TextField("ملاحظات", blank=True)

    class Meta: verbose_name = "فرصة بيع"; verbose_name_plural = "فرص البيع"
    def __str__(self): return self.name


class MediaAsset(TimestampedModel):
    class Type(models.TextChoices): IMAGE = "image", "صورة"; VIDEO = "video", "فيديو"; FILE = "file", "ملف"
    class Placement(models.TextChoices):
        HOME_HERO = "home_hero", "صورة الواجهة الرئيسية"
        HOME_SUCCESS = "home_success", "صورة قصة النجاح"
        LOGIN_VISUAL = "login_visual", "صورة صفحة تسجيل الدخول"

    title = models.CharField("العنوان", max_length=160)
    type = models.CharField("النوع", max_length=10, choices=Type.choices)
    file = models.FileField("رفع الملف", upload_to="kajo-media/%Y/%m/", blank=True)
    file_url = models.URLField("رابط الملف", blank=True)
    placement = models.CharField("مكان الظهور", max_length=80, choices=Placement.choices, blank=True, help_text="اختر مكان الصورة، وسيظهر آخر ملف نشط مرفوع في هذا المكان.")
    alt_text = models.CharField("النص البديل", max_length=200, blank=True)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="المنتج المرتبط")
    is_active = models.BooleanField("ظاهر", default=True)

    class Meta: verbose_name = "وسيط"; verbose_name_plural = "الوسائط"
    def __str__(self): return self.title

    @property
    def source_url(self):
        return self.file.url if self.file else self.file_url


class SiteSection(TimestampedModel):
    key = models.SlugField("معرّف القسم", unique=True, help_text="معرّف ثابت يستخدمه القالب، مثل home_hero")
    page = models.CharField("الصفحة", max_length=80, default="home")
    eyebrow_ar = models.CharField("العنوان الصغير بالعربية", max_length=160, blank=True)
    eyebrow_en = models.CharField("العنوان الصغير بالإنكليزية", max_length=160, blank=True)
    title_ar = models.CharField("العنوان بالعربية", max_length=240)
    title_en = models.CharField("العنوان بالإنكليزية", max_length=240)
    accent_ar = models.CharField("النص المميز بالعربية", max_length=160, blank=True)
    accent_en = models.CharField("النص المميز بالإنكليزية", max_length=160, blank=True)
    body_ar = models.TextField("المحتوى بالعربية", blank=True)
    body_en = models.TextField("المحتوى بالإنكليزية", blank=True)
    order = models.PositiveSmallIntegerField("الترتيب", default=0)
    is_visible = models.BooleanField("إظهار القسم", default=True)

    class Meta:
        verbose_name = "قسم صفحة"
        verbose_name_plural = "أقسام الصفحات"
        ordering = ("page", "order")

    def __str__(self):
        return f"{self.page} — {self.title_ar}"


class KeywordMetric(TimestampedModel):
    keyword = models.CharField("الكلمة المفتاحية", max_length=180, unique=True)
    monthly_volume = models.PositiveIntegerField("حجم البحث الشهري", default=0)
    difficulty = models.PositiveSmallIntegerField("صعوبة المنافسة", default=0)
    rank = models.PositiveSmallIntegerField("الترتيب الحالي", null=True, blank=True)

    class Meta: verbose_name = "كلمة مفتاحية"; verbose_name_plural = "الكلمات المفتاحية"
    def __str__(self): return self.keyword
