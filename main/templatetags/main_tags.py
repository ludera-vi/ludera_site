import re
import urllib.parse
from django import template
from django.utils.html import mark_safe

register = template.Library()


@register.filter
def truncate_chars(value, max_length):
    if not value:
        return ''
    text = str(value)
    if len(text) <= max_length:
        return text
    return text[:max_length] + '…'


@register.filter(is_safe=True)
def privacy_format(value):
    if not value:
        return ''
    blocks = value.strip().split('\n\n')
    parts = []
    for block in blocks:
        lines = block.strip().split('\n')
        stripped = [l.strip() for l in lines if l.strip()]
        if not stripped:
            continue
        is_list = all(l.startswith('-') or l.startswith('—') or l.startswith('•') for l in stripped)
        if is_list:
            items = []
            for l in stripped:
                item = l.lstrip('-—• ').strip()
                items.append(f'<li class="privacy__list-item">{item}</li>')
            parts.append('<ul class="privacy__list">' + ''.join(items) + '</ul>')
        else:
            parts.append('<p class="privacy__text">' + ' '.join(stripped) + '</p>')
    return mark_safe('\n'.join(parts))


@register.filter(is_safe=True)
def embed_videos(value):
    if not value:
        return value

    def youtube_id(url):
        parsed = urllib.parse.urlparse(url)
        if 'youtube.com' in parsed.netloc:
            if '/embed/' in parsed.path:
                return parsed.path.split('/embed/')[-1].split('?')[0].split('&')[0]
            qs = urllib.parse.parse_qs(parsed.query)
            return qs.get('v', [None])[0]
        if 'youtu.be' in parsed.netloc:
            return parsed.path.lstrip('/').split('?')[0].split('&')[0]
        return None

    def vimeo_id(url):
        match = re.search(r'vimeo\.com/(\d+)', url)
        return match.group(1) if match else None

    def make_thumb(vid):
        thumb = f'https://img.youtube.com/vi/{vid}/maxresdefault.jpg'
        return (
            f'<div class="vplayer" data-video="{vid}">'
            f'<img class="vplayer__thumb" src="{thumb}" alt="" loading="lazy">'
            f'<div class="vplayer__btn">'
            f'<svg viewBox="0 0 68 48" width="68" height="48">'
            f'<path d="M66.52 7.74c-.78-2.93-2.49-5.41-5.42-6.19C55.79.13 34 0 34 0S12.21.13 6.9 1.55c-2.93.78-4.63 3.26-5.42 6.19C0 13.07 0 24 0 24s0 10.93 1.48 16.26c.78 2.93 2.49 5.41 5.42 6.19C12.21 47.87 34 48 34 48s21.79-.13 27.1-1.55c2.93-.78 4.64-3.26 5.42-6.19C68 34.93 68 24 68 24s0-10.93-1.48-16.26z" fill="red"/>'
            f'<path d="M45 24L27 14v20z" fill="white"/>'
            f'</svg></div></div>'
        )

    def make_vimeo(vim_id):
        embed_url = f'https://player.vimeo.com/video/{vim_id}?autoplay=1'
        thumb = f'https://vumbnail.com/{vim_id}.jpg'
        e = embed_url.replace('"', '&quot;')
        return (
            f'<div class="vplayer" data-embed="{e}">'
            f'<img class="vplayer__thumb" src="{thumb}" alt="" loading="lazy">'
            f'<div class="vplayer__btn">'
            f'<svg viewBox="0 0 68 48" width="68" height="48">'
            f'<path d="M66.52 7.74c-.78-2.93-2.49-5.41-5.42-6.19C55.79.13 34 0 34 0S12.21.13 6.9 1.55c-2.93.78-4.63 3.26-5.42 6.19C0 13.07 0 24 0 24s0 10.93 1.48 16.26c.78 2.93 2.49 5.41 5.42 6.19C12.21 47.87 34 48 34 48s21.79-.13 27.1-1.55c2.93-.78 4.64-3.26 5.42-6.19C68 34.93 68 24 68 24s0-10.93-1.48-16.26z" fill="red"/>'
            f'<path d="M45 24L27 14v20z" fill="white"/>'
            f'</svg></div></div>'
        )

    def replace_video(match):
        url = match.group(1)

        vid = youtube_id(url)
        if vid:
            return make_thumb(vid)

        vim_id = vimeo_id(url)
        if vim_id:
            return make_vimeo(vim_id)

        return (
            f'<div class="video-container">'
            f'<iframe src="{url}" frameborder="0" allowfullscreen '
            f'allow="autoplay; fullscreen" loading="lazy">'
            f'</iframe></div>'
        )

    result = re.sub(r'\{video:([^}]+)\}', replace_video, value)
    return mark_safe(result)
