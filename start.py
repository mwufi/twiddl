import tweepy

from storage import TwitterProfile, Follow, Storage
from twitter_client import client
from test_log import log
from datetime import datetime
from utils import ExploreQueue
from discord import log_to_discord
from neighbors import MixedNeighborSelector

store = Storage()
store.init()

# get seed user!
screen_name = "tordotcom"
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
    log_to_discord(f"Exploring {username}...")

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
        if users:
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


EXPANSIONS_PER_NODE = 1000
BEGIN_TIME = datetime.now()

first_level = ExploreQueue(
    [screen_name], max_buffer=EXPANSIONS_PER_NODE, max_capacity=1e7
)

# Actually, we can set max_buffer to really high because... it's actually a heap
# so a bigger number will give us a better idea of who to explore
next_level = ExploreQueue([], max_buffer=EXPANSIONS_PER_NODE, max_capacity=1e7)

algo = MixedNeighborSelector(min_count=200, max_count=1e6)
explore_count = 0

# Add everyone that the seed users are following
while len(first_level) > 0:
    show_stats = False
    current_name = first_level.pop(0)
    explore_count += 1

    if not store.has_seen_user(current_name):
        expand_user(current_name)
        show_stats = True

    # Always add neighbors to list, since... we want to continue the BFS
    # where we left off...
    buffer = EXPANSIONS_PER_NODE
    neighborhood = algo.get_neighbors(store, current_name).limit(buffer)
    for user in neighborhood:
        log(f"Adding to seeds:", user.username)
        next_level.append(user.username)

    log(f"Queue length {len(first_level)} Next level {len(next_level)}")
    elapsed = datetime.now() - BEGIN_TIME
    if show_stats:
        log_to_discord(
            "Finished exploring",
            title=f"# {explore_count}",
            author_name=current_name,
            extras={
                "Queue length": len(first_level),
                "Next level": len(next_level),
                "elapsed (minutes)": str(elapsed.total_seconds() / 60),
                **store.log_db_stats(),
            },
        )

# For the infinite search, we limit the number of neighbors
while len(next_level) > 0:
    show_stats = False
    current_name = next_level.pop(0)
    explore_count += 1

    if not store.has_seen_user(current_name):
        expand_user(current_name)
        show_stats = True

    # Always add neighbors to list, since... we want to continue the BFS
    # where we left off...
    buffer = next_level.estimate_free()
    neighborhood = algo.get_neighbors(store, current_name).limit(buffer)
    for user in neighborhood:
        log(f"Adding to seeds:", user.username)
        next_level.append(user.username)

    log(f"Queue length {len(next_level)}")
    elapsed = datetime.now() - BEGIN_TIME
    if show_stats:
        log_to_discord(
            "Finished exploring",
            title=f"# {explore_count}",
            author_name=current_name,
            extras={
                "Queue length": len(next_level),
                "elapsed (minutes)": str(elapsed.total_seconds() / 60),
                **store.log_db_stats(),
            },
        )
