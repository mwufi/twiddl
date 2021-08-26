from keys import webhook_url
from discord_webhook import DiscordWebhook, DiscordEmbed


def log_to_discord(
    *args, title="", description="", author_name="", author_url="", extras={}
):
    msg = " ".join(map(str, args))
    webhook = DiscordWebhook(url=webhook_url, content=msg)

    if title or description:
        embed = DiscordEmbed(title=title, description=description, color="03b2f8")
        embed.set_author(
            name=author_name,
            url=author_url,
            icon_url="https://avatars0.githubusercontent.com/u/14542790",
        )
        # embed.set_footer(text="Embed Footer Text")
        embed.set_timestamp()

        for k, v in extras.items():
            embed.add_embed_field(name=k, value=v)

        webhook.add_embed(embed)
    return webhook.execute()


if __name__ == "__main__":
    log_to_discord(
        "Finished exploring",
        title="#223",
        author_name="Behance",
        extras={
            "Queue length": 343,
            "Next level": 1233,
            "users": 12,
            "connections": 12312,
        },
    )
    r = log_to_discord("ok fine")
    print(r.text)
