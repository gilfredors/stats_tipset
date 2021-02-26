import random


def get_draft(matches, players, number_matches_per_player):
    draft = {player: [] for player in players}
    for _ in range(number_matches_per_player):
        for player in players:
            match = random.choice(matches)
            index_match = matches.index(match)
            matches.pop(index_match)
            draft[player].append(match)
    return draft, matches


def main():
    matches = list(range(1, 14))
    players = ['Zimon', 'Dawid', 'Joakim', 'Gilfredo']
    draft, undrafted = get_draft(matches, players, 3)

    for player, matches in draft.items():
        print(f'* {player}: {", ".join(map(str, matches))}')

    print(f'Match to decide: {undrafted}')


if __name__ == '__main__':
    main()
