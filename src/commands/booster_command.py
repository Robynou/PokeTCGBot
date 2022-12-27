import pickle
import random

import discord
from discord import Embed, app_commands
from discord.ext import commands
from pokemontcgsdk import Card, Set

from src.services.localization_service import LocalizationService
from src.services.rarity_service import RarityService
from src.services.settings_service import SettingsService
from src.colors import GREEN
from src.services.type_service import TypeService


class BoosterCog(commands.Cog):
    CARDS_PICKLE_FILE_LOCATION = "data/cards.p"

    def __init__(self, bot: commands.Bot, settings_service: SettingsService,
                 localization_service: LocalizationService, rarity_service: RarityService,
                 type_service: TypeService) -> None:
        self.bot = bot
        self.settings_service = settings_service
        self.t = localization_service.get_string
        self.rarity_service = rarity_service
        self.type_service = type_service
        self.sets: list[Set] = Set.all()
        self.cards_by_rarity: dict[str, list[Card]] = BoosterCog._compute_all_cards()

    @staticmethod
    def _filter_cards_for_rarities(cards: list[Card], rarities: set[str]) -> list[Card]:
        filtered_cards = []
        for card in cards:
            rarity = card.rarity.lower()
            if rarity in rarities:
                filtered_cards.append(card)
        return filtered_cards

    @staticmethod
    def _compute_all_cards() -> dict[str, list[Card]]:
        cards: list[Card] = pickle.load(open(BoosterCog.CARDS_PICKLE_FILE_LOCATION, "rb"))
        # TODO: find out why some cards don't have any rarity and define what should be the default rarity for them
        cards_with_rarity = list(filter(lambda card: card.rarity is not None, cards))
        return {
            "common": BoosterCog._filter_cards_for_rarities(cards_with_rarity, {"common"}),
            "uncommon": BoosterCog._filter_cards_for_rarities(cards_with_rarity, {"uncommon"}),
            "tier_0": BoosterCog._filter_cards_for_rarities(cards_with_rarity, {"rare"}),
            "tier_1": BoosterCog._filter_cards_for_rarities(cards_with_rarity, {"rare holo", "promo"}),
            "tier_2": BoosterCog._filter_cards_for_rarities(cards_with_rarity, {"rare holo ex", "rare holo gx",
                                                                                "rare holo v", "rare break"}),
            "tier_3": BoosterCog._filter_cards_for_rarities(cards_with_rarity, {"radiant rare", "rare holo lv.x",
                                                                                "rare holo vmax", "rare ace",
                                                                                "rare ultra",
                                                                                "amazing rare", "rare prime",
                                                                                "rare prism rare",
                                                                                "rare shining", "rare shiny"}),
            "tier_4": BoosterCog._filter_cards_for_rarities(cards_with_rarity,
                                                            {"legend", "rare holo star", "rare rainbow",
                                                             "rare secret", "rare shiny gx", "v-union",
                                                             "rare holo vstar"})
        }

    def _get_card_type_display(self, card: Card) -> str:
        if card.types is None or len(card.types) == 0:
            return ""
        return f"[{self.type_service.get_type(card.types[0].lower()).emoji}]"

    def _display_card_in_embed(self, card: Card, embed: Embed):
        rarity_emoji = "" if (rarity := self.rarity_service.get_rarity(
            card.rarity.lower())) is None else rarity.emoji
        type_emoji = self._get_card_type_display(card)
        embed.add_field(name=card.id,
                        value=f"{card.name} {type_emoji}\n `{card.rarity} {rarity_emoji}`\n ~ {card.set.name} ~")

    def _draw_rare_card(self) -> Card:
        card_tier = ""
        drop_number = random.random()
        if drop_number < 0.4:
            card_tier = "tier_0"
        elif drop_number < 0.7:
            card_tier = "tier_1"
        elif drop_number < 0.9:
            card_tier = "tier_2"
        elif drop_number < 0.98:
            card_tier = "tier_3"
        elif drop_number < 1:
            card_tier = "tier_4"

        return random.choice(self.cards_by_rarity[card_tier])

    @app_commands.command(name="booster", description="Open a random booster")
    async def booster_command(self, interaction: discord.Interaction) -> None:
        user_language_id = self.settings_service.get_user_language_id(interaction.user.id)

        embed = Embed(
            title=f"---------- {self.t(user_language_id, 'booster_cmd.title')} ----------",
            description=self.t(user_language_id, 'booster_cmd.description'),
            color=GREEN)
        embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)

        # Draw the 5 common cards
        for _ in range(5):
            self._display_card_in_embed(random.choice(self.cards_by_rarity["common"]), embed)

        # Draw the 3 uncommon cards
        for _ in range(3):
            self._display_card_in_embed(random.choice(self.cards_by_rarity["uncommon"]), embed)

        # Draw the rare or higher card
        self._display_card_in_embed(self._draw_rare_card(), embed)

        await interaction.response.send_message(embed=embed)
