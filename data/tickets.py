import os

class TicketManager:
    def __init__(self):
        self.tickets = {}  # {user_id: ticket_id}
        self.ticket_users = {}  # {ticket_id: user_id}
        self.ticket_messages = {}  # {ticket_id: message_id}
        self.counter = self.load_last_ticket_id() + 1  # Загружаем последний ID

    def load_last_ticket_id(self):
        """Читает последний ID обращения из файла."""
        if not os.path.exists("tickets.txt"):
            return 0
        with open("tickets.txt", "r", encoding="utf-8") as file:
            lines = file.readlines()
            for line in reversed(lines):
                if line.startswith("Обращение #"):
                    return int(line.split("#")[1].strip())
        return 0

    def start_ticket(self, user_id, username):
        """Создаёт новое обращение, если его нет."""
        if user_id in self.tickets:
            return self.tickets[user_id]

        ticket_id = str(self.counter)
        self.tickets[user_id] = ticket_id
        self.ticket_users[ticket_id] = user_id
        self.counter += 1

        # Записываем в файл начало нового обращения
        with open("tickets.txt", "a", encoding="utf-8") as file:
            file.write(f"\nОбращение #{ticket_id}\n")

        return ticket_id

    def get_ticket_id(self, user_id):
        """Возвращает номер текущего обращения пользователя."""
        return self.tickets.get(user_id)

    def get_user_by_ticket(self, ticket_id):
        """Возвращает user_id по номеру обращения."""
        return self.ticket_users.get(ticket_id)

    def store_message(self, ticket_id, sender, text, sender_type):
        """Сохраняет сообщение в файле `tickets.txt`."""
        user_info = f"({sender.id}/@{sender.username})" if sender_type == "Клиент" else "Поддержка"
        with open("tickets.txt", "a", encoding="utf-8") as file:
            file.write(f"{sender_type} {user_info}: {text}\n")

    def close_ticket(self, ticket_id):
        """Закрывает обращение и записывает в файл 'ОБРАЩЕНИЕ ЗАКРЫТО'."""
        user_id = self.ticket_users.pop(ticket_id, None)
        if user_id:
            self.tickets.pop(user_id, None)
            self.ticket_messages.pop(ticket_id, None)

            with open("tickets.txt", "a", encoding="utf-8") as file:
                file.write("ОБРАЩЕНИЕ ЗАКРЫТО\n\n")

    def extract_ticket_id(self, text):
        """Извлекает номер обращения из текста сообщения."""
        for line in text.split("\n"):
            if "Номер обращения: #" in line:
                return line.split("#")[1].strip()
        return None
