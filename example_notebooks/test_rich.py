from rich.console import Console
from rich.progress import *
from rich.live import Live
from rich.traceback import install
from rich.logging import RichHandler
from rich.style import Style
import logging
import time

install()
logging.basicConfig(handlers=[RichHandler(markup=True)])

log = logging.getLogger("sagemaker-core")
log.setLevel("INFO")
console = Console()

from sagemaker_core.generated.exceptions import TimeoutExceededError


def wait(timeout):
    with Progress(
        SpinnerColumn("bouncingBar"),
        TextColumn("{task.description}"),
        TimeElapsedColumn(),
        console=console,
    ) as progress:
        task = progress.add_task(f"Waiting for TrainingJob to be deleted...")
        start_time = time.time()
        status = ["Completed", "Failed", "Stopped"]
        i = 0
        status_task = progress.add_task("Current status:")
        while True:
            current_status = status[i % 3]
            status_description = f"Current status: [bold]{current_status}"
            progress.update(status_task, description=status_description)
            time.sleep(1.0)
            if time.time() - start_time >= 5:
                progress.stop()
                break
            if timeout is not None and time.time() - start_time >= timeout:
                raise TimeoutExceededError(resource_type="TrainingJob", status=current_status)
            i += 1
        log.info("[bold green]TrainingJob has been deleted successfully")


wait(6)
