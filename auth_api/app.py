import gevent.monkey

gevent.monkey.patch_all()

from dotenv import load_dotenv

from src import create_app
from src.core.config import settings
from src.utils.tracer_conf import configure_tracer


load_dotenv()

app = create_app()
if settings.tracer_enabled:
    configure_tracer()


def main():
    app.run()


if __name__ == "__main__":
    main()
