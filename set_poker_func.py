# import package
# basic
import random
import math
import scipy.stats as st


'''
including function : 
* generate_deck(shuffled=True)
* get_hand_label(card1, card2)
* hand_to_code_all()
* hand_to_code(hand)
* code_to_hand(hand_code)
* simulate_simple_game(my_hand=None, opponent_hand=None)
* simulate_detail_game(my_hand, community_card=None, opponent_num=1, opponent_hands_or_vpip=[100], epoch=10000, street="preflop")
* find_epoch_inCI(my_hand, community_card, opp_num, opp_hand_or_vpip, street, without_spec_enemy,
                    target_confidence=0.95, epsilon=0.02, max_epoch=10000, simulate_batch=30, show_log=True)
* 
* 

'''

# def generate deck
def generate_deck(shuffled=True):
    # def poker with rank & suit
    suits = ['spade', 'heart', 'diamond', 'club']
    ranks = [str(i) for i in range(2, 10)] + ['T','J', 'Q', 'K', 'A']
    # generate a poker deck
    deck = [(suit, rank) for suit in suits for rank in ranks]
    if shuffled:
        random.shuffle(deck)
    return deck

# let hand into realize
def get_hand_label(card1, card2):
    from judge_hands_func import rank_map
    r1, r2 = card1[1], card2[1]
    s1, s2 = card1[0], card2[0]
    if r1 == r2:  
        # pair
        return r1 + r2
    else:
        # high is in front
        if rank_map[r1] > rank_map[r2]:
            high, low = r1, r2
        else:
            high, low = r2, r1

        # suited or offsuit
        suited_flag = "s" if s1 == s2 else "o"
        return high + low + suited_flag


# generat all unique hands
# change [("spade", "A"), ("spade", "K")] into AKs
def hand_to_code_all():
    from judge_hands_func import rank_map
    unique_hands = []
    for i, r1 in enumerate(rank_map):
        for j, r2 in enumerate(rank_map):
            # not loop (A, K), (K, A)
            if i < j:
                # suit
                unique_hands.append([('spade', r1), ('spade', r2)])
                # not suit
                unique_hands.append([('spade', r1), ('heart', r2)])
            # pair
            elif i == j:
                unique_hands.append([('spade', r1), ('heart', r2)])
    return unique_hands



# change [("spade", "A"), ("spade", "K")] into AKs
def hand_to_code(hand):
    from judge_hands_func import rank_map
    ranks = [h[1] for h in hand]
    suits = [h[0] for h in hand]
    r1, r2 = ranks
    # suit or not
    suited = "s" if suits[0] == suits[1] else "o"
    # sort by rank
    if rank_map[r1] < rank_map[r2]:
        r1, r2 = r2, r1
    # if pair
    if r1 == r2:
        return f"{r1}{r2}"
    return f"{r1}{r2}{suited}"



# change AKs into [("spade", "A"), ("spade", "K")]
def code_to_hand(hand_code):
    suits = ['spade', 'heart', 'diamond', 'club']
    # pair
    if len(hand_code) == 2:
        rank = hand_code[0]
        # random suit
        selected_suits = random.sample(suits, 2)
        card1 = (selected_suits[0], rank)
        card2 = (selected_suits[1], rank)
        return [card1, card2]

    # not pair
    r1, r2 = hand_code[0], hand_code[1]
    suited = hand_code.endswith("s")
    offsuit = hand_code.endswith("o")

    # random suit
    if suited:
        chosen_suit = random.choice(suits)
        card1 = (chosen_suit, r1)
        card2 = (chosen_suit, r2)
    elif offsuit:
        chosen_suits = random.sample(suits, 2)
        card1 = (chosen_suits[0], r1)
        card2 = (chosen_suits[1], r2)
    return [card1, card2]




# simuate one game
def simulate_simple_game(my_hand=None, opponent_hand=None):
    from compete_hands import compare_hands
    # set deck
    deck = generate_deck(shuffled=True)

    # set up hands
    # if not specify, get random
    if my_hand is None:
        my_hand = deck[:2]
        del deck[:2]
    else:
        for card in my_hand:
            deck.remove(card)

    if opponent_hand is None:
        opponent_hand = deck[:2]
        del deck[:2]
    else:
        for card in opponent_hand:
            deck.remove(card)

    # show hands
    print(f"my hand : {my_hand}")
    print(f"enemy hand : {opponent_hand}")

    # get community card, list out
    community_cards = []

    # Preflop

    # Flop, community card
    flop = deck[:3]
    del deck[:3]
    community_cards += flop
    print(f"\n Flop : {flop}")
    winner_now, _ = compare_hands(my_hand, opponent_hand, community_cards)
    print(f"Current Leader : {winner_now}")

    # Turn, community card
    turn = deck[0]
    del deck[:1]
    community_cards.append(turn)
    print(f"\n Turn : {turn}")
    winner_now, _ = compare_hands(my_hand, opponent_hand, community_cards)
    print(f"Current Leader : {winner_now}")

    # River, community card
    river = deck[0]
    del deck[:1]
    community_cards.append(river)
    print(f"\n River : {river}")
    winner_now, _ = compare_hands(my_hand, opponent_hand, community_cards)
    print(f"Current Leader : {winner_now}")

    # final
    final_winner, detail = compare_hands(my_hand, opponent_hand, community_cards)
    print("\n final result")
    print(f"winner : {final_winner}")
    print(f"hand type : {detail['hand_type']}")
    print(f"composition : {detail['best_hand']}")

    return final_winner, detail




# simulate game detaily
def simulate_detail_game(my_hand, community_card=None, opponent_num=1, opponent_hands_or_vpip=(100), epoch=10000, street="preflop",
    without_spec_enemy=None):
    # import package
    from preflop_func import vpip_range, build_preflop_winrate_df
    from compete_hands import evaluate_hand, get_hand_score
    # build df
    for i in range(1, 10):
        globals()[f"preflop_winrate_df_{i}"] = build_preflop_winrate_df(
            opponent_num=i,
            save_path=f"preflop_sim_result/preflop_enemy_{i}.csv",
            simulate=False
        )
    # set preflop_winrate_df
    preflop_df_dict = {i: globals()[f"preflop_winrate_df_{i}"] for i in range(1, 10)}
    preflop_df = preflop_df_dict.get(opponent_num)

    # if not fill in, all compete
    if without_spec_enemy is None:
        without_spec_enemy = [1] * opponent_num
    if len(without_spec_enemy) != opponent_num:
        raise ValueError("without_spec_enemy length must equal opponent_num")
    
    # init count
    win_count, tie_count = 0, 0
    # set all prob hands
    all_hands = vpip_range(preflop_df, 100)["hand"].tolist()

    # repeat
    for _ in range(epoch):
        # init deck
        deck = generate_deck()
        for card in my_hand:
            deck.remove(card)

        # enemy hand
        current_opponent_hands = []
        # if list--get hands
        if isinstance(opponent_hands_or_vpip, list):
            for opp_hand in opponent_hands_or_vpip:
                if all(c in deck for c in opp_hand):
                    for c in opp_hand:
                        deck.remove(c)
                    current_opponent_hands.append(opp_hand)
                else:
                    raise ValueError(f"card {opp_hand} is not in deck")
                

        # if value--use vpip to random get hand from vpip_df
        elif isinstance(opponent_hands_or_vpip, tuple):
            for i in range(opponent_num):
                vpip_df = vpip_range(preflop_df, opponent_hands_or_vpip[i])
                candidate_hands_vpip = vpip_df["hand"].tolist()
                
                # get enemy's hand not include in vpip
                if without_spec_enemy[i] == 0:
                    candidate_hands = list(set(all_hands) - set(candidate_hands_vpip))
                else:
                    candidate_hands = candidate_hands_vpip

                while True:
                    hand_code = random.choice(candidate_hands)
                    opp_hand = code_to_hand(hand_code)
                    # del card
                    if all(c in deck for c in opp_hand):
                        for c in opp_hand:
                            deck.remove(c)
                        current_opponent_hands.append(opp_hand)
                        break
        
        # else--random
        else:
            for _ in range(opponent_num):
                hand = random.sample(deck, 2)
                for c in hand:
                    deck.remove(c)
                current_opponent_hands.append(hand)

        # set board--random
        if street == "preflop":
            if community_card is not None:
                raise ValueError("preflop street have no community cards")
            board = random.sample(deck, 5)
        elif street == "flop":
            if community_card is None or len(community_card) != 3:
                raise ValueError("flop street requires 3 community cards")
            board = community_card + random.sample(deck, 2)
        elif street == "turn":
            if community_card is None or len(community_card) != 4:
                raise ValueError("turn street requires 4 community cards")
            board = community_card + random.sample(deck, 1)
        elif street == "river":
            if community_card is None or len(community_card) != 5:
                raise ValueError("river street requires 5 community cards")
            board = community_card  # no new card to draw
        else:
            raise ValueError("street must be one of 'preflop', 'flop', 'turn', 'river'")

        # get my_hand score
        my_result = evaluate_hand(my_hand + board, return_best_cards=True)
        my_score = get_hand_score(my_result)

        # get enemy_hand score
        enemy_scores = []
        for hand, exclude_flag in zip(current_opponent_hands, without_spec_enemy):
            result = evaluate_hand(hand + board, return_best_cards=True)
            score = get_hand_score(result)
            # when 0, get in compete
            if exclude_flag == 1:
                enemy_scores.append(score)

        # find winner
        max_score = max(enemy_scores + [my_score])
        winners = [s for s in enemy_scores + [my_score] if s == max_score]

        if my_score == max_score and len(winners) == 1:
            win_count += 1
        elif my_score == max_score:
            tie_count += 1
    # count rate
    win_rate = round(win_count / epoch, 4)
    tie_rate = round(tie_count / epoch, 4)
    return my_hand, community_card, win_rate, tie_rate, opponent_hands_or_vpip if opponent_hands_or_vpip else "random"





# find least simulating epoch
def find_epoch_inCI(my_hand, community_card, opp_num, opp_hand_or_vpip, street, without_spec_enemy,
                    target_confidence=0.95, epsilon=0.02, max_epoch=10000, simulate_batch=30, show_log=True):

    # use target CI to find z value
    ## 95% CI--> z = 1.96
    alpha = 1 - target_confidence
    z = st.norm.ppf(1 - alpha / 2)

    wins = 0
    checked = 0 

    # by CLT
    # n >= \frac{z^{2}_{2/a} * p * (1-p)}{e^2}
    # but p unknow --> set p = 0.5 is maxium
    upper_bound_epoch = math.ceil((z ** 2) * 0.25 / (epsilon ** 2))
    if show_log:
        print(f"CI : {target_confidence*100:.1f}% → z={z:.3f}")
        print(f"theorical : need at least {upper_bound_epoch} epoch to reach ±{epsilon*100:.1f}% accuracy\n")

    for i in range(1, max_epoch + 1):
        # simulate
        _, _, win_rate, _, _ = simulate_detail_game(
            my_hand=my_hand,
            community_card=community_card,
            opponent_num=opp_num,
            opponent_hands_or_vpip=opp_hand_or_vpip,
            epoch=simulate_batch,
            street=street,
            without_spec_enemy=without_spec_enemy
        )
        wins += win_rate
        checked += 1

        # checking after every 50 epoch 
        if i % 50 == 0:
            # p hat
            p_hat = wins / checked
            se = math.sqrt(p_hat * (1 - p_hat) / checked)
            margin = z * se
            # show log
            if show_log:
                print(f"Epoch={checked:5d}, estimate win rate p̂={p_hat:.3f}, with {int(target_confidence*100)}%CI ±{margin:.3f} epsilon")

            if margin <= epsilon:
                if show_log:
                    print(f"\ncomplete converge {target_confidence*100:.1f}% CI with epsilon ±{margin:.3f} ≦ ±{epsilon:.3f}")
                    print(f"simulating epochs : {checked}, estimate win rate ≈ {p_hat:.4f}")
                return checked

    # if not meet epsilon
    p_hat = wins / checked
    se = math.sqrt(p_hat * (1 - p_hat) / checked)
    margin = z * se
    if show_log:
        print(f"\n not converge : meet max simulating times : {checked}, {int(target_confidence*100)}%CI=±{margin:.3f} (target : ±{epsilon:.3f})")
        print(f"estimate win rate ≈{p_hat:.4f}")

    return checked
