import random
import os
import pandas as pd
import math
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib import colors

'''
including function : 
* simulate_preflop(my_hand, opponent_num=1, opponent_hands_or_vpip=None, epoch=10000)
* build_preflop_winrate_df(opponent_num=1, epoch=None, save_path=None, simulate=True)
* sort_preflop_df(preflop_winrate_df, value_col="win_rate")
* vpip_range(preflop_df, vpip)
* plot_preflop_heatmap_vpip(preflop_winrate_df, vpip=100, value_col="win_rate", vpip_dict=None)
* 
* 

'''

# simulate preflop
def simulate_preflop(my_hand, opponent_num=1, opponent_hands_or_vpip=None, epoch=10000):
    from set_poker_func import generate_deck, code_to_hand
    from judge_hands_func import evaluate_hand, get_hand_score
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

    # init count
    win_count, tie_count = 0, 0

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
                candidate_hands = vpip_df["hand"].tolist()
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

        # game start
        board = random.sample(deck, 5)

        # get my score 
        my_result = evaluate_hand(my_hand + board, return_best_cards=True)
        my_score = get_hand_score(my_result)

        # get enemys score
        enemy_scores = []
        for hand in current_opponent_hands:
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

    return my_hand, win_rate, tie_rate, opponent_hands_or_vpip if opponent_hands_or_vpip else "random", opponent_num



# def build preflop winrate df
def build_preflop_winrate_df(opponent_num=1, epoch=None, save_path=None, simulate=True):
    from set_poker_func import hand_to_code, get_hand_label
    old_df = None
    # if there are old data, load
    if save_path and os.path.exists(save_path):
        old_df = pd.read_csv(save_path)
        # check same enemy
        if "opponent_num" in old_df.columns:
            if int(old_df["opponent_num"].iloc[0]) != opponent_num:
                raise ValueError(f"file opponent number : ({old_df['opponent_num'].iloc[0]}) \
                             is not equal to ({opponent_num}), please use new path")
        else:
            old_df["opponent_num"] = opponent_num
            old_df["total_epoch"] = 0

    # if not simulate, call old data
    if not simulate:
        if old_df is None:
            raise FileNotFoundError("no data to load, please simulate")
        return old_df

    if epoch is None:
        raise ValueError("when simulate=True, must fill in epoch")

    # ensure directory exists if save_path is provided
    if save_path:
        save_dir = os.path.dirname(save_path)
        if save_dir and not os.path.exists(save_dir):
            os.makedirs(save_dir, exist_ok=True)

    # new simulate
    new_records = []
    for hand in hand_to_code():
        label = get_hand_label(hand[0], hand[1])
        _, win_rate, tie_rate, _, _ = simulate_preflop(my_hand=hand, opponent_num=opponent_num, opponent_hands_or_vpip=None, epoch=epoch)
        new_records.append({
            "hand": label,
            "win_rate": win_rate,
            "tie_rate": tie_rate,
            "total_epoch": epoch,
            "opponent_num": opponent_num
        })
    new_df = pd.DataFrame(new_records)

    # if there are old data, combine
    if old_df is not None:
        merged = pd.merge(old_df, new_df, on="hand", suffixes=("_old", "_new"))
        merged["win_rate"] = (
            merged["win_rate_old"] * merged["total_epoch_old"] +
            merged["win_rate_new"] * merged["total_epoch_new"]
        ) / (merged["total_epoch_old"] + merged["total_epoch_new"])

        merged["tie_rate"] = (
            merged["tie_rate_old"] * merged["total_epoch_old"] +
            merged["tie_rate_new"] * merged["total_epoch_new"]
        ) / (merged["total_epoch_old"] + merged["total_epoch_new"])

        merged["total_epoch"] = merged["total_epoch_old"] + merged["total_epoch_new"]
        merged["opponent_num"] = opponent_num

        df = merged[["hand", "win_rate", "tie_rate", "total_epoch", "opponent_num"]].copy()
    else:
        df = new_df.copy()

    # save
    if save_path:
        df.to_csv(save_path, index=False)

    return df




# sort preflop df
def sort_preflop_df(preflop_winrate_df, value_col="win_rate"):
    return preflop_winrate_df.sort_values(by=value_col, ascending=False).reset_index(drop=True)



# get vpip range
def vpip_range(preflop_df, vpip):
    sorted_df = sort_preflop_df(preflop_df)
    n = math.ceil(len(sorted_df) * vpip / 100)
    return sorted_df.head(n).copy()



# def function of plot preflop heatmap
def plot_preflop_heatmap_vpip(
    preflop_winrate_df,
    vpip=100,
    value_col="win_rate",
    vmin=None,
    vmax=None,
    vcenter=None,
    cmap_colors=["green", "yellow", "red"],
    vpip_dict=None
):
    """
    if vpip_dict is None : 
        use vpip
    elif vpip is Not None : 
        show all winrate heatmap
        show points of all position
    """
    from judge_hands_func import rank_map
    # position option setting
    position_colors = {
        "SB": "red",
        "BB": "orange",
        "UTG": "yellow",
        "MP": "green",
        "CO": "blue",
        "BTN": "purple",
    }
    position_offsets = {
        "UTG": (0.25, -0.25),
        "MP": (0.25, 0.25),
        "CO": (0.0, 0.35),
        "BTN": (-0.25, 0.25),
        "SB": (-0.25, -0.25),
        "BB": (0.0, -0.35),
    }

    # get ranks
    ranks = sorted(rank_map.keys(), key=lambda x: rank_map[x], reverse=True)
    heatmap_matrix = pd.DataFrame(np.nan, index=ranks, columns=ranks)
    labels_matrix = pd.DataFrame("", index=ranks, columns=ranks)

    # fill all winrate and label
    for _, row in preflop_winrate_df.iterrows():
        hand = row["hand"]
        winrate = row[value_col]
        label_text = f"{hand}\n{winrate*100:.1f}%"
        # pocket
        if len(hand) == 2:
            r, c = hand[0], hand[0]
        else:
            r, c = (hand[0], hand[1]) if hand.endswith("s") else (hand[1], hand[0])
        if (r in ranks) and (c in ranks):
            heatmap_matrix.loc[r, c] = winrate
            labels_matrix.loc[r, c] = label_text

    # if no vpip_dict, show front vpip hands
    if vpip_dict is None:
        vpip_df = vpip_range(preflop_winrate_df, vpip)
        vpip_hands = set(vpip_df["hand"])

        for rr in ranks:
            for cc in ranks:
                label = labels_matrix.loc[rr, cc]
                if label == "":
                    continue
                hand = label.split("\n")[0]
                if hand not in vpip_hands:
                    heatmap_matrix.loc[rr, cc] = np.nan
                    labels_matrix.loc[rr, cc] = ""

    # set colormap & normalization
    cmap = colors.LinearSegmentedColormap.from_list("custom_cmap", cmap_colors)
    # matrix min/max (avoid NAN)
    try:
        mat_min = np.nanmin(heatmap_matrix.values)
        mat_max = np.nanmax(heatmap_matrix.values)
    except ValueError:
        mat_min, mat_max = 0.0, 1.0
    if np.isnan(mat_min) or np.isnan(mat_max):
        mat_min, mat_max = 0.0, 1.0
    if vcenter is not None:
        norm = colors.TwoSlopeNorm(
            vmin=vmin if vmin is not None else mat_min,
            vcenter=vcenter,
            vmax=vmax if vmax is not None else mat_max
        )
    else:
        norm = colors.Normalize(
            vmin=vmin if vmin is not None else mat_min,
            vmax=vmax if vmax is not None else mat_max
        )

    # plot
    plt.figure(figsize=(12, 10))
    ax = sns.heatmap(
        heatmap_matrix.astype(float),
        cmap=cmap,
        norm=norm,
        annot=labels_matrix, fmt="",
        linewidths=.5, linecolor="gray",
        cbar_kws={'label': 'Winrate'}
    )

    # if vpip_dict exist : show position points
    if vpip_dict is not None:
        for place, pct in vpip_dict.items():
            dx, dy = position_offsets.get(place, (0.0, 0.0))
            color = position_colors.get(place, None)
            if color is None:
                color = None
            vpip_df = vpip_range(preflop_winrate_df, pct)
            for _, row in vpip_df.iterrows():
                hand = row["hand"]
                if len(hand) == 2:
                    if hand[0] not in ranks:
                        continue
                    idx = ranks.index(hand[0])
                    x = idx + 0.5 + dx
                    y = idx + 0.5 + dy
                else:
                    r, c = (hand[0], hand[1]) if hand.endswith("s") else (hand[1], hand[0])
                    if (r not in ranks) or (c not in ranks):
                        continue
                    x = ranks.index(c) + 0.5 + dx
                    y = ranks.index(r) + 0.5 + dy

                ax.scatter(x, y, color=color, s=100, edgecolor="black", alpha=0.5)

        # show ticks & labels
        ax.set_xticks([i + 0.5 for i in range(len(ranks))])
        ax.set_yticks([i + 0.5 for i in range(len(ranks))])
        ax.set_xticklabels(ranks)
        ax.set_yticklabels(ranks)
        ax.set_xlabel("Second Card")
        ax.set_ylabel("First Card")
        ax.set_title("Preflop Winrate Heatmap with Position VPIP Points", fontsize=16)
        # legend
        for place, color in position_colors.items():
            ax.scatter([], [], color=color, label=place, s=100, edgecolor="black", alpha=0.8)
        ax.legend(title="Position", bbox_to_anchor=(1.25, 1), loc='upper left')

    else:
        # only show top N vpip
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_xlabel("")
        ax.set_ylabel("")
        ax.set_title(f"Preflop Winrate Heatmap (Top {len(vpip_df)} hands, VPIP={vpip}%)",
                     fontsize=16, pad=20)

    plt.show()


