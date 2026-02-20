import random
from datetime import datetime, timedelta

def random_time_between_7h35_and_10h17():
    """Genere une heure aleatoire entre 7h35 et 10h17."""
    start_minutes = 7 * 60 + 35   # 7h35 = 455 minutes
    end_minutes = 10 * 60 + 17    # 10h17 = 617 minutes
    random_minutes = random.randint(start_minutes, end_minutes)
    hour = random_minutes // 60
    minute = random_minutes % 60
    return hour, minute

def generate_schedule(start_date=None):
    """
    Genere le calendrier complet des 100 publications.

    Retourne une liste de 100 datetime avec date et heure de publication.
    """
    if start_date is None:
        start_date = datetime.now().date() + timedelta(days=1)  # Commence demain

    schedule = []

    # ===== PHASE 1 : Articles 1-30 — Lundi a vendredi, 1 par jour =====
    current_date = start_date
    count = 0
    while count < 30:
        # 0=lundi, 4=vendredi — on skip samedi(5) et dimanche(6)
        if current_date.weekday() <= 4:
            hour, minute = random_time_between_7h35_and_10h17()
            pub_datetime = datetime.combine(current_date, datetime.min.time().replace(hour=hour, minute=minute))
            schedule.append(pub_datetime)
            count += 1
        current_date += timedelta(days=1)

    # ===== PHASE 2 : Articles 31-100 — Tous les 2 jours, lundi-samedi, alternance =====
    # On commence la phase 2 le lundi suivant la fin de la phase 1
    phase2_start = current_date
    while phase2_start.weekday() != 0:  # Avancer jusqu'au prochain lundi
        phase2_start += timedelta(days=1)

    current_date = phase2_start
    count = 0
    week_type = "A"  # A = commence lundi, B = commence mardi

    while count < 70:
        # Determiner les jours de publication de cette semaine
        monday_of_week = current_date - timedelta(days=current_date.weekday())

        if week_type == "A":
            # Semaine A : lundi, mercredi, vendredi
            pub_days = [
                monday_of_week,                        # Lundi
                monday_of_week + timedelta(days=2),    # Mercredi
                monday_of_week + timedelta(days=4),    # Vendredi
            ]
        else:
            # Semaine B : mardi, jeudi, samedi
            pub_days = [
                monday_of_week + timedelta(days=1),    # Mardi
                monday_of_week + timedelta(days=3),    # Jeudi
                monday_of_week + timedelta(days=5),    # Samedi
            ]

        # Filtrer les jours passes (pour la premiere semaine partielle)
        pub_days = [d for d in pub_days if d >= current_date]

        for pub_date in pub_days:
            if count >= 70:
                break
            hour, minute = random_time_between_7h35_and_10h17()
            pub_datetime = datetime.combine(pub_date, datetime.min.time().replace(hour=hour, minute=minute))
            schedule.append(pub_datetime)
            count += 1

        # Passer a la semaine suivante et alterner le type
        current_date = monday_of_week + timedelta(days=7)
        week_type = "B" if week_type == "A" else "A"

    return schedule

if __name__ == "__main__":
    schedule = generate_schedule()
    print(f"Planning genere : {len(schedule)} publications\n")
    print("=== PHASE 1 : Articles 1-30 (lundi-vendredi, quotidien) ===")
    for i, dt in enumerate(schedule[:30], 1):
        day_name = ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"][dt.weekday()]
        print(f"  Article {i:3d} -> {day_name} {dt.strftime('%d/%m/%Y a %Hh%M')}")

    print(f"\n=== PHASE 2 : Articles 31-100 (lun-sam, tous les 2 jours, alternance) ===")
    for i, dt in enumerate(schedule[30:], 31):
        day_name = ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"][dt.weekday()]
        print(f"  Article {i:3d} -> {day_name} {dt.strftime('%d/%m/%Y a %Hh%M')}")

    print(f"\nPremiere publication : {schedule[0].strftime('%d/%m/%Y a %Hh%M')}")
    print(f"Derniere publication : {schedule[-1].strftime('%d/%m/%Y a %Hh%M')}")
    total_days = (schedule[-1] - schedule[0]).days
    print(f"Duree totale : {total_days} jours (~{total_days // 7} semaines)")
