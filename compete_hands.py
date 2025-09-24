# import package
## basic 
import random
## function
from set_poker_func import generate_deck
from judge_hands_func import evaluate_hand, get_hand_score


'''
including function : 
* compare_hands(my_hand, opponent_hand, community_cards)
* simple_compete(my_hand, opponent_hand, community_cards)
* simulate_preflop(my_hand, opponent_num=1, epoch=10000)
* 
* 
* 
* 

'''


# compare hands
def compare_hands(my_hand, opponent_hand, community_cards):
    my_result = evaluate_hand(my_hand + community_cards, return_best_cards=True)
    opp_result = evaluate_hand(opponent_hand + community_cards, return_best_cards=True)

    my_score = get_hand_score(my_result)
    opp_score = get_hand_score(opp_result)

    if my_score > opp_score:
        return "me", {
            "hand_type": my_result[0],
            "top_value": my_result[1],
            "best_hand": my_result[2]
        }
    elif opp_score > my_score:
        return "enemy", {
            "hand_type": opp_result[0],
            "top_value": opp_result[1],
            "best_hand": opp_result[2]
        }
    else:
        return "tie", {
            "hand_type": my_result[0],
            "top_value": my_result[1],
            "best_hand": my_result[2]
        }

# simple compete
def simple_compete(my_hand, opponent_hand, community_cards):
    my_result = evaluate_hand(my_hand + community_cards, return_best_cards=False)
    opp_result = evaluate_hand(opponent_hand + community_cards, return_best_cards=False)
    my_score = get_hand_score(my_result)
    opp_score = get_hand_score(opp_result)
    if my_score > opp_score:
        return "me"
    elif opp_score > my_score:
        return "enemy"
    else:
        return "tie"
    
# simulate preflop
def simulate_preflop(my_hand, opponent_num=1, epoch=10000):
    win_count = 0
    tie_count = 0

    for _ in range(epoch):
        # init deck
        deck = generate_deck()
        for card in my_hand:
            deck.remove(card)

        # enemy hand
        opponent_hand = []
        for _ in range(opponent_num):
            hand = random.sample(deck, 2)
            for c in hand:
                deck.remove(c)
            opponent_hand.append(hand)

        # game start
        board = random.sample(deck, 5)

        # get my score 
        my_result = evaluate_hand(my_hand + board, return_best_cards=True)
        my_score = get_hand_score(my_result)

        # get enemys score
        enemy_scores = []
        for hand in opponent_hand:
            result = evaluate_hand(hand + board, return_best_cards=True)
            enemy_scores.append(get_hand_score(result))

        # compare who win
        max_score = max(enemy_scores + [my_score])
        winners = [s for s in enemy_scores + [my_score] if s == max_score]

        if my_score == max_score and len(winners) == 1:
            win_count += 1
        elif my_score == max_score:
            tie_count += 1

    win_rate = round(win_count / epoch, 4)
    tie_rate = round(tie_count / epoch, 4)
    return my_hand, win_rate, tie_rate

