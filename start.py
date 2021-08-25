import tweepy

from storage import TwitterProfile, Follow, Storage
from twitter_client import client
from test_log import log
import random
import numpy as np
from datetime import datetime

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


def mark_expanded(user):
    profile = TwitterProfile.get(TwitterProfile.username == user.username)
    profile.last_expanded = datetime.now()
    log(f"Finished exploring", user.username, profile.last_expanded)


def expand_user(user):
    """Explore the neighborhood of one user"""
    log(f"Exploring", user)

    following = []
    for response in tweepy.Paginator(
        client.get_users_following,
        user.id,
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

    mark_expanded(next_user)

    return following


def sample_next_user(neighborhood, k=5):
    """Decide who to expand next"""
    score = (
        lambda user: np.log10(user.public_metrics["tweet_count"] + 1)
        + np.log10(user.public_metrics["followers_count"] + 1)
        - np.log10(user.public_metrics["following_count"] + 1)
    )
    weights = [score(user) for user in neighborhood]
    names = [user.username for user in neighborhood]
    my_choices = random.choices(names, weights, k=k)

    # dedup any random choices
    my_choices = list(set(my_choices))
    name2user = {user.username: user for user in neighborhood}
    return map(lambda name: name2user[name], my_choices)


explore_queue = [user]

while explore_queue:
    next_user = explore_queue.pop(0)
    if store.has_seen_user(next_user):
        log(f"Has seen {user.name} before!")
        continue
    
    neighborhood = expand_user(next_user)
    seeds = sample_next_user(neighborhood, k=200)
    for user in seeds:
        log("Adding to seeds:", user)
        explore_queue.append(user)
    
    store.log_db_stats()
