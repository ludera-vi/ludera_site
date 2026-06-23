from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse

from main.models import Product, BlogPost, Service, Project
from main.templatetags.main_tags import embed_videos
from users.models import Goods, GoodsFile, UserGoods, CabinetPermission


class EmbedVideosFilterTest(TestCase):
    def test_youtube_embed_url(self):
        result = embed_videos('{video:https://www.youtube.com/embed/dQw4w9WgXcQ}')
        self.assertIn('vplayer', result)
        self.assertIn('data-video="dQw4w9WgXcQ"', result)
        self.assertIn('img.youtube.com', result)

    def test_youtube_watch_url(self):
        result = embed_videos('{video:https://www.youtube.com/watch?v=dQw4w9WgXcQ}')
        self.assertIn('data-video="dQw4w9WgXcQ"', result)

    def test_youtu_be_url(self):
        result = embed_videos('{video:https://youtu.be/dQw4w9WgXcQ}')
        self.assertIn('data-video="dQw4w9WgXcQ"', result)

    def test_vimeo_url(self):
        result = embed_videos('{video:https://vimeo.com/123456789}')
        self.assertIn('vplayer', result)
        self.assertIn('data-embed=', result)

    def test_plain_text_unchanged(self):
        text = '<p>Hello world</p>'
        result = embed_videos(text)
        self.assertEqual(result, text)

    def test_empty_value(self):
        self.assertEqual(embed_videos(''), '')
        self.assertIsNone(embed_videos(None))

    def test_multiple_videos(self):
        text = '{video:https://youtu.be/aaa} text {video:https://youtu.be/bbb}'
        result = embed_videos(text)
        self.assertIn('data-video="aaa"', result)
        self.assertIn('data-video="bbb"', result)

    def test_non_video_url_fallback(self):
        result = embed_videos('{video:https://example.com/video.mp4}')
        self.assertIn('iframe', result)
        self.assertIn('example.com/video.mp4', result)


class StaticFilesTest(TestCase):
    def test_content_display_css_exists(self):
        import os
        path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'css', 'content-display.css')
        self.assertTrue(os.path.exists(path), 'content-display.css not found')

    def test_content_display_js_exists(self):
        import os
        path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'js', 'content-display.js')
        self.assertTrue(os.path.exists(path), 'content-display.js not found')

    def test_cabinet_editor_css_exists(self):
        import os
        path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'css', 'cabinet-editor.css')
        self.assertTrue(os.path.exists(path), 'cabinet-editor.css not found')


class CabinetEditorTemplateTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='admin', password='testpass123', is_staff=True)
        for section, _ in CabinetPermission.SECTIONS:
            CabinetPermission.objects.create(user=self.user, section=section)
        self.client.login(username='admin', password='testpass123')

    def test_goods_form_includes_shared_editor_css(self):
        response = self.client.get(reverse('cabinet:goods_create'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'cabinet-editor.css')
        self.assertContains(response, 'quill-editor')
        self.assertContains(response, 'rich-editor')

    def test_product_form_includes_shared_editor_css(self):
        response = self.client.get(reverse('cabinet:product_create'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'cabinet-editor.css')
        self.assertContains(response, 'quill-editor')
        self.assertContains(response, 'rich-editor')

    def test_service_form_includes_shared_editor_css(self):
        response = self.client.get(reverse('cabinet:service_create'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'cabinet-editor.css')
        self.assertContains(response, 'quill-editor')
        self.assertContains(response, 'rich-editor')


class UserDetailTemplateTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.goods = Goods.objects.create(
            title='Test Good',
            content='<div class="ql-code-block-container"><div class="ql-code-block">const x = 1;</div></div>',
        )
        UserGoods.objects.create(user=self.user, goods=self.goods, is_active=True)
        self.client.login(username='testuser', password='testpass123')

    def test_goods_detail_includes_content_display_files(self):
        response = self.client.get(reverse('users:goods_detail', args=[self.goods.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'content-display.css')
        self.assertContains(response, 'content-display.js')
        self.assertContains(response, 'prismjs')
        self.assertContains(response, 'pre-content')

    def test_goods_detail_renders_code_block(self):
        response = self.client.get(reverse('users:goods_detail', args=[self.goods.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'ql-code-block-container')
        self.assertContains(response, 'const x = 1;')


class PublicDetailTemplateTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.product = Product.objects.create(
            title='Test Product',
            content='<div class="ql-code-block-container"><div class="ql-code-block">print("hello")</div></div>',
        )

    def test_product_detail_includes_content_display(self):
        response = self.client.get(reverse('main:product_detail', args=[self.product.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'content-display.css')
        self.assertContains(response, 'content-display.js')
        self.assertContains(response, 'prismjs')
        self.assertContains(response, 'pre-content')

    def test_blog_detail_includes_content_display(self):
        blog = BlogPost.objects.create(
            title='Test Post',
            content='<p>Test content</p>',
            category='Test',
            author='Author',
        )
        response = self.client.get(reverse('main:blog_detail', args=[blog.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'content-display.css')
        self.assertContains(response, 'content-display.js')
