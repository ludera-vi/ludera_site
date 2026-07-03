from allauth.socialaccount.models import SocialApp


def social_providers_configured(request):
    apps = SocialApp.objects.all()
    configured_ids = [app.provider for app in apps]
    return {
        'configured_providers': configured_ids,
    }
