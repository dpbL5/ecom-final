from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("search", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="searchproductdocument",
            name="image_urls",
            field=models.JSONField(blank=True, default=list),
        ),
    ]
