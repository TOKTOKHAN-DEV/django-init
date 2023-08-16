from urllib import parse

from channels.auth import AuthMiddleware
from channels.sessions import CookieMiddleware, SessionMiddleware
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.tokens import AccessToken

from app.user.models import User


async def get_user(scope):
    query_string = scope["query_string"].decode("utf-8")
    query_string = parse.parse_qs((parse.urlsplit(query_string).path.encode("ascii")).decode("ascii"))
    access = query_string.get("access", [None])[0]
    if access:
        access_token = AccessToken(access)
        try:
            return await User.objects.aget(pk=access_token.payload["user_id"])
        except User.DoesNotExist:
            return AnonymousUser()
    else:
        return AnonymousUser()


class TokenAuthMiddleware(AuthMiddleware):
    async def resolve_scope(self, scope):
        scope["user"]._wrapped = await get_user(scope)


TokenAuthMiddlewareStack = lambda inner: CookieMiddleware(SessionMiddleware(TokenAuthMiddleware(inner)))
