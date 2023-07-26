# %%
from typing import List, Optional

from sqlalchemy import Float, ForeignKey, Integer, String
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    MappedAsDataclass,
    mapped_column,
    relationship,
)


# %%
class Base(DeclarativeBase, MappedAsDataclass):
    pass


# %%
class GunDev(Base):
    __tablename__ = "gun_dev"
    id: Mapped[int] = mapped_column(primary_key=True)
    dev_type: Mapped[int]
    user_id: Mapped[int] = mapped_column(primary_key=True)
    build_slot: Mapped[int]
    dev_lv: Mapped[int]
    gun_id: Mapped[int] = mapped_column(ForeignKey("gun.id"))
    mp: Mapped[int]
    ammo: Mapped[int]
    mre: Mapped[int]
    part: Mapped[int]
    input_level: Mapped[int]
    item1_num: Mapped[int]
    core: Mapped[int]
    dev_time: Mapped[int]
    log_time: Mapped[int]


# %%
class Gun(Base):
    __tablename__ = "gun"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    en_name: Mapped[str]
    code: Mapped[str]
    introduce: Mapped[str]
    dialogue: Mapped[str]
    extra: Mapped[str]
    en_introduce: Mapped[str]
    character: Mapped[str]
    type: Mapped[int]
    rank: Mapped[int]
    develop_duration: Mapped[int]
    baseammo: Mapped[int]
    basemre: Mapped[int]
    ammo_add_withnumber: Mapped[int]
    mre_add_withnumber: Mapped[int]
    retiremp: Mapped[int]
    retireammo: Mapped[int]
    retiremre: Mapped[int]
    retirepart: Mapped[int]
    ratio_life: Mapped[int]
    ratio_pow: Mapped[int]
    ratio_rate: Mapped[int]
    ratio_speed: Mapped[int]
    ratio_hit: Mapped[int]
    ratio_dodge: Mapped[int]
    ratio_armor: Mapped[int]
    armor_piercing: Mapped[int]
    crit: Mapped[int]
    special: Mapped[int]
    eat_ratio: Mapped[int]
    ratio_range: Mapped[int]
    skill1: Mapped[int]
    skill2: Mapped[int]
    normal_attack: Mapped[int]
    passive_skill: Mapped[str]
    dynamic_passive_skill: Mapped[str]
    effect_grid_center: Mapped[int]
    effect_guntype: Mapped[str]
    effect_grid_pos: Mapped[str]
    effect_grid_effect: Mapped[str]
    max_equip: Mapped[int]
    type_equip1: Mapped[str]
    type_equip2: Mapped[str]
    type_equip3: Mapped[str]
    type_equip4: Mapped[str]
    ai: Mapped[int]
    is_additional: Mapped[int]
    launch_time: Mapped[str]
    obtain_ids: Mapped[str]
    rank_display: Mapped[int]
    prize_id: Mapped[int]
    mindupdate_consume: Mapped[str]
    explore_tag: Mapped[str]
    gun_detail_bg: Mapped[str]
    org_id: Mapped[int]
    related_story_id: Mapped[int]
    show_damage_skin: Mapped[str]
    gun_tag_ids: Mapped[str]
    atk_speed_max: Mapped[int]
    ratio_rec: Mapped[int]
    recommended_team_ids: Mapped[str]


# %%
class EquipDev(Base):
    __tablename__ = "equip_dev"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(primary_key=True)
    dev_type: Mapped[int]
    build_slot: Mapped[int]
    dev_lv: Mapped[int]
    equip_id: Mapped[int] = mapped_column(ForeignKey("equip.id"))
    mp: Mapped[int]
    ammo: Mapped[int]
    mre: Mapped[int]
    part: Mapped[int]
    input_level: Mapped[int]
    core: Mapped[int]
    item_num: Mapped[int]
    dev_time: Mapped[int]
    fairy_id: Mapped[int] = mapped_column(ForeignKey("fairy.id"))
    passive_skill: Mapped[int] = mapped_column(ForeignKey("fairy_talent.id"))
    quality_lv: Mapped[int]
    log_time: Mapped[int]


# %%
class Equip(Base):
    __tablename__ = "equip"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    description: Mapped[str]
    rank: Mapped[int]
    category: Mapped[int]
    type: Mapped[int]
    pow: Mapped[str]
    hit: Mapped[str]
    dodge: Mapped[str]
    speed: Mapped[str]
    rate: Mapped[str]
    critical_harm_rate: Mapped[str]
    critical_percent: Mapped[str]
    armor_piercing: Mapped[str]
    armor: Mapped[str]
    shield: Mapped[str]
    damage_amplify: Mapped[str]
    damage_reduction: Mapped[str]
    night_view_percent: Mapped[str]
    bullet_number_up: Mapped[str]
    skill_effect_per: Mapped[int]
    skill_effect: Mapped[int]
    slow_down_percent: Mapped[int]
    slow_down_rate: Mapped[int]
    slow_down_time: Mapped[int]
    dot_percent: Mapped[int]
    dot_damage: Mapped[int]
    dot_time: Mapped[int]
    retire_mp: Mapped[int]
    retire_ammo: Mapped[int]
    retire_mre: Mapped[int]
    retire_part: Mapped[int]
    code: Mapped[str]
    develop_duration: Mapped[int]
    company: Mapped[str]
    skill_level_up: Mapped[int]
    fit_guns: Mapped[str]
    equip_introduction: Mapped[str]
    powerup_mp: Mapped[float]
    powerup_ammo: Mapped[float]
    powerup_mre: Mapped[float]
    powerup_part: Mapped[float]
    exclusive_rate: Mapped[int]
    bonus_type: Mapped[str]
    skill: Mapped[int]
    passive_skill: Mapped[str]
    max_level: Mapped[int]
    auto_select_id: Mapped[int]
    equip_group_id: Mapped[int]
    is_addition: Mapped[int]
    is_show: Mapped[int]
    obtain_ids: Mapped[str]
    sp_description: Mapped[str]


class Fairy(Base):
    __tablename__ = "fairy"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    code: Mapped[str]
    description: Mapped[str]
    introduce: Mapped[str]
    type: Mapped[int] = mapped_column(ForeignKey("fairy_type.id"))
    pow: Mapped[int]
    hit: Mapped[int]
    dodge: Mapped[int]
    armor: Mapped[int]
    critical_harm_rate: Mapped[int]
    grow: Mapped[int]
    proportion: Mapped[str]
    skill_id: Mapped[str]
    quality_exp: Mapped[int]
    quality_need_number: Mapped[str]
    category: Mapped[int]
    develop_duration: Mapped[int]
    retiremp: Mapped[int]
    retireammo: Mapped[int]
    retiremre: Mapped[int]
    retirepart: Mapped[int]
    powerup_mp: Mapped[int]
    powerup_ammo: Mapped[int]
    powerup_mre: Mapped[int]
    powerup_part: Mapped[int]
    armor_piercing: Mapped[int]
    ai: Mapped[int]
    is_additional: Mapped[int]
    avatar_offset: Mapped[str]
    avatar_scale: Mapped[str]
    picture_offset: Mapped[str]
    picture_scale: Mapped[str]
    org_id: Mapped[int]
    obtain_ids: Mapped[str]
    skill_id_mod: Mapped[str]
    passive_skill_mod: Mapped[str]
    pow_mod: Mapped[int]
    hit_mod: Mapped[int]


class FairyTalent(Base):
    __tablename__ = "fairy_talent"
    id: Mapped[int] = mapped_column(primary_key=True)
    rank: Mapped[int]
    type_id: Mapped[int]
    name: Mapped[str]


class FairyType(Base):
    __tablename__ = "fairy_type"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    en_name: Mapped[str]


# %%
if __name__ == "__main__":
    # %%
    from sqlalchemy import create_engine

    engine = create_engine("sqlite+pysqlite:///../../Elisa/logs/develop_log.db")
# %%
