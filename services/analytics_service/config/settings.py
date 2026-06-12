from pathlib import Path

from ecommerce_common.settings import configure

BASE_DIR = Path(__file__).resolve().parent.parent

configure(
    globals(),
    service_name="analytics",
    base_dir=BASE_DIR,
    local_apps=["analytics"],
)
