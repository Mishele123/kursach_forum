from auth.in_memory import MemoryStorage
from auth.user_interactor import CreateUserInteractor
from auth.user_interfaces import UserRepository
from dishka import Provider, Scope, provide


class AuthProvider(Provider):
    user_repo = provide(source=MemoryStorage, scope=Scope.APP, provides=UserRepository)
    create_user = provide(source=CreateUserInteractor, scope=Scope.REQUEST)
