from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Movie(models.Model):
    name = models.CharField(max_length=255) # 50 маловато для длинных названий
    description = models.TextField(blank=True)
    duration_minutes = models.PositiveIntegerField(help_text="Длительность в минутах")

    def __str__(self):
        return self.name


class Hall(models.Model):
    name = models.CharField(max_length=50, unique=True)

    configuration = models.JSONField(

        default=dict,
        help_text={

                "total_rows": 8,

                "total_cols": 12,

                "screen_position": "top",

                "layout": [

                    [0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0],

                    [0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0],

                    [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0],

                    [1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1],

                    [1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1],

                    [1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1],

                    [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2],

                    [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2]

                ],

                "legend": {

                    "0": "GAP",

                    "1": "STANDARD",

                    "2": "VIP"

                }

                }
    )

    def __str__(self):
        return self.name


class Seat(models.Model):
    hall = models.ForeignKey(Hall, on_delete=models.CASCADE, related_name='seats')
    row_number = models.PositiveIntegerField()
    seat_number = models.PositiveIntegerField()
    is_vip = models.BooleanField(default=False)

    class Meta:
        unique_together = ('hall', 'row_number', 'seat_number')
    
    def __str__(self):
        return f"{self.hall.name} | R:{self.row_number} S:{self.seat_number}"


class Screening(models.Model):
    hall = models.ForeignKey(Hall, on_delete=models.CASCADE, related_name='screenings')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='screenings')
    start_time = models.DateTimeField()
    price = models.DecimalField(max_digits=8, decimal_places=2) 

    def __str__(self):
        return f"{self.movie.name} at {self.start_time}"


class Reservation(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('CONFIRMED', 'Confirmed'),
        ('CANCELLED', 'Cancelled')
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reservations')
    # Одно бронирование = Одно место (для упрощения архитектуры)
    seat = models.ForeignKey(Seat, on_delete=models.CASCADE)
    screening = models.ForeignKey(Screening, on_delete=models.CASCADE)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    
    # payment_intent может быть пустым, пока оплата не началась
    payment_intent_id = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        # Уникальность: Нельзя забронировать одно место на один сеанс дважды,
        # ЕСЛИ старая бронь не отменена. (Эту сложную проверку мы сделаем в коде/constraint позже)
        pass