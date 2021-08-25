from re import I
from peewee import *
from test_log import log

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

    last_expanded = DateTimeField(null=True)


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
                last_expanded=None,
            )
        except IntegrityError:
            profile = TwitterProfile.get(TwitterProfile.username == user.username)
        return profile

    def has_seen_user(self, username):
        profile = TwitterProfile.get(TwitterProfile.username == username)
        log(f"{username} seen?", profile.last_expanded)
        return profile.last_expanded is not None

    def clear(self):
        db.drop_tables(MODELS)
        db.create_tables(MODELS)

    def get_profile_by_username(self, username):
        """Returns the TwitterProfile of this user"""
        profile = TwitterProfile.get(TwitterProfile.username == username)
        return profile

    def get_neighbors(self, username):
        """Returns a list of TwitterProfiles that this user follow"""
        profile = self.get_profile_by_username(username)
        id = profile.id
        neighbors = (
            TwitterProfile.select()
            .join(Follow, on=(TwitterProfile.id == Follow.celebrity_id))
            .where(Follow.fan_id == id)
            .where(
                TwitterProfile.following_count > 200
                and TwitterProfile.followers_count > 200
                and TwitterProfile.tweet_count > 200
            )
            .order_by(fn.Random())
        )
        return neighbors

    def log_db_stats(self):
        n_users = TwitterProfile.select().count()
        n_connections = Follow.select().count()
        log(f"db now has {n_users} users and {n_connections} connections")
