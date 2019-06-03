from graphene_django.forms.mutation import DjangoModelFormMutation

from allauth.exceptions import ImmediateHttpResponse
from allauth.utils import get_form_class, get_request_param
from allauth.account import app_settings, signals
from allauth.account.adapter import get_adapter
from allauth.account.forms import (
    AddEmailForm,
    ChangePasswordForm,
    LoginForm,
    ResetPasswordForm,
    ResetPasswordKeyForm,
    SetPasswordForm,
    SignupForm,
    UserTokenForm,
)



class LoginMutation(DjangoModelFormMutation):
    class Meta:
        form_class = LoginForm

    authUser = Field(UserNode)

    @classmethod
    def get_form_class(cls):
        return get_form_class(app_settings.FORMS, 'login', cls.form_class)

    @classmethod
    def get_form_kwargs(cls, root, info, **input):
        kwargs = {"data": input}
        kwargs['request'] = info.context
        return kwargs

    @classmethod
    def perform_mutate(cls, form, info):
        form.login(info.context)
        obj = form.user
        return cls(errors=[], authUser=obj)


class SignupMutation(DjangoModelFormMutation):
    form_class = SignupForm

    @classmethod
    def is_open(cls, request):
        return get_adapter(request).is_open_for_signup(request)

    @classmethod
    def get_form_class(cls):
        return get_form_class(app_settings.FORMS, 'signup', cls.form_class)


    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        if not cls.is_open(info.context):
            raise ValidationError()
        return 

    @classmethod
    def perform_mutate(cls, form, info):
        obj = form.save(info.context)
        try:
            return complete_signup(
                info.context, obj,
                app_settings.EMAIL_VERIFICATION)
        except ImmediateHttpResponse as e:
            return e.response
        return cls(errors=[], authUser=obj)
