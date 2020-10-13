from configparser import SafeConfigParser


class Settings():
    config = SafeConfigParser()
    config.read("settings.ini")

    def write_changes(self):
        with open('settings.ini', 'w') as config_file:
            self.config.write(config_file)
            config_file.close()

    def get_config(self, key, default=None):
        return self.config.get("DEFAULT", key, fallback=default)

    def get_bool(self, key, default=False):
        return bool(self.config.get("DEFAULT", key, fallback=default) == "True")

    def set_config(self, key, value):
        value = str(value)
        self.config.set("DEFAULT", key, value)
        self.write_changes()

    def add_to_list(self, key, value):
        config_value = self.config.get("DEFAULT", key, fallback=None)
        value = str(value)

        if config_value:
            config_list = config_value.split("|")
        else:
            config_list = []

        if value not in config_list:
            config_list.append(value)

        self.config.set("DEFAULT", key, "|".join(config_list))
        self.write_changes()

    def remove_from_list(self, key, value):
        config_value = self.config.get("DEFAULT", key, fallback=None)
        value = str(value)

        if config_value:
            config_list = config_value.split("|")
        else:
            return

        if value in config_list:
            config_list.remove(value)
        else:
            return

        self.config.set("DEFAULT", key, "|".join(config_list))
        self.write_changes()

    def get_list(self, key):
        list_setting = self.config.get("DEFAULT", key, fallback="")
        return list_setting.split("|") if list_setting else []
