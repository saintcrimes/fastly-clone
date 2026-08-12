import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from models.model import role
from models import model
from base import get_db
from sqlalchemy import select
from typing import Annotated
from fastapi import Depends
from base import session as async_session

async def seed_roles():

    async with async_session() as session:

        default_roles = ["user", "admin"]

        '''
        ❄️If you want to modify the number of roles you can or change the sequence of the users you
        ought to change the registeration as well as login system values.

        ⚙️You can easily modify the roles by editing the value "default_roles".

        '''

        for name in default_roles:
            result = await session.execute(
            select(model.role).where(model.role.name==name)
            )
            existing = result.scalar_one_or_none()
            if not existing:
                session.add(
                    role(
                        name=name
                    )
                )

        await session.commit()


if __name__ == "__main__":
    asyncio.run(seed_roles())