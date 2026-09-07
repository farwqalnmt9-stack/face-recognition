from django.db import migrations, models


def seed_sections(apps, schema_editor):
    SiteSection = apps.get_model("web", "SiteSection")
    sections = [
        ("home-hero", 10, "هندسة برمجية تواكب أعمالك", "Engineering software built for your business", "حوّل إدارة عملك", "Turn business management", "إلى وضوحٍ ونمو.", "into clarity and growth.", "من المحاسبة إلى إدارة العيادات، تصنع كاجو أنظمة أكثر بساطةً وأعلى موثوقية للشركات الطموحة.", "From accounting to clinic management, Kajo builds simpler, more dependable systems for ambitious companies."),
        ("home-solutions", 20, "حلول مصممة حولك", "Solutions designed around you", "نحن لا نبيع برامج.", "We do not just sell software.", "نصمّم راحة البال.", "We design peace of mind.", "بنية مرنة، لوحات واضحة، ودعم حقيقي. كل ما تحتاجه لتتخذ القرار الصحيح في الوقت الصحيح.", "Flexible architecture, clear dashboards and real support for every confident decision."),
        ("home-products", 30, "منتجاتنا", "Our products", "برامج تعمل", "Software that works", "كما تفكّر أنت.", "the way you think.", "منتجات مترابطة وقابلة للتوسع مع نمو أعمالك.", "Connected products designed to scale with your business."),
        ("home-control", 40, "تحكم كامل", "Complete control", "كل التفاصيل.", "Every detail.", "في مكانها.", "In its place.", "أدر النصوص والصور والمنتجات والعملاء والتراخيص من مركز واحد.", "Manage text, images, products, customers and licenses from one place."),
        ("home-success", 50, "أثر يمكن قياسه", "Measurable impact", "من فوضى الأرقام", "From scattered numbers", "إلى قرارٍ واثق.", "to a confident decision.", "قصص عملاء حقيقية ونتائج يمكن قياسها.", "Real customer stories with measurable results."),
        ("home-partners", 60, "شبكة كاجو", "Kajo network", "ننمو مع", "We grow with", "شركائنا.", "our partners.", "انضم إلى شبكة الوكلاء وقدم حلول كاجو في منطقتك.", "Join our partner network and bring Kajo solutions to your region."),
        ("home-demo", 70, "خطوتك التالية", "Your next step", "دعنا نبني وضوحاً", "Let us build clarity", "لعملك.", "for your business.", "احجز عرضاً مخصصاً واكتشف كيف يمكن لكاجو أن تدفع أعمالك إلى الأمام.", "Book a tailored demo and discover how Kajo can move your business forward."),
    ]
    for key, order, ear, een, tar, ten, aar, aen, bar, ben in sections:
        SiteSection.objects.update_or_create(key=key, defaults={"page": "home", "order": order, "eyebrow_ar": ear, "eyebrow_en": een, "title_ar": tar, "title_en": ten, "accent_ar": aar, "accent_en": aen, "body_ar": bar, "body_en": ben, "is_visible": True})


class Migration(migrations.Migration):
    dependencies = [("web", "0002_product_showcase_fields")]
    operations = [
        migrations.AddField(model_name="mediaasset", name="file", field=models.FileField(blank=True, upload_to="kajo-media/%Y/%m/", verbose_name="رفع الملف")),
        migrations.AddField(model_name="mediaasset", name="placement", field=models.CharField(blank=True, help_text="مثال: home_hero أو login_visual", max_length=80, verbose_name="مكان الظهور")),
        migrations.AddField(model_name="mediaasset", name="is_active", field=models.BooleanField(default=True, verbose_name="ظاهر")),
        migrations.CreateModel(name="SiteSection", fields=[("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")), ("created_at", models.DateTimeField(auto_now_add=True)), ("updated_at", models.DateTimeField(auto_now=True)), ("key", models.SlugField(help_text="معرّف ثابت يستخدمه القالب، مثل home_hero", unique=True, verbose_name="معرّف القسم")), ("page", models.CharField(default="home", max_length=80, verbose_name="الصفحة")), ("eyebrow_ar", models.CharField(blank=True, max_length=160, verbose_name="العنوان الصغير بالعربية")), ("eyebrow_en", models.CharField(blank=True, max_length=160, verbose_name="العنوان الصغير بالإنكليزية")), ("title_ar", models.CharField(max_length=240, verbose_name="العنوان بالعربية")), ("title_en", models.CharField(max_length=240, verbose_name="العنوان بالإنكليزية")), ("accent_ar", models.CharField(blank=True, max_length=160, verbose_name="النص المميز بالعربية")), ("accent_en", models.CharField(blank=True, max_length=160, verbose_name="النص المميز بالإنكليزية")), ("body_ar", models.TextField(blank=True, verbose_name="المحتوى بالعربية")), ("body_en", models.TextField(blank=True, verbose_name="المحتوى بالإنكليزية")), ("order", models.PositiveSmallIntegerField(default=0, verbose_name="الترتيب")), ("is_visible", models.BooleanField(default=True, verbose_name="إظهار القسم"))], options={"verbose_name": "قسم صفحة", "verbose_name_plural": "أقسام الصفحات", "ordering": ("page", "order")}),
        migrations.RunPython(seed_sections, migrations.RunPython.noop),
    ]
