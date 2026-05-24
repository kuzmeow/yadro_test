from notification_service.domain.notification.entities.notification_entity import Notification
from notification_service.domain.notification.protocols.notification_tasks_protocol import NotificationTasksProtocol
from notification_service.infra.taskiq.post_commit_queue import PostCommitQueue
from notification_service.infra.taskiq.tasks.notification_tasks import send_notification


class TaskIQNotificationTasksAdapter(NotificationTasksProtocol):
    def __init__(self, queue: PostCommitQueue) -> None:
        self.queue = queue

    def enqueue_notification(self, notification: Notification) -> None:
        """Запланировать отправку уведомления.

        :param notification: Доменная сущность уведомления.
        :return: None
        """

        self.queue.schedule(send_notification.kiq(notification=notification))
