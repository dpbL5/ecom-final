from pathlib import Path

from ecommerce_common.settings import configure


BASE_DIR = Path(__file__).resolve().parent.parent

configure(
    globals(),
    service_name="identity",
    base_dir=BASE_DIR,
    local_apps=["accounts"],
    identity_service=True,
)
