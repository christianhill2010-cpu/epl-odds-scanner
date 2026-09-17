from sqlalchemy.orm import Session

from app.storage.schema import ScanRun


def create_scan_run(session: Session, *, status: str = "started") -> ScanRun:
    scan_run = ScanRun(status=status)
    session.add(scan_run)
    session.commit()
    session.refresh(scan_run)
    return scan_run
