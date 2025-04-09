def get_profile_link(user_id: int | str, full_name: str) -> str:
    return f'<a href="tg://user?id={user_id}">{full_name}</a>'


def make_build(string: str) -> str:
    return f"<b>{string}</b>"


def make_pretty(string: str) -> str:
    return f"<b><i><u>{string}</u></i></b>"


def get_minutes_and_seconds_text(
    start: int | None = None,
    end: int | None = None,
    seconds: int | None = None,
    message="До начала игры осталось примерно ",
) -> str:
    if seconds:
        diff = seconds
    else:
        diff = end - start
    minutes = diff // 60
    seconds = diff % 60
    if minutes:
        message += f"{minutes} мин. "
    message += f"{seconds} сек."
    return message


def cut_off_old_text(text: str):
    text = "\n\n".join(text.split("\n\n")[-11:-1:1]) + "\n\n"
    return text
