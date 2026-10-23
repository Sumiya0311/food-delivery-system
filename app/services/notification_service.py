from datetime import datetime


def create_notification_message(
    title: str,
    message: str,
) -> dict:
    """Prepare notification data for saving or sending."""
    title = title.strip()
    message = message.strip()

    if not title:
        raise ValueError("Notification title cannot be empty")

    if not message:
        raise ValueError("Notification message cannot be empty")

    return {
        "title": title,
        "message": message,
        "created_at": datetime.now(),
        "is_read": False,
    }