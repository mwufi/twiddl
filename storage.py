from peewee import *

db = SqliteDatabase("twitter.db")


class BaseModel(Model):
    """
    Create a base model class which specifies our database
    """

    class Meta:
        database = db


class TwitterProfile(BaseModel):
    twitter_id = IntegerField(unique=True)
    username = CharField(unique=True)

    name = CharField()
    profile_image_url = CharField()

    url = CharField()
    description = CharField()

    followers_count = IntegerField()
    following_count = IntegerField()
    tweet_count = IntegerField()
    listed_count = IntegerField()
    created_at = DateTimeField()


class Follow(BaseModel):
    fan = ForeignKeyField(TwitterProfile)
    celebrity = ForeignKeyField(TwitterProfile)

    class Meta:
        primary_key = CompositeKey("fan", "celebrity")


MODELS = [TwitterProfile, Follow]


class Storage:
    """The API we use to save things"""

    def init(self):
        db.connect()
        db.create_tables(MODELS)

    def save_user(self, user):
        try:
            profile = TwitterProfile.create(
                twitter_id=user["id"],
                name=user["name"],
                username=user["username"],
                profile_image_url=user["profile_image_url"],
                url=user["url"],
                description=user["description"],
                created_at=user["created_at"],
                followers_count=user.public_metrics["followers_count"],
                following_count=user.public_metrics["following_count"],
                tweet_count=user.public_metrics["tweet_count"],
                listed_count=user.public_metrics["listed_count"],
            )
        except IntegrityError:
            profile = TwitterProfile.get(TwitterProfile.username == user.username)
        return profile

    def clear(self):
        db.drop_tables(MODELS)
        db.create_tables(MODELS)
