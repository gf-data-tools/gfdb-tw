# %%
import pandas as pd
from sqlalchemy import (
    Column,
    Float,
    and_,
    cast,
    create_engine,
    func,
    or_,
    select,
    text,
    union_all,
)
from sqlalchemy.orm import Session

from database import Equip, EquipDev, Fairy, FairyType, Gun, GunDev
from event_record import EventRecord


# %%
class RecordAnalyzer:
    def __init__(self, engine_dir, record_dir):
        self.engine = create_engine(engine_dir)
        self.eventrecord = EventRecord(record_dir)

    def analyze_gun_period_table(self, period_table):
        gun_cnt = (
            select(
                period_table,
                func.row_number()
                .over(
                    order_by=period_table.c.id.asc(),
                    partition_by=[
                        period_table.c.user_id % 10,
                        period_table.c.log_time,
                        period_table.c.gun_id,
                        period_table.c.rank,
                    ],
                )
                .label("cnt"),
                period_table.c.rank,
            )
            .select_from(period_table)
            .subquery("gun_cnt")
        )
        trust_limit = (
            select(
                (gun_cnt.c.user_id % 10).label("subtable"),
                gun_cnt.c.log_time,
                gun_cnt.c.rank,
                func.min(gun_cnt.c.id).label("id"),
            )
            .where(gun_cnt.c.cnt == 10)
            .group_by(
                text("subtable"),
                gun_cnt.c.log_time,
                gun_cnt.c.rank,
            )
            .order_by(gun_cnt.c.log_time)
            .subquery("trust_limit")
        )
        rank_trust_limit = (
            select(
                trust_limit.c.subtable,
                trust_limit.c.log_time,
                func.min(trust_limit.c.id).label("id"),
            )
            .group_by(
                trust_limit.c.subtable,
                trust_limit.c.log_time,
            )
            .subquery("rank_trust_limit")
        )

        rank_trust_records = (
            select(period_table)
            .select_from(period_table)
            .join(
                rank_trust_limit,
                (period_table.c.user_id % 10 == rank_trust_limit.c.subtable)
                & (period_table.c.log_time == rank_trust_limit.c.log_time),
                isouter=True,
            )
            .where(
                or_(
                    rank_trust_limit.c.id == None,
                    period_table.c.id <= rank_trust_limit.c.id,
                )
            )
        ).subquery("rank_trust_records")
        rank_count = (
            select(
                rank_trust_records.c.mp,
                rank_trust_records.c.ammo,
                rank_trust_records.c.mre,
                rank_trust_records.c.part,
                rank_trust_records.c.input_level,
                rank_trust_records.c.rank,
                func.count().label("rank_count"),
            )
            .select_from(rank_trust_records)
            .group_by(
                rank_trust_records.c.mp,
                rank_trust_records.c.ammo,
                rank_trust_records.c.mre,
                rank_trust_records.c.part,
                rank_trust_records.c.input_level,
                rank_trust_records.c.rank,
            )
            .subquery("rank_count")
        )

        rank_total = (
            select(
                rank_count.c.mp,
                rank_count.c.ammo,
                rank_count.c.mre,
                rank_count.c.part,
                rank_count.c.input_level,
                func.sum(rank_count.c.rank_count).label("rank_total"),
            )
            .select_from(rank_count)
            .group_by(
                rank_count.c.mp,
                rank_count.c.ammo,
                rank_count.c.mre,
                rank_count.c.part,
                rank_count.c.input_level,
            )
            .subquery("rank_total")
        )
        gun_records = (
            select(period_table)
            .select_from(period_table)
            .join(
                trust_limit,
                and_(
                    period_table.c.user_id % 10 == trust_limit.c.subtable,
                    period_table.c.log_time == trust_limit.c.log_time,
                    period_table.c.rank == trust_limit.c.rank,
                ),
                isouter=True,
            )
            .where(
                or_(
                    trust_limit.c.id == None,
                    period_table.c.id <= trust_limit.c.id,
                )
            )
        ).subquery("gun_records")

        gun_count = (
            select(
                gun_records.c.mp,
                gun_records.c.ammo,
                gun_records.c.mre,
                gun_records.c.part,
                gun_records.c.input_level,
                gun_records.c.rank,
                gun_records.c.gun_id,
                func.count().label("gun_count"),
            )
            .select_from(gun_records)
            .group_by(
                gun_records.c.mp,
                gun_records.c.ammo,
                gun_records.c.mre,
                gun_records.c.part,
                gun_records.c.input_level,
                gun_records.c.rank,
                gun_records.c.gun_id,
            )
            .subquery("gun_count")
        )

        gun_total = (
            select(
                gun_count.c.mp,
                gun_count.c.ammo,
                gun_count.c.mre,
                gun_count.c.part,
                gun_count.c.input_level,
                gun_count.c.rank,
                func.sum(gun_count.c.gun_count).label("gun_total"),
            )
            .select_from(gun_count)
            .group_by(
                gun_count.c.mp,
                gun_count.c.ammo,
                gun_count.c.mre,
                gun_count.c.part,
                gun_count.c.input_level,
                gun_count.c.rank,
            )
            .subquery("gun_total")
        )

        rc, rt, gc, gt = (
            rank_count.c.rank_count,
            rank_total.c.rank_total,
            gun_count.c.gun_count,
            gun_total.c.gun_total,
        )
        rm, gm = rc / rt, gc / gt
        rv = rc * (rt - rc) / (rt * rt * (rt + 1))
        gv = gc * (gt - gc) / (gt * gt * (gt + 1))

        mean, stdev = rm * gm, rm * func.sqrt(gv) + rv * func.sqrt(gm)

        analyze = (
            select(
                rank_total.c.mp,
                rank_total.c.ammo,
                rank_total.c.mre,
                rank_total.c.part,
                rank_total.c.input_level,
                rank_count.c.rank,
                gun_count.c.gun_id,
                Gun.name,
                cast((mean * 100).label("mean%"), Float),
                cast((stdev * 100).label("stdev%"), Float),
                rank_total.c.rank_total,
                rank_count.c.rank_count,
                gun_total.c.gun_total,
                gun_count.c.gun_count,
            )
            .select_from(rank_count)
            .join(
                rank_total,
                and_(
                    *[
                        rank_count.c[i] == rank_total.c[i]
                        for i in ["mp", "ammo", "mre", "part", "input_level"]
                    ]
                ),
            )
            .join(
                gun_count,
                and_(
                    *[
                        rank_count.c[i] == gun_count.c[i]
                        for i in ["mp", "ammo", "mre", "part", "input_level", "rank"]
                    ]
                ),
            )
            .join(
                gun_total,
                and_(
                    *[
                        rank_count.c[i] == gun_total.c[i]
                        for i in ["mp", "ammo", "mre", "part", "input_level", "rank"]
                    ]
                ),
            )
            .join(Gun)
            .subquery("analyze")
        )
        return analyze

    def analyze_gun_nm(self):
        engine = self.engine
        eventrecord = self.eventrecord

        analyze_queries = []
        for idx, period in enumerate(eventrecord["gun_nm"]):
            name = period.note
            time_tuple = [(a.timestamp(), b.timestamp()) for a, b in period.times]

            period_table = (
                select(GunDev, Gun.rank)
                .select_from(GunDev)
                .join(Gun)
                .where(or_(*[GunDev.dev_time.between(a, b) for a, b in time_tuple]))
                .where(GunDev.input_level == 0)
            ).subquery()

            analyze = self.analyze_gun_period_table(period_table)

            analyze = (
                select(Column(f"{idx:03} {name}").label("event"), analyze)
                .where(analyze.c.rank_total > 5000)
                .subquery()
            )

            analyze_queries.append(analyze)

        stmt = union_all(*[select(t) for t in analyze_queries])
        with Session(self.engine) as session:
            res = session.execute(stmt).all()

        df = pd.DataFrame(res)

        return df

    def analyze_gun_sp(self):
        engine = self.engine
        eventrecord = self.eventrecord

        analyze_queries = []
        for idx, period in enumerate(eventrecord["gun_sp"]):
            name = period.note
            time_tuple = [(a.timestamp(), b.timestamp()) for a, b in period.times]

            period_table = (
                select(GunDev, Gun.rank)
                .select_from(GunDev)
                .join(Gun)
                .where(or_(*[GunDev.dev_time.between(a, b) for a, b in time_tuple]))
                .where(GunDev.input_level != 0)
            ).subquery()

            analyze = self.analyze_gun_period_table(period_table)

            analyze = (
                select(Column(f"{idx:03} {name}").label("event"), analyze)
                .where(analyze.c.rank_total > 2000)
                .subquery()
            )

            analyze_queries.append(analyze)

        stmt = union_all(*[select(t) for t in analyze_queries])
        with Session(self.engine) as session:
            res = session.execute(stmt).all()

        df = pd.DataFrame(res)

        return df

    # %%
    def analyze_equip(self):
        engine = self.engine
        eventrecord = self.eventrecord

        analyze_queries = []
        for idx, period in enumerate(eventrecord["equip"]):
            # %%
            name = period.note
            time_tuple = [(a.timestamp(), b.timestamp()) for a, b in period.times]
            # %%
            period_table = (
                select(EquipDev, Equip.rank)
                .select_from(EquipDev)
                .join(Equip)
                .where(or_(*[EquipDev.dev_time.between(a, b) for a, b in time_tuple]))
                .where(EquipDev.equip_id != 0)
            ).subquery()
            # %%
            equip_cnt = (
                select(
                    period_table,
                    func.row_number()
                    .over(
                        order_by=period_table.c.id.asc(),
                        partition_by=[
                            period_table.c.user_id % 10,
                            period_table.c.log_time,
                            period_table.c.equip_id,
                            period_table.c.rank,
                        ],
                    )
                    .label("cnt"),
                    period_table.c.rank,
                )
                .select_from(period_table)
                .subquery("equip_cnt")
            )
            # %%
            trust_limit = (
                select(
                    (equip_cnt.c.user_id % 10).label("subtable"),
                    equip_cnt.c.log_time,
                    func.min(equip_cnt.c.id).label("id"),
                )
                .where(equip_cnt.c.cnt == 10)
                .group_by(
                    text("subtable"),
                    equip_cnt.c.log_time,
                )
                .order_by(equip_cnt.c.log_time)
                .subquery("trust_limit")
            )
            # %%
            equip_records = (
                select(period_table)
                .select_from(period_table)
                .join(
                    trust_limit,
                    and_(
                        period_table.c.user_id % 10 == trust_limit.c.subtable,
                        period_table.c.log_time == trust_limit.c.log_time,
                    ),
                    isouter=True,
                )
                .where(
                    or_(
                        trust_limit.c.id == None,
                        period_table.c.id <= trust_limit.c.id,
                    )
                )
            ).subquery("equip_records")

            # %%
            equip_count = (
                select(
                    equip_records.c.mp,
                    equip_records.c.ammo,
                    equip_records.c.mre,
                    equip_records.c.part,
                    equip_records.c.item_num,
                    equip_records.c.rank,
                    equip_records.c.equip_id,
                    func.count().label("equip_count"),
                )
                .select_from(equip_records)
                .group_by(
                    equip_records.c.mp,
                    equip_records.c.ammo,
                    equip_records.c.mre,
                    equip_records.c.part,
                    equip_records.c.item_num,
                    equip_records.c.rank,
                    equip_records.c.equip_id,
                )
                .subquery("equip_count")
            )
            # %%
            equip_total = (
                select(
                    equip_count.c.mp,
                    equip_count.c.ammo,
                    equip_count.c.mre,
                    equip_count.c.part,
                    equip_count.c.item_num,
                    func.sum(equip_count.c.equip_count).label("equip_total"),
                )
                .select_from(equip_count)
                .group_by(
                    equip_count.c.mp,
                    equip_count.c.ammo,
                    equip_count.c.mre,
                    equip_count.c.part,
                    equip_count.c.item_num,
                )
                .subquery("equip_total")
            )
            # %%
            ec, et = equip_count.c.equip_count, equip_total.c.equip_total
            mean = ec / et
            stdev = func.sqrt(ec * (et - ec) / (et * et * (et + 1)))

            analyze = (
                select(
                    equip_total.c.mp,
                    equip_total.c.ammo,
                    equip_total.c.mre,
                    equip_total.c.part,
                    equip_total.c.item_num,
                    equip_count.c.rank,
                    equip_count.c.equip_id,
                    Equip.name,
                    cast((mean * 100).label("mean%"), Float),
                    cast((stdev * 100).label("stdev%"), Float),
                    equip_total.c.equip_total,
                    equip_count.c.equip_count,
                )
                .select_from(equip_total)
                .join(
                    equip_count,
                    and_(
                        *[
                            equip_count.c[i] == equip_total.c[i]
                            for i in ["mp", "ammo", "mre", "part", "item_num"]
                        ]
                    ),
                )
                .join(Equip)
                .subquery("analyze")
            )
            analyze = (
                select(Column(f"{idx:03} {name}").label("event"), analyze)
                .where(analyze.c.equip_total >= 1000)
                .subquery()
            )
            analyze_queries.append(analyze)
        # %%
        stmt = union_all(*[select(t) for t in analyze_queries])
        with Session(self.engine) as session:
            res = session.execute(stmt).all()
        # %%
        df = pd.DataFrame(res)

        return df

    def analyze_fairy(self):
        engine = self.engine
        eventrecord = self.eventrecord

        analyze_queries = []
        for idx, period in enumerate(eventrecord["fairy"]):
            # %%
            name = period.note
            time_tuple = [(a.timestamp(), b.timestamp()) for a, b in period.times]
            # %%
            period_table = (
                select(EquipDev)
                .select_from(EquipDev)
                .where(or_(*[EquipDev.dev_time.between(a, b) for a, b in time_tuple]))
                .where(EquipDev.fairy_id != 0)
            ).subquery()
            # %%
            fairy_cnt = (
                select(
                    period_table,
                    func.row_number()
                    .over(
                        order_by=period_table.c.id.asc(),
                        partition_by=[
                            period_table.c.user_id % 10,
                            period_table.c.log_time,
                            period_table.c.fairy_id,
                        ],
                    )
                    .label("cnt"),
                )
                .select_from(period_table)
                .subquery("fairy_cnt")
            )
            # %%
            trust_limit = (
                select(
                    (fairy_cnt.c.user_id % 10).label("subtable"),
                    fairy_cnt.c.log_time,
                    func.min(fairy_cnt.c.id).label("id"),
                )
                .where(fairy_cnt.c.cnt == 10)
                .group_by(
                    text("subtable"),
                    fairy_cnt.c.log_time,
                )
                .subquery("trust_limit")
            )
            # %%
            fairy_records = (
                select(period_table)
                .select_from(period_table)
                .join(
                    trust_limit,
                    and_(
                        period_table.c.user_id % 10 == trust_limit.c.subtable,
                        period_table.c.log_time == trust_limit.c.log_time,
                    ),
                    isouter=True,
                )
                .where(
                    or_(
                        trust_limit.c.id == None,
                        period_table.c.id <= trust_limit.c.id,
                    )
                )
            ).subquery("fairy_records")

            # %%
            fairy_count = (
                select(
                    fairy_records.c.mp,
                    fairy_records.c.ammo,
                    fairy_records.c.mre,
                    fairy_records.c.part,
                    fairy_records.c.input_level,
                    fairy_records.c.fairy_id,
                    func.count().label("fairy_count"),
                )
                .select_from(fairy_records)
                .group_by(
                    fairy_records.c.mp,
                    fairy_records.c.ammo,
                    fairy_records.c.mre,
                    fairy_records.c.part,
                    fairy_records.c.input_level,
                    fairy_records.c.fairy_id,
                )
                .subquery("fairy_count")
            )
            # %%
            fairy_total = (
                select(
                    fairy_count.c.mp,
                    fairy_count.c.ammo,
                    fairy_count.c.mre,
                    fairy_count.c.part,
                    fairy_count.c.input_level,
                    func.sum(fairy_count.c.fairy_count).label("fairy_total"),
                )
                .select_from(fairy_count)
                .group_by(
                    fairy_count.c.mp,
                    fairy_count.c.ammo,
                    fairy_count.c.mre,
                    fairy_count.c.part,
                    fairy_count.c.input_level,
                )
                .subquery("fairy_total")
            )
            # %%
            ec, et = fairy_count.c.fairy_count, fairy_total.c.fairy_total
            mean = ec / et
            stdev = func.sqrt(ec * (et - ec) / (et * et * (et + 1)))

            analyze = (
                select(
                    fairy_total.c.mp,
                    fairy_total.c.ammo,
                    fairy_total.c.mre,
                    fairy_total.c.part,
                    fairy_total.c.input_level,
                    FairyType.name.label("type"),
                    fairy_count.c.fairy_id,
                    Fairy.name,
                    cast((mean * 100).label("mean%"), Float),
                    cast((stdev * 100).label("stdev%"), Float),
                    fairy_total.c.fairy_total,
                    fairy_count.c.fairy_count,
                )
                .select_from(fairy_total)
                .join(
                    fairy_count,
                    and_(
                        *[
                            fairy_count.c[i] == fairy_total.c[i]
                            for i in ["mp", "ammo", "mre", "part", "input_level"]
                        ]
                    ),
                )
                .join(Fairy)
                .join(FairyType)
                .subquery("analyze")
            )
            analyze = (
                select(Column(f"{idx:03} {name}").label("event"), analyze)
                .where(analyze.c.fairy_total >= 1000)
                .subquery()
            )
            analyze_queries.append(analyze)
        # %%
        stmt = union_all(*[select(t) for t in analyze_queries])
        with Session(self.engine) as session:
            res = session.execute(stmt).all()
        # %%
        df = pd.DataFrame(res)

        return df


# %%
if __name__ == "__main__":
    analyzer = RecordAnalyzer(
        "sqlite+pysqlite:///../Elisa/logs/develop_log.db",
        "events.hjson",
    )
    from logger_tt import logger
    from sqlalchemy.exc import OperationalError

    def keep_retry(func, file):
        while True:
            try:
                df = func()
                df.to_csv(file, index=False, float_format="%.3f")
                break
            except OperationalError as e:
                logger.error(e)
            except:
                logger.exception("Unknown Error")
                raise

    keep_retry(analyzer.analyze_gun_nm, "analyze/gun_nm.csv")
    keep_retry(analyzer.analyze_gun_sp, "analyze/gun_sp.csv")
    keep_retry(analyzer.analyze_equip, "analyze/equip.csv")
    keep_retry(analyzer.analyze_fairy, "analyze/fairy.csv")
    # df = analyzer.analyze_gun_nm()
    # df.to_csv("analyze/gun_nm.csv", index=False, float_format="%.3f")
    # df = analyzer.analyze_gun_sp()
    # df.to_csv("analyze/gun_sp.csv", index=False, float_format="%.3f")
    # df = analyzer.analyze_equip()
    # df.to_csv("analyze/equip.csv", index=False, float_format="%.3f")
    # df = analyzer.analyze_fairy()
    # df.to_csv("analyze/fairy.csv", index=False, float_format="%.3f")
