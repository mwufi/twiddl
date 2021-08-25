import json
from datetime import datetime
import tweepy

from storage import TwitterProfile, Follow, db, remember_user
from twitter_client import client

# connect to db!
db.connect()
db.create_tables([TwitterProfile, Follow])

# get seed user!
screen_name = "aliettedb"
user_fields = [
    "created_at",
    "description",
    "profile_image_url",
    "public_metrics",
    "url",
]

response = client.get_user(
    username=screen_name,
    user_fields=user_fields,
)
user = response.data

seed_user = remember_user(user)

print(user.id, user.name)


responses = []
for response in tweepy.Paginator(
    client.get_users_following,
    user.id,
    user_fields=user_fields,
    max_results=1000,
    limit=2,
):
    responses.append(response)
    print(response.meta)


user_count = 0
for r in responses:
    for i, user in enumerate(r.data):
        user_count += 1
        profile = remember_user(user)
        following = Follow.create(fan=seed_user, celebrity=profile)

print(f"Created {user_count} users!")

# there should... only be 1?
query = TwitterProfile.select().where(TwitterProfile.name == "Frances Hardinge")
for user in query:
    print(
        "%s has %d followers! Visit them at %s"
        % (user.name, user.followers_count, user.profile_image_url)
    )
