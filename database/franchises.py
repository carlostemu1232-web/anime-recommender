from collections import Counter, defaultdict
import re
import unicodedata


# Explicit relationships only. Unknown relationships stay separate.
FRANCHISE_GROUPS = {
    'attack_on_titan': {
        'name': 'Attack on Titan',
        'parts': {
            'attack_on_titan',
            'attack_on_titan_season_2',
            'attack_on_titan_season_3',
            'attack_on_titan_season_3_part_2',
            'attack_on_titan_final_season',
            'attack_on_titan_final_season_part_2',
            'attack_on_titan_final_season_the_final_chapters_special_1',
            'attack_on_titan_final_season_the_final_chapters_special_2',
            'attack_on_titan_ova',
            'attack_on_titan_lost_girls',
            'attack_on_titan_no_regrets'
        }
    },
    'naruto': {
        'name': 'Naruto',
        'parts': {'naruto', 'naruto_shippuden', 'boruto_naruto_next_generations'}
    },
    'dragon_ball': {
        'name': 'Dragon Ball',
        'parts': {'dragon_ball', 'dragon_ball_z', 'dragon_ball_super'}
    },
    'my_hero_academia': {
        'name': 'My Hero Academia',
        'parts': {'my_hero_academia', 'my_hero_academia_season_2'}
    },
    're_zero': {
        'name': 'Re:ZERO',
        'parts': {
            're_zero',
            're_zero_starting_life_in_another_world',
            're_zero_starting_life_in_another_world_season_2',
            're_zero_starting_life_in_another_world_season_2_part_2',
            're_zero_starting_life_in_another_world_season_3',
            're_zero_starting_life_in_another_world_season_4',
            're_zero_starting_life_in_another_world_ovas'
        }
    },
    'fate': {
        'name': 'Fate',
        'parts': {'fate_zero', 'fate_stay_night'}
    },
    'magi': {
        'name': 'Magi',
        'parts': {'magi_labyrinth_of_magic', 'magi_kingdom_of_magic'}
    },
    'mobile_suit_gundam': {
        'name': 'Mobile Suit Gundam',
        'parts': {'mobile_suit_gundam', 'mobile_suit_gundam_00'}
    },
    'mushoku_tensei': {
        'name': 'Mushoku Tensei',
        'parts': {
            'mushoku_tensei',
            'mushoku_tensei_jobless_reincarnation_cour_2',
            'mushoku_tensei_jobless_reincarnation_cour_2_eris_the_goblin_slayer',
            'mushoku_tensei_jobless_reincarnation_season_2',
            'mushoku_tensei_jobless_reincarnation_season_2_part_2',
            'mushoku_tensei_jobless_reincarnation_season_3'
        }
    },
    'frieren': {
        'name': "Frieren: Beyond Journey's End",
        'parts': {
            'frieren',
            'frieren_beyond_journey_s_end',
            'frieren_beyond_journey_s_end_season_2'
        }
    },
    'jojo': {
        'name': "JoJo's Bizarre Adventure",
        'parts': {
            'jojos_bizarre_adventure',
            'jojo_s_bizarre_adventure_tv',
            'jojo_s_bizarre_adventure_stardust_crusaders',
            'jojo_s_bizarre_adventure_stardust_crusaders_battle_in_egypt',
            'jojo_s_bizarre_adventure_diamond_is_unbreakable',
            'jojo_s_bizarre_adventure_golden_wind',
            'jojo_s_bizarre_adventure_stone_ocean',
            'jojo_s_bizarre_adventure_stone_ocean_part_2'
        }
    }
}

FRANCHISE_GROUPS.update({
    'assassination_classroom': {
        'name': 'Assassination Classroom',
        'parts': {'assassination_classroom', 'assassination_classroom_second_season'}
    },
    'black_lagoon': {
        'name': 'Black Lagoon',
        'parts': {'black_lagoon', 'black_lagoon_the_second_barrage'}
    },
    'call_of_the_night': {
        'name': 'Call of the Night',
        'parts': {'call_of_the_night', 'call_of_the_night_season_2'}
    },
    'chainsaw_man': {
        'name': 'Chainsaw Man',
        'parts': {'chainsaw_man', 'chainsaw_man_the_movie_reze_arc'}
    },
    'cowboy_bebop': {
        'name': 'Cowboy Bebop',
        'parts': {'cowboy_bebop', 'cowboy_bebop_the_movie_knockin_on_heaven_s_door'}
    },
    'demon_slayer': {
        'name': 'Demon Slayer',
        'parts': {'demon_slayer', 'demon_slayer_kimetsu_no_yaiba_the_movie_mugen_train'}
    },
    'durarara': {
        'name': 'Durarara!!',
        'parts': {
            'durarara',
            'durarara_x2_the_second_arc',
            'durarara_x2_the_third_arc'
        }
    },
    'fate_zero': {
        'name': 'Fate/Zero',
        'parts': {'fate_zero', 'fate_zero_season_2'}
    },
    'fate_stay_night': {
        'name': 'Fate/stay night: Unlimited Blade Works',
        'parts': {
            'fate_stay_night',
            'fate_stay_night_unlimited_blade_works_2nd_season'
        }
    },
    'food_wars': {
        'name': 'Food Wars!',
        'parts': {
            'food_wars',
            'food_wars_the_second_plate',
            'food_wars_the_third_plate',
            'food_wars_the_third_plate_totsuki_train_arc',
            'food_wars_the_fourth_plate',
            'food_wars_the_fifth_plate'
        }
    },
    'given': {
        'name': 'Given',
        'parts': {'given', 'given_the_movie'}
    },
    'kaguya_sama': {
        'name': 'Kaguya-sama: Love Is War',
        'parts': {
            'kaguya_sama',
            'kaguya_sama_wa_kokurasetai_tensaitachi_no_renai_zunousen_ova',
            'kaguya_sama_love_is_war',
            'kaguya_sama_love_is_war_the_first_kiss_that_never_ends',
            'kaguya_sama_love_is_war_ultra_romantic'
        }
    },
    'kimi_ni_todoke': {
        'name': 'Kimi ni Todoke',
        'parts': {'kimi_ni_todoke', 'kimi_ni_todoke_from_me_to_you_season_2'}
    },
    'komi_can_t_communicate': {
        'name': "Komi Can't Communicate",
        'parts': {'komi_can_t_communicate', 'komi_can_t_communicate_part_2'}
    },
    'k_on': {
        'name': 'K-On!',
        'parts': {'k_on', 'k_on_season_2', 'k_on_the_movie'}
    },
    'my_dress_up_darling': {
        'name': 'My Dress-Up Darling',
        'parts': {'my_dress_up_darling', 'my_dress_up_darling_season_2'}
    },
    'relife': {
        'name': 'ReLIFE',
        'parts': {'relife', 'relife_final_arc'}
    },
    'rent_a_girlfriend': {
        'name': 'Rent-a-Girlfriend',
        'parts': {'rent_a_girlfriend', 'rent_a_girlfriend_season_2'}
    },
    'shangri_la_frontier': {
        'name': 'Shangri-La Frontier',
        'parts': {'shangri_la_frontier', 'shangri_la_frontier_season_2'}
    },
    'snow_white_with_the_red_hair': {
        'name': 'Snow White with the Red Hair',
        'parts': {'snow_white_with_the_red_hair', 'snow_white_with_the_red_hair_season_2'}
    },
    'steins_gate': {
        'name': 'Steins;Gate',
        'parts': {'steins_gate', 'steins_gate_the_movie_load_region_of_d_j_vu'}
    },
    '86_eighty_six': {
        'name': '86 Eighty-Six',
        'parts': {'86_eighty_six', '86_eighty_six_part_2'}
    },
    'arifureta': {
        'name': 'Arifureta',
        'parts': {
            'arifureta',
            'arifureta_from_commonplace_to_world_s_strongest_season_2'
        }
    },
    'beastars': {
        'name': 'BEASTARS',
        'parts': {'beastars', 'beastars_season_2'}
    },
    'blue_lock': {
        'name': 'BLUE LOCK',
        'parts': {'blue_lock', 'blue_lock_season_2'}
    },
    'bofuri': {
        'name': "BOFURI: I Don't Want to Get Hurt",
        'parts': {
            'bofuri_i_don_t_want_to_get_hurt_so_i_ll_max_out_my_defense',
            'bofuri_i_don_t_want_to_get_hurt_so_i_ll_max_out_my_defense_season_2'
        }
    },
    'classroom_of_the_elite': {
        'name': 'Classroom of the Elite',
        'parts': {
            'classroom_of_the_elite',
            'classroom_of_the_elite_season_2',
            'classroom_of_the_elite_season_3',
            'classroom_of_the_elite_4th_season_second_year_first_semester'
        }
    },
    'dan_da_dan': {
        'name': 'DAN DA DAN',
        'parts': {'dan_da_dan', 'dan_da_dan_season_2'}
    },
    'dr_stone': {
        'name': 'Dr. STONE',
        'parts': {
            'dr_stone',
            'dr_stone_new_world_part_2',
            'dr_stone_science_future_cour_2',
            'dr_stone_special_episode_ryusui'
        }
    },
    'fairy_tail': {
        'name': 'Fairy Tail',
        'parts': {'fairy_tail', 'fairy_tail_final_season'}
    },
    'fire_force': {
        'name': 'Fire Force',
        'parts': {
            'fire_force',
            'fire_force_season_2',
            'fire_force_season_3',
            'fire_force_season_3_part_2'
        }
    },
    'fruits_basket': {
        'name': 'Fruits Basket',
        'parts': {
            'fruits_basket',
            'fruits_basket_season_2',
            'fruits_basket_the_final_season'
        }
    },
    'gintama': {
        'name': 'Gintama',
        'parts': {
            'gintama',
            'gintama_season_2',
            'gintama_season_2_part_2',
            'gintama_season_3',
            'gintama_season_4'
        }
    },
    'haikyuu': {
        'name': 'Haikyu!!',
        'parts': {'haikyuu', 'haikyu_to_the_top_part_2'}
    },
    'jujutsu_kaisen': {
        'name': 'Jujutsu Kaisen',
        'parts': {
            'jujutsu_kaisen',
            'jujutsu_kaisen_season_2',
            'jujutsu_kaisen_season_3_the_culling_game_part_1'
        }
    },
    'k_on': {
        'name': 'K-On!',
        'parts': {'k_on', 'k_on_season_2', 'k_on_the_movie'}
    },
    'kizumonogatari': {
        'name': 'Kizumonogatari',
        'parts': {
            'kizumonogatari_part_1_tekketsu',
            'kizumonogatari_part_2_nekketsu',
            'kizumonogatari_part_3_reiketsu'
        }
    },
    'mashle': {
        'name': 'MASHLE: MAGIC AND MUSCLES',
        'parts': {'mashle_magic_and_muscles', 'mashle_magic_and_muscles_season_2'}
    },
    'march_comes_in_like_a_lion': {
        'name': 'March Comes in Like a Lion',
        'parts': {'march_comes_in_like_a_lion', 'march_comes_in_like_a_lion_season_2'}
    },
    'my_hero_academia': {
        'name': 'My Hero Academia',
        'parts': {
            'my_hero_academia',
            'my_hero_academia_season_2',
            'my_hero_academia_season_3',
            'my_hero_academia_season_4',
            'my_hero_academia_season_5',
            'my_hero_academia_season_6',
            'my_hero_academia_season_7',
            'my_hero_academia_final_season'
        }
    },
    'oshi_no_ko': {
        'name': 'OSHI NO KO',
        'parts': {'oshi_no_ko', 'oshi_no_ko_season_2', 'oshi_no_ko_season_3'}
    },
    'one_punch_man': {
        'name': 'One-Punch Man',
        'parts': {'one_punch_man', 'one_punch_man_season_2', 'one_punch_man_season_3'}
    },
    'spy_x_family': {
        'name': 'SPY x FAMILY',
        'parts': {
            'spy_x_family',
            'spy_x_family_cour_2',
            'spy_x_family_season_2',
            'spy_x_family_season_3'
        }
    },
    'solo_leveling': {
        'name': 'Solo Leveling',
        'parts': {'solo_leveling', 'solo_leveling_season_2_arise_from_the_shadow'}
    },
    'sword_art_online': {
        'name': 'Sword Art Online',
        'parts': {
            'sword_art_online',
            'sword_art_online_the_movie_progressive_aria_of_a_starless_night',
            'sword_art_online_the_movie_ordinal_scale',
            'sword_art_online_alicization_war_of_underworld_part_2'
        }
    },
    'tsukimichi': {
        'name': 'TSUKIMICHI -Moonlit Fantasy-',
        'parts': {
            'tsukimichi',
            'tsukimichi_moonlit_fantasy',
            'tsukimichi_moonlit_fantasy_season_2'
        }
    },
    'saga_of_tanya': {
        'name': 'Saga of Tanya the Evil',
        'parts': {
            'saga_of_tanya',
            'saga_of_tanya_the_evil',
            'saga_of_tanya_the_evil_the_movie',
            'saga_of_tanya_the_evil_season_2'
        }
    }
})

ADDITIONAL_PARTS = {
    'monogatari': {
        'name': 'Monogatari Series',
        'parts': {
            'bakemonogatari',
            'hanamonogatari',
            'kizumonogatari_part_1_tekketsu',
            'kizumonogatari_part_2_nekketsu',
            'kizumonogatari_part_3_reiketsu',
            'koyomimonogatari',
            'monogatari_series_second_season',
            'nekomonogatari_black',
            'nisemonogatari',
            'owarimonogatari',
            'owarimonogatari_second_season',
            'tsukimonogatari',
            'zoku_owarimonogatari'
        }
    },
    'puella_magi_madoka_magica': {
        'name': 'Puella Magi Madoka Magica',
        'parts': {
            'puella_magi_madoka_magica',
            'puella_magi_madoka_magica_the_movie_rebellion'
        }
    },
    'naruto': {
        'name': 'Naruto',
        'parts': {
            'naruto',
            'naruto_shippuden',
            'boruto_naruto_next_generations',
            'boruto_naruto_the_movie',
            'the_last_naruto_the_movie'
        }
    },
    'haikyuu': {
        'name': 'Haikyu!!',
        'parts': {
            'haikyuu',
            'haikyu_2nd_season',
            'haikyu_3rd_season',
            'haikyu_to_the_top_part_2'
        }
    },
    'natsume_book_of_friends': {
        'name': "Natsume's Book of Friends",
        'parts': {'natsume_book_of_friends', 'natsume_s_book_of_friends_season_1'}
    },
    'that_time_i_got_reincarnated_as_a_slime': {
        'name': 'That Time I Got Reincarnated as a Slime',
        'parts': {
            'tensei_slime',
            'that_time_i_got_reincarnated_as_a_slime_season_2',
            'that_time_i_got_reincarnated_as_a_slime_season_2_part_2',
            'that_time_i_got_reincarnated_as_a_slime_season_3',
            'that_time_i_got_reincarnated_as_a_slime_season_4',
            'that_time_i_got_reincarnated_as_a_slime_the_movie_scarlet_bond'
        }
    },
    'devil_is_part_timer': {
        'name': 'The Devil Is a Part-Timer!',
        'parts': {'devil_is_part_timer', 'the_devil_is_a_part_timer_season_2'}
    },
    'eminence_in_shadow': {
        'name': 'The Eminence in Shadow',
        'parts': {'eminence_in_shadow', 'the_eminence_in_shadow_season_2'}
    },
    'rising_shield_hero': {
        'name': 'The Rising of the Shield Hero',
        'parts': {
            'rising_shield_hero',
            'the_rising_of_the_shield_hero_season_2',
            'the_rising_of_the_shield_hero_season_3'
        }
    },
    'we_never_learn': {
        'name': 'We Never Learn!',
        'parts': {'we_never_learn_bokuben', 'we_never_learn_bokuben_season_2'}
    },
    'hells_paradise': {
        'name': "Hell's Paradise",
        'parts': {'hells_paradise', 'hell_s_paradise_season_2'}
    },
    'is_it_wrong_to_try_to_pick_up_girls_in_a_dungeon': {
        'name': 'Is It Wrong to Try to Pick Up Girls in a Dungeon?',
        'parts': {
            'is_it_wrong_to_try_to_pick_up_girls_in_a_dungeon',
            'is_it_wrong_to_try_to_pick_up_girls_in_a_dungeon_iv_part_2'
        }
    },
    'how_a_realist_hero_rebuilt_the_kingdom': {
        'name': 'How a Realist Hero Rebuilt the Kingdom',
        'parts': {
            'how_a_realist_hero_rebuilt_the_kingdom',
            'how_a_realist_hero_rebuilt_the_kingdom_part_2'
        }
    },
    'moriarty_the_patriot': {
        'name': 'Moriarty the Patriot',
        'parts': {'moriarty_the_patriot', 'moriarty_the_patriot_part_2'}
    },
    'sakamoto_days': {
        'name': 'SAKAMOTO DAYS',
        'parts': {'sakamoto_days', 'sakamoto_days_part_2'}
    },
    'shangri_la_frontier': {
        'name': 'Shangri-La Frontier',
        'parts': {'shangri_la_frontier', 'shangri_la_frontier_season_2'}
    },
    'the_seven_deadly_sins': {
        'name': 'The Seven Deadly Sins',
        'parts': {
            'the_seven_deadly_sins',
            'the_seven_deadly_sins_the_movie_prisoners_of_the_sky'
        }
    },
    'the_apothecary_diaries': {
        'name': 'The Apothecary Diaries',
        'parts': {'the_apothecary_diaries', 'the_apothecary_diaries_season_2'}
    },
    'the_dangers_in_my_heart': {
        'name': 'The Dangers in My Heart',
        'parts': {'the_dangers_in_my_heart', 'the_dangers_in_my_heart_season_2'}
    },
    'the_disastrous_life_of_saiki_k': {
        'name': 'The Disastrous Life of Saiki K.',
        'parts': {
            'the_disastrous_life_of_saiki_k',
            'the_disastrous_life_of_saiki_k_season_2',
            'the_disastrous_life_of_saiki_k_season_3'
        }
    },
    'the_promised_neverland': {
        'name': 'The Promised Neverland',
        'parts': {'the_promised_neverland', 'the_promised_neverland_season_2'}
    },
    'to_your_eternity': {
        'name': 'To Your Eternity',
        'parts': {'to_your_eternity', 'to_your_eternity_season_2'}
    },
    'tokyo_revengers': {
        'name': 'Tokyo Revengers',
        'parts': {
            'tokyo_revengers',
            'tokyo_revengers_season_2',
            'tokyo_revengers_season_2_part_2'
        }
    },
    'tower_of_god': {
        'name': 'Tower of God',
        'parts': {'tower_of_god', 'tower_of_god_season_2'}
    },
    'vinland_saga': {
        'name': 'Vinland Saga',
        'parts': {'vinland_saga', 'vinland_saga_season_2'}
    },
    'violet_evergarden': {
        'name': 'Violet Evergarden',
        'parts': {
            'violet_evergarden',
            'violet_evergarden_special',
            'violet_evergarden_the_movie'
        }
    },
    'wind_breaker': {
        'name': 'WIND BREAKER',
        'parts': {'wind_breaker', 'wind_breaker_season_2'}
    },
    'welcome_to_demon_school_iruma_kun': {
        'name': 'Welcome to Demon School! Iruma-kun',
        'parts': {
            'welcome_to_demon_school_iruma_kun',
            'welcome_to_demon_school_iruma_kun_season_2'
        }
    },
    'wistoria_wand_and_sword': {
        'name': 'Wistoria: Wand and Sword',
        'parts': {'wistoria_wand_and_sword', 'wistoria_wand_and_sword_season_2'}
    },
    'tonikawa': {
        'name': 'TONIKAWA: Over The Moon For You',
        'parts': {'tonikawa_over_the_moon_for_you', 'tonikawa_over_the_moon_for_you_season_2'}
    },
    'teasing_master_takagi_san': {
        'name': 'Teasing Master Takagi-san',
        'parts': {'teasing_master_takagi_san', 'teasing_master_takagi_san_season_2'}
    },
    'the_case_study_of_vanitas': {
        'name': 'The Case Study of Vanitas',
        'parts': {'banana_fish_extra', 'the_case_study_of_vanitas_part_2'}
    },
    'the_quintessential_quintuplets': {
        'name': 'The Quintessential Quintuplets',
        'parts': {'the_quintessential_quintuplets', 'the_quintessential_quintuplets_movie'}
    },
    'kaiju_no_8': {
        'name': 'Kaiju No. 8',
        'parts': {'kaiju_no_8', 'kaiju_no_8_season_2'}
    }
}

for group_key, group in ADDITIONAL_PARTS.items():

    existing = FRANCHISE_GROUPS.setdefault(
        group_key,
        {'name': group['name'], 'parts': set()}
    )
    existing['parts'].update(group['parts'])

PART_TO_GROUP = {
    part: group_key
    for group_key, group in FRANCHISE_GROUPS.items()
    for part in group['parts']
}


def franchise_key(anime):

    return PART_TO_GROUP.get(
        anime['franchise'],
        anime['franchise']
    )


def franchise_name(anime):

    key = franchise_key(anime)
    group = FRANCHISE_GROUPS.get(key)

    if group:

        return group['name']

    return anime['title']


def build_franchise_groups(animes):

    groups = defaultdict(list)
    seen_titles = set()

    for anime in animes:

        title_key = normalize_title(anime['title'])

        if title_key in seen_titles:

            continue

        seen_titles.add(title_key)

        groups[franchise_key(anime)].append(anime)

    result = []

    for key, parts in groups.items():

        representative = max(
            parts,
            key=lambda item: (
                item.get('rating') or 0,
                -(item.get('year') or 9999)
            )
        )
        known_episodes = [
            item['episodes']
            for item in parts
            if item.get('episodes') is not None
        ]
        genres = sorted({
            genre
            for item in parts
            for genre in item.get('genres', [])
        })
        ratings = [
            item['rating']
            for item in parts
            if item.get('rating') is not None
        ]
        genre_counts = Counter(
            genre
            for item in parts
            for genre in item.get('genres', [])
        )
        primary_genre = min(
            genre_counts,
            key=lambda genre: (-genre_counts[genre], genre),
            default=None
        )
        average_rating = (
            sum(ratings) / len(ratings)
            if ratings
            else None
        )
        completeness = sum(
            bool(item.get(field))
            for item in parts
            for field in ('rating', 'year', 'episodes', 'status')
        ) / max(len(parts) * 4, 1)

        grouped = dict(representative)
        grouped['franchise_key'] = key
        grouped['franchise_name'] = franchise_name(representative)
        grouped['parts'] = sorted(
            parts,
            key=lambda item: (
                item.get('year') or 9999,
                item['title'].casefold()
            )
        )
        grouped['genres'] = genres
        grouped['rating'] = max(ratings) if ratings else None
        grouped['average_rating'] = average_rating
        grouped['primary_genre'] = primary_genre
        grouped['popularity_score'] = (
            (average_rating or 0) * 0.65
            + min(len(parts), 5) * 0.35
            + completeness * 0.25
        )
        grouped['year'] = min(
            (item['year'] for item in parts if item.get('year')),
            default=None
        )
        grouped['known_episodes'] = sum(known_episodes)
        grouped['episodes_complete'] = len(known_episodes) == len(parts)
        grouped['part_count'] = len(parts)
        grouped['title'] = grouped['franchise_name']
        result.append(grouped)

    return sorted(
        result,
        key=lambda item: item['title'].casefold()
    )


def normalize_title(title):

    value = unicodedata.normalize('NFKC', title).casefold()
    value = value.replace('’', "'").replace('–', '-').replace('−', '-')
    value = re.sub(r'[^a-z0-9]+', ' ', value)
    return ' '.join(value.split())
