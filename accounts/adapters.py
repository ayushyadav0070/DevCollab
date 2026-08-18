from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.socialaccount.models import SocialLogin

class GithubAdapter(DefaultSocialAccountAdapter):

    def populate_user(self, request, sociallogin:SocialLogin, data):
        user=super().populate_user(request, sociallogin, data)

        # mapping github_id in user model to git oauth settings

        if sociallogin.account.provider =='github':
            data = sociallogin.account.extra_data
            user.github_id = data.get('login')
            user.avatar_url = data.get('avatar_url')
            user.full_name = data.get('name','')
        return user