from django.db import migrations
from django.utils.text import slugify


def populate_slugs(apps, schema_editor):
    for model_name in ('Service', 'Project', 'Product', 'BlogPost'):
        Model = apps.get_model('main', model_name)
        for obj in Model.objects.all():
            if not obj.slug:
                base = slugify(obj.title, allow_unicode=True)[:200]
                if not base:
                    fallback = {'Service': 'usluga', 'Project': 'proekt', 'Product': 'produkt', 'BlogPost': 'statya'}
                    base = fallback.get(model_name, 'item')
                slug = base
                counter = 1
                while Model.objects.filter(slug=slug).exclude(pk=obj.pk).exists():
                    counter += 1
                    slug = f'{base}-{counter}'
                obj.slug = slug
                obj.save(update_fields=['slug'])


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0005_blogpost_slug_product_slug_project_slug_service_slug_and_more'),
    ]

    operations = [
        migrations.RunPython(populate_slugs),
    ]
