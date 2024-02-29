from sqlalchemy import (
    DOUBLE_PRECISION,
    UUID,
    VARCHAR,
    ARRAY,
    ForeignKey
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship
)


class BaseORM(DeclarativeBase):
    pass


class WellORM(BaseORM):
    __tablename__ = 'well'

    id: Mapped[UUID] = mapped_column(
        UUID,
        primary_key=True,
        name='pk_id'
    )
    name: Mapped[VARCHAR] = mapped_column(
        VARCHAR(64),
        nullable=False,
        name='well_name'
    )
    # head: Mapped['Point'] = mapped_column(
    #     ...
    # )
    measured_depth: Mapped[ARRAY[DOUBLE_PRECISION]] = mapped_column(
        ARRAY[DOUBLE_PRECISION],
        nullable=False,
        name='measured_depth'
    )
    tracks = relationship('TrajectoryORM', back_populates='well')


class TrajectoryORM(BaseORM):
    __table__ = 'trajectory'

    x: Mapped[DOUBLE_PRECISION] = mapped_column(
        DOUBLE_PRECISION,
        nullable=False,
        name='x'
    )
    y: Mapped[DOUBLE_PRECISION] = mapped_column(
        DOUBLE_PRECISION,
        nullable=False,
        name='y'
    )
    z: Mapped[DOUBLE_PRECISION] = mapped_column(
        DOUBLE_PRECISION,
        nullable=False,
        name='z'
    )
    well_id: Mapped[UUID] = mapped_column(
        UUID,
        ForeignKey('well.pk_id', ondelete='CASCADE'),
        nullable=False,
        name='fk_well_id'
    )
    well = relationship('WellORM', back_populates='trajectory')
