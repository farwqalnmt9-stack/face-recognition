from django.db import migrations, models


def seed_products(apps, schema_editor):
    Product = apps.get_model("web", "Product")
    items = [
        ("kajo-erp", "كاجو ERP", "Kajo ERP", "منظومة مالية وتشغيلية متكاملة تربط الحسابات والمخزون والمبيعات.", "A unified finance and operations platform connecting accounting, inventory and sales.", "Enterprise resource planning", "#a8e82c"),
        ("kajo-dental", "كاجو لطب الأسنان", "Kajo Dental", "إدارة المواعيد والمرضى والفواتير والملفات الطبية من مكان واحد.", "Manage appointments, patients, billing and clinical files from one place.", "Clinic management", "#2bd66f"),
        ("kajo-pos", "كاجو نقاط البيع", "Kajo POS", "نقاط بيع سريعة ومتعددة الفروع مع مخزون متزامن وتقارير فورية.", "Fast multi-branch point of sale with synced inventory and instant reports.", "Retail operations", "#d7ff5c"),
        ("kajo-hr", "كاجو للموارد البشرية", "Kajo HR", "الحضور والرواتب والإجازات وملفات الموظفين ضمن تجربة واضحة.", "Attendance, payroll, leave and employee records in one clear experience.", "People operations", "#42b65e"),
        ("kajo-analytics", "كاجو للتحليلات", "Kajo Analytics", "حوّل بيانات شركتك إلى مؤشرات وقرارات يمكن متابعتها لحظة بلحظة.", "Turn business data into live indicators and confident decisions.", "Business intelligence", "#8fdb32"),
        ("kajo-cloud", "كاجو السحابي", "Kajo Cloud", "وصول آمن لأنظمة كاجو وتحديثاتها من أي مكان وعلى أي جهاز.", "Secure access to Kajo systems and updates from anywhere, on any device.", "Cloud services", "#30c979"),
    ]
    for slug, ar, en, sar, sen, category, accent in items:
        Product.objects.update_or_create(slug=slug, defaults={"name_ar": ar, "name_en": en, "summary_ar": sar, "summary_en": sen, "category": category, "accent": accent, "is_active": True})


class Migration(migrations.Migration):
    dependencies = [("web", "0001_initial")]
    operations = [
        migrations.AddField(model_name="product", name="summary_en", field=models.TextField(blank=True, verbose_name="English summary")),
        migrations.AddField(model_name="product", name="category", field=models.CharField(default="Business software", max_length=80, verbose_name="التصنيف")),
        migrations.AddField(model_name="product", name="accent", field=models.CharField(default="#1ca84b", max_length=20, verbose_name="لون العرض")),
        migrations.RunPython(seed_products, migrations.RunPython.noop),
    ]
