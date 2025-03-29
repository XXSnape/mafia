from collections import Counter

from cache.cache_types import PlayersIds


def get_the_most_frequently_encountered_id(ids: PlayersIds):
    if not ids:
        return None
    if len(set(ids)) == 1:
        return ids[0]
    most_common = Counter(ids).most_common()
    if most_common[0][1] == most_common[1][1]:
        return None
    return most_common[0][0]
