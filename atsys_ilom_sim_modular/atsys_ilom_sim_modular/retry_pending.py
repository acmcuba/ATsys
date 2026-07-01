from ilom_sim.publisher import EventPublisher
from ilom_sim.storage import EventStorage
from ilom_sim.utils import load_config


def main() -> None:
    config = load_config()
    publisher = EventPublisher(config)
    storage = EventStorage(config["runtime"]["sqlite_path"])

    pending = storage.get_pending_events(limit=100)
    if not pending:
        print("[INFO] No hay eventos pendientes.")
        return

    print(f"[INFO] Reintentando {len(pending)} evento(s) pendiente(s)...")
    retried_ok = 0
    retried_fail = 0

    for row_id, event in pending:
        delivered = publisher.try_http_post(event)
        if delivered:
            storage.update_delivery_status_by_row_id(row_id, "sent")
            retried_ok += 1
        else:
            storage.update_delivery_status_by_row_id(row_id, "failed")
            retried_fail += 1

    print(f"[INFO] Reintentos completados. sent={retried_ok}, failed={retried_fail}")


if __name__ == "__main__":
    main()
