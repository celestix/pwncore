from typing import AsyncGenerator
from contextlib import asynccontextmanager

import aiodocker
from aiodocker import docker
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from tortoise import Tortoise, generate_config
from tortoise.contrib.fastapi import RegisterTortoise

import pwncore.containerASD as containerASD
import pwncore.docs as docs
import pwncore.routes as routes
from pwncore.config import config
from pwncore.models import Container


@asynccontextmanager
async def lifespan_test(app: FastAPI) -> AsyncGenerator[None, None]:
    config = generate_config(
        "sqlite://:memory:",
        app_modules={"models": ["pwncore.models"]},
        testing=True,
        connection_label="models",
    )
    async with RegisterTortoise(
        app=app,
        config=config,
        generate_schemas=True,
        add_exception_handlers=True,
        _create_db=True,
    ):
        # db connected
        yield
        # app teardown
    # db connections closed
    await Tortoise._drop_databases()


@asynccontextmanager
async def app_lifespan(app: FastAPI):
    if getattr(app.state, "testing", None):
        async with lifespan_test(app) as _:
            yield
    else:
        # Startup
        await Tortoise.init(
            db_url=config.db_url, modules={"models": ["pwncore.models"]}
        )
        await Tortoise.generate_schemas()
    # Startup
    await Tortoise.init(db_url=config.db_url, modules={"models": ["pwncore.models"]})
    await Tortoise.generate_schemas()

    containerASD.docker_client = aiodocker.Docker(url=config.docker_url)

    yield
    # Shutdown
    # Stop and remove all running containers
    containers = await Container.all().values()
    await Container.all().delete()
    for db_container in containers:
        try:
            container = await containerASD.docker_client.containers.get(
                db_container["docker_id"]
            )
            await container.kill()
            await container.delete()
        except (
            Exception
        ):  # Raises DockerError if container does not exist, just pass for now.
            pass

    # close_connections is deprecated, not sure how to use connections.close_all()
    await Tortoise.close_connections()
    await containerASD.docker_client.close()


app = FastAPI(
    title="Pwncore",
    openapi_tags=docs.tags_metadata,
    description=docs.description,
    lifespan=app_lifespan,
)
app.include_router(routes.router)

origins = [
    "http://ctf.lugvitc.org",
    "https://ctf.lugvitc.org",
]

if config.development:
    origins.append("http://localhost:5173")
    origins.append("http://localhost:4173")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
