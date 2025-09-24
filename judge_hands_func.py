# import package
# basic
from collections import defaultdict

'''
including function : 
* rank_map
* HAND_RANK
* get_hand_score(hand_result)
* convert_cards(cards)
* get_rank_counts(cards)
* get_suit_groups(cards)
* is_straight(ranks)
* evaluate_hand(seven_cards, return_best_cards=False)
* 

'''



# def rank map
rank_map = {
    'A': 14, 'K': 13, 'Q': 12, 'J': 11, 'T': 10,
    '9': 9, '8': 8, '7': 7, '6': 6,
    '5': 5, '4': 4, '3': 3, '2': 2
}

# def hand rank
HAND_RANK = {
    'High Card': 1,
    'One Pair': 2,
    'Two Pairs': 3,
    'Three of a Kind': 4,
    'Straight': 5,
    'Flush': 6,
    'Full House': 7,
    'Four of a Kind': 8,
    'Straight Flush': 9
}


# get hand score
def get_hand_score(hand_result):
    name, value, best_cards = hand_result
    # change hand into rank
    base = HAND_RANK[name]
    # get kicker
    ranks = sorted([c[1] for c in best_cards], reverse=True)
    return (base, value, ranks)

# convert rank to num
def convert_cards(cards):
    return [(suit, rank_map[rank]) for suit, rank in cards]

# get rank count
def get_rank_counts(cards):
    counts = defaultdict(list)
    for suit, rank in cards:
        counts[rank].append((suit, rank))
    return counts

# get suit count
def get_suit_groups(cards):
    suits = defaultdict(list)
    for suit, rank in cards:
        suits[suit].append((suit, rank))
    return suits

# distinguish straight
def is_straight(ranks):
    ranks = sorted(set(ranks))
    for i in range(len(ranks) - 4):
        if ranks[i+4] - ranks[i] == 4:
            return ranks[i+4], ranks[i:i+5]
    if set([14, 2, 3, 4, 5]).issubset(set(ranks)):
        return 5, [2, 3, 4, 5, 14]
    return False, []

# evaluate hand
def evaluate_hand(seven_cards, return_best_cards=False):
    cards = convert_cards(seven_cards)
    rank_counts = get_rank_counts(cards)
    suit_groups = get_suit_groups(cards)
    all_ranks = sorted([r for _, r in cards], reverse=True)

    # 1. Straight Flush
    for suit, suited_cards in suit_groups.items():
        if len(suited_cards) >= 5:
            suited_ranks = [rank for _, rank in suited_cards]
            top_rank, straight_ranks = is_straight(suited_ranks)
            if top_rank:
                best_cards = [card for r in straight_ranks for card in suited_cards if card[1] == r]
                best_cards = sorted(set(best_cards), key=lambda x: x[1], reverse=True)[:5]
                return ("Straight Flush", top_rank, best_cards) if return_best_cards else ("Straight Flush", top_rank)

    # 2. Four of a Kind
    four_kind = [r for r, v in rank_counts.items() if len(v) == 4]
    if four_kind:
        fk = max(four_kind)
        kicker = max([c for c in cards if c[1] != fk], key=lambda x: x[1])
        chosen = rank_counts[fk] + [kicker]
        return ("Four of a Kind", fk, chosen) if return_best_cards else ("Four of a Kind", fk)

    # 3. Full House
    three_kind = [r for r, v in rank_counts.items() if len(v) == 3]
    pairs = [r for r, v in rank_counts.items() if len(v) == 2]
    if three_kind and (pairs or len(three_kind) >= 2):
        tk = max(three_kind)
        pr = max(pairs) if pairs else max([r for r in three_kind if r != tk])
        chosen = rank_counts[tk][:3] + rank_counts[pr][:2]
        return ("Full House", tk, chosen) if return_best_cards else ("Full House", tk)

    # 4. Flush
    for suit, suited_cards in suit_groups.items():
        if len(suited_cards) >= 5:
            best_cards = sorted(suited_cards, key=lambda x: x[1], reverse=True)[:5]
            return ("Flush", best_cards[0][1], best_cards) if return_best_cards else ("Flush", best_cards[0][1])

    # 5. Straight
    top_rank, straight_ranks = is_straight(all_ranks)
    if top_rank:
        chosen = []
        for r in straight_ranks:
            for c in cards:
                if c[1] == r and c not in chosen:
                    chosen.append(c)
                    break
        return ("Straight", top_rank, chosen[:5]) if return_best_cards else ("Straight", top_rank)

    # 6. Three of a Kind
    if three_kind:
        tk = max(three_kind)
        kickers = sorted([c for c in cards if c[1] != tk], key=lambda x: x[1], reverse=True)[:2]
        chosen = rank_counts[tk] + kickers
        return ("Three of a Kind", tk, chosen) if return_best_cards else ("Three of a Kind", tk)

    # 7. Two Pairs
    if len(pairs) >= 2:
        top2 = sorted(pairs, reverse=True)[:2]
        kicker = max([c for c in cards if c[1] not in top2], key=lambda x: x[1])
        chosen = rank_counts[top2[0]][:2] + rank_counts[top2[1]][:2] + [kicker]
        return ("Two Pairs", top2[0], chosen) if return_best_cards else ("Two Pairs", top2[0])

    # 8. One Pair
    if pairs:
        pr = max(pairs)
        kickers = sorted([c for c in cards if c[1] != pr], key=lambda x: x[1], reverse=True)[:3]
        chosen = rank_counts[pr] + kickers
        return ("One Pair", pr, chosen) if return_best_cards else ("One Pair", pr)

    # 9. High Card
    top5 = sorted(cards, key=lambda x: x[1], reverse=True)[:5]
    return ("High Card", top5[0][1], top5) if return_best_cards else ("High Card", top5[0][1])

