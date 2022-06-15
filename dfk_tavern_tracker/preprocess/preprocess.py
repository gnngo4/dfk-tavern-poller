import pandas as pd

def score_profession(profession,idx,df,simulate_lvl=100):
    """
    Score a hero based in a dataframe based on 
    the index (`idx`) and `profession`
    """

    assert simulate_lvl > 1

    # Define relevant profession stats
    if profession == 'mining':
        stat1 = 'strength'
        stat2 = 'endurance'
    elif profession == 'gardening':
        stat1 = 'wisdom'
        stat2 = 'vitality'
    elif profession == 'foraging':
        stat1 = 'dexterity'
        stat2 = 'intelligence'
    elif profession == 'fishing':
        stat1 = 'agility'
        stat2 = 'luck'
    else:
        NotImplemented

    # Get dataSeries
    hero_info = df.iloc[idx]
    # Get current level
    current_level = hero_info.level
    rarity = hero_info.rarity
    # Get level up info
    stat1_info = {}
    stat1_info['base'] = hero_info[stat1]
    stat1_info['extra'] = 0
    stat1_info['GrowthP'] = hero_info[f"{stat1}GrowthP"]/10_000.
    stat1_info['GrowthS'] = hero_info[f"{stat1}GrowthS"]/10_000.
    stat2_info = {}
    stat2_info['base'] = hero_info[stat2]
    stat2_info['GrowthP'] = hero_info[f"{stat2}GrowthP"]/10_000.
    stat2_info['GrowthS'] = hero_info[f"{stat2}GrowthS"]/10_000.
    # simulate scores
    for _lvl in range(current_level,simulate_lvl):
        # Level-up bonus
        stat1_info['base'] += 1. * (stat1_info['GrowthP']) # Increase stats based on rolls (GrowthP%)
        stat1_info['base'] += 1. * (stat1_info['GrowthS']) # Increase stats based on rolls (GrowthS%)
        stat2_info['base'] += 1. * (stat2_info['GrowthP']) # Increase stats based on rolls (GrowthP%)
        stat2_info['base'] += 1. * (stat2_info['GrowthS']) # Increase stats based on rolls (GrowthS%)
        stat1_info['extra'] += 1. # Increase stat by 1
        # Increase two other stats by 1 (50%)
        stat1_info['extra'] += 1. * (.5)
        stat1_info['extra'] += 1. * (.5) 
        if ( (_lvl+1) % 5 ) == 0:
            # +1 to two different stats
            if rarity == 1:
                # +1 to two different stats
                stat1_info['base'] += 1.
                stat2_info['base'] += 1.
            # +1 to three different stats, +1 to any stat
            elif rarity == 2:
                stat1_info['base'] += 1.
                stat2_info['base'] += 1.
                stat1_info['extra'] += 1.
            # +2 to one stat, +1 to three different stats, +1 to any stat
            elif rarity == 3:
                stat1_info['base'] += 1.
                stat2_info['base'] += 1.
                stat1_info['extra'] += 3.
            # +2 to three different stats, +1 to three different stats, +1 to any stat
            elif rarity == 4:
                stat1_info['base'] += 3.
                stat2_info['base'] += 3.
                stat1_info['extra'] += 1.
            else:
                pass
        
    # Get profession bonus
    if hero_info.profession == profession:
        return (stat1_info['base']+stat2_info['base']+stat1_info['extra'])*1.1
    else:
        return stat1_info['base']+stat2_info['base']+stat1_info['extra']

def score_professions(_df):
    n_rows = _df.shape[0]
    for _prof in ['mining','gardening','foraging','fishing']:
        for _sim_lvl in [100]:
            scores = []
            for r in range(n_rows):
                score = score_profession(_prof,r,_df,simulate_lvl=_sim_lvl)
                scores.append(score)
            _df[f"score_{_prof}_lvl{str(_sim_lvl).zfill(3)}"] = scores

    print(n_rows)

    return _df
