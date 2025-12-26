import time
import random
import psycopg2
from datetime import datetime

# Игроки
PLAYER_IDS = list(range(1, 6))  # 5 игроков

# Состояние каждого игрока
player_states = {
    player_id: {
        "current_enemy": None,
        "session_start": None,
        "level": 1,
        "last_activity_time": 0  # время последнего действия (в секундах)
    } for player_id in PLAYER_IDS
}

def connect_to_db():
    while True:
        try:
            conn = psycopg2.connect(
                host="db",
                database="analytics_db",
                user="user",
                password="pass"
            )
            print("✅ Подключено к базе данных")
            return conn
        except psycopg2.OperationalError as e:
            print("❌ Ошибка подключения к БД, жду 2 сек... Ошибка:", e)
            time.sleep(2)

def generate_event(player_id):
    state = player_states[player_id]
    current_time = time.time()

    # Если прошло больше 5 секунд с последнего действия — можно менять активность
    if current_time - state["last_activity_time"] > 5:
        event_types = ['attack', 'kill', 'rest']
        if state["level"] < 3:
            weights = [0.7, 0.2, 0.1]  # чаще атакует слабых
        else:
            weights = [0.5, 0.4, 0.1]  # больше убийств
        event_type = random.choices(event_types, weights=weights)[0]
    else:
        # Продолжаем текущее действие
        event_type = 'attack' if state["current_enemy"] else 'rest'

    enemy_type = random.choice(['Goblin', 'Orc', 'Wolf', 'Skeleton'])
    ability = random.choice(['Slash', 'Fireball', 'Arrow', 'Heal', 'None'])

    if event_type == 'attack':
        damage = random.randint(10, 50)  # 10–50 урона за атаку
        exp = random.randint(1, 5)       # 1–5 опыта за атаку
        duration = 0
        state["current_enemy"] = enemy_type
    elif event_type == 'kill':
        # Убийство даёт больше опыта, но редко происходит
        damage = random.randint(30, 80)   # 30–80 урона при убийстве
        exp = random.randint(10, 30)      # 10–30 опыта за убийство
        duration = random.randint(10, 30) # 10–30 секунд после убийства
        state["current_enemy"] = None
        # Шанс повысить уровень
        if random.random() < 0.1:
            state["level"] += 1
    else:  # rest
        damage = 0
        exp = 0
        duration = random.randint(15, 60) # 15–60 секунд отдыха
        state["current_enemy"] = None

    # Обновляем время последнего действия
    state["last_activity_time"] = current_time

    return {
        'player_id': player_id,
        'enemy_type': enemy_type if event_type != 'rest' else None,
        'damage_dealt': damage,
        'experience_gained': exp,
        'ability_used': ability,
        'session_duration_sec': duration,
        'event_type': event_type
    }

def main():
    print("🔄 Запуск генератора игровых событий...")
    conn = connect_to_db()
    cursor = conn.cursor()

    print("🟢 Генератор начал работу. События каждые 3 секунды.\n")

    try:
        while True:
            for player_id in PLAYER_IDS:
                event = generate_event(player_id)

                cursor.execute(
                    """
                    INSERT INTO game_events 
                    (player_id, enemy_type, damage_dealt, experience_gained, 
                     ability_used, session_duration_sec, event_type)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        event['player_id'],
                        event['enemy_type'],
                        event['damage_dealt'],
                        event['experience_gained'],
                        event['ability_used'],
                        event['session_duration_sec'],
                        event['event_type']
                    )
                )

            conn.commit()

            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"[{timestamp}] Добавлено {len(PLAYER_IDS)} игровых событий")

            time.sleep(3)

    except KeyboardInterrupt:
        print("\n🛑 Генератор остановлен.")
    except Exception as e:
        print("❗ Ошибка:", e)
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    main()
