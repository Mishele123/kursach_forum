from auth.user_storage import SqlAlchemyUserRepository
from auth.user_interactor import CreateUserInteractor
from auth.user_interfaces import UserRepository
from posts.post_storage import PostStorage
from bikes.bike_storage import BikeStorage
from database import Database
from dishka import Provider, Scope, provide, from_context


class AppProvider(Provider):
    database = from_context(provides=Database, scope=Scope.APP)
    user_repo = provide(source=SqlAlchemyUserRepository, scope=Scope.APP, provides=UserRepository)
    create_user = provide(source=CreateUserInteractor, scope=Scope.REQUEST)
    post_storage = provide(source=PostStorage, scope=Scope.APP)
    bike_storage = provide(source=BikeStorage, scope=Scope.APP)
