from apps.queue_control.models import Queue, QueueTicket


class QueueSelector:
    @staticmethod
    def queue_state(queue_id):
        queue = Queue.objects.get(pk=queue_id)
        return {
            "queue": queue,
            "waiting": QueueTicket.objects.filter(queue=queue, status__in=["issued", "waiting"]).count(),
            "called": QueueTicket.objects.filter(queue=queue, status="called").count(),
            "current_serving": queue.current_serving,
        }
