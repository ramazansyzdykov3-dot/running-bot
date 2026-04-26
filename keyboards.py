from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup


def confirm_run_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Сохранить", callback_data="run_save"),
            InlineKeyboardButton("Отменить", callback_data="run_cancel"),
        ]
    ])


def skip_notes_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        [["/skip"]],
        one_time_keyboard=True,
        resize_keyboard=True,
    )


def main_menu_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        [
            ["Новая пробежка", "Прогресс"],
            ["Статистика", "История"],
            ["График", "Советы"],
        ],
        resize_keyboard=True,
    )
