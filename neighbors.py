from storage import TwitterProfile, Follow
from peewee import SQL


class NaiveNeighborSelector:
    def __init__(self, **kwargs) -> None:
        self.conf = kwargs
        print(self.conf["min_count"])

    def get_neighbors(self, store, username):
        """Returns a list of TwitterProfiles that this user follow"""
        profile = store.get_profile_by_username(username)
        id = profile.id
        min_count = self.conf["min_count"]

        neighbors = (
            TwitterProfile.select(TwitterProfile.username)
            .join(Follow, on=(TwitterProfile.id == Follow.celebrity_id))
            .where(Follow.fan_id == id)
            .where(
                TwitterProfile.following_count > min_count
                and TwitterProfile.followers_count > min_count
                and TwitterProfile.tweet_count > min_count
            )
            .order_by(SQL("followers_count"))
        )
        return neighbors


class MixedNeighborSelector:
    def __init__(self, **kwargs) -> None:
        self.conf = kwargs
        print(self.conf["max_count"])
        print(self.conf["min_count"])

    def get_neighbors(self, store, username):
        profile = store.get_profile_by_username(username)
        id = profile.id
        M = self.conf["max_count"]
        m = self.conf["min_count"]
        neighbors = (
            TwitterProfile.select(
                TwitterProfile.username,
                TwitterProfile.following_count,
                TwitterProfile.followers_count,
                TwitterProfile.tweet_count,
                SQL("followers_count / (following_count + 100) * tweet_count").alias(
                    "mixed_popularity"
                ),
            )
            .join(Follow, on=(TwitterProfile.id == Follow.celebrity_id))
            .where(Follow.fan_id == id)
            .where(
                TwitterProfile.following_count < M,
                TwitterProfile.followers_count < M,
                TwitterProfile.tweet_count < M,
                TwitterProfile.followers_count > m,
                TwitterProfile.tweet_count > m,
            )
            .order_by(SQL("mixed_popularity").desc())
        )
        return neighbors


if __name__ == "__main__":
    m = MixedNeighborSelector(min_count=200, max_count=1e6)
