from src.entities.user_settings_entity import UserSettingsEntity


class UserEntity:
    def __init__(self, user_id: int, money: int = 0, user_settings_entity: UserSettingsEntity = None):
        self.id = user_id
        self.money = money
        self.settings = user_settings_entity if user_settings_entity is not None else UserSettingsEntity()
