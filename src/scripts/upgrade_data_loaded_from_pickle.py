# Useful script to run when a new field has been added/removed from an entity and saved data needs to be refresh
import pickle

from src.entities.user_cooldowns_entity import UserCooldownsEntity
from src.entities.user_entity import UserEntity

PICKLE_FILE_LOCATION = "../../data/users.p"

users_by_id = pickle.load(open(PICKLE_FILE_LOCATION, "rb"))
new_users_by_id = {}

for user in users_by_id.values():
    user.cooldowns = UserCooldownsEntity(timestamp_for_next_basic_booster=user.cooldowns.timestamp_for_next_basic_booster)
    new_users_by_id[user.id] = UserEntity(user.id, money=user.money, boosters_quantity=user.boosters_quantity, cards_by_id=user.cards, user_settings_entity=user.settings, user_cooldowns_entity=user.cooldowns)

pickle.dump(new_users_by_id, open(PICKLE_FILE_LOCATION, "wb"))

print("Pickle upgrade done")
