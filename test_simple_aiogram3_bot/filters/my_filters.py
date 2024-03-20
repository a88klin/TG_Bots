from config_set import config

allowed_ids = config.allowed_ids


def message_filter_users(message, allowed_ids=allowed_ids):
    return message.chat.id in allowed_ids


def callback_filter_users(callback, allowed_ids=allowed_ids):
    return callback.from_user.id in allowed_ids
