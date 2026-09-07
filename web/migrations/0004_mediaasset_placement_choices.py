from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("web", "0003_site_sections_and_media_uploads")]
    operations = [
        migrations.AlterField(
            model_name="mediaasset",
            name="placement",
            field=models.CharField(
                blank=True,
                choices=[
                    ("home_hero", "صورة الواجهة الرئيسية"),
                    ("home_success", "صورة قصة النجاح"),
                    ("login_visual", "صورة صفحة تسجيل الدخول"),
                ],
                help_text="اختر مكان الصورة، وسيظهر آخر ملف نشط مرفوع في هذا المكان.",
                max_length=80,
                verbose_name="مكان الظهور",
            ),
        ),
    ]
