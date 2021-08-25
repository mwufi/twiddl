import tweepy

from storage import TwitterProfile, Follow, Storage
from twitter_client import client
from test_log import log
from datetime import datetime
from utils import ExploreQueue

store = Storage()
store.init()

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

seed_user = store.save_user(user)

print(user.id, user.name)


def mark_expanded(username):
    query = TwitterProfile.update(last_expanded=datetime.now()).where(
        TwitterProfile.username == username
    )
    n = query.execute()
    log(f"{n} Finished exploring", username)


def expand_user(username):
    """Explore the neighborhood of one user"""
    log(f"Exploring", username)

    seed_user = store.get_profile_by_username(username)

    following = []
    for response in tweepy.Paginator(
        client.get_users_following,
        seed_user.twitter_id,
        user_fields=user_fields,
        max_results=1000,
        limit=1,
    ):
        if response.errors:
            log("error", response.errors)
            break

        log("get_users_following", response.meta)
        users = response.data
        following += users

    f_count = 0
    created_count = 0
    for f in following:
        f_count += 1
        profile = store.save_user(f)
        _, created = Follow.get_or_create(fan=seed_user, celebrity=profile)
        if created:
            created_count += 1
    log(f"Created {f_count} users!")
    log(f"Created {created_count} connections!")

    mark_expanded(username)

    return following


EXPANSIONS_PER_NODE = 500

explore_queue = ExploreQueue(
    [screen_name], max_buffer=EXPANSIONS_PER_NODE, max_capacity=1e7
)
next_level = ExploreQueue([], max_buffer=EXPANSIONS_PER_NODE, max_capacity=1e7)

# BFS search
while len(explore_queue) or len(next_level):
    while len(explore_queue) > 0:
        current_name = explore_queue.pop(0)
        if not store.has_seen_user(current_name):
            expand_user(current_name)

        buffer = next_level.estimate_free()
        neighborhood = store.get_neighbors(current_name).limit(buffer)
        for user in neighborhood:
            log(f"Adding to seeds:", user.username)
            next_level.append(user.username)

        log(f"Queue length {len(explore_queue)} Next level {len(next_level)}")
        store.log_db_stats()

    explore_queue = next_level
    next_level = ExploreQueue([], max_buffer=500, max_capacity=1e7)
