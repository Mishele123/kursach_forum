from auth.in_memory import MemoryStorage
from auth.user_interactor import CreateUserInteractor
from auth.user_interfaces import UserRepository
from posts.post_storage import PostStorage
from bikes.bike_storage import BikeStorage
from dishka import Provider, Scope, provide


class AuthProvider(Provider):
    user_repo = provide(source=MemoryStorage, scope=Scope.APP, provides=UserRepository)
    create_user = provide(source=CreateUserInteractor, scope=Scope.REQUEST)


class PostProvider(Provider):
    post_storage = provide(source=PostStorage, scope=Scope.APP)


class BikeProvider(Provider):
    bike_storage = provide(source=BikeStorage, scope=Scope.APP)
