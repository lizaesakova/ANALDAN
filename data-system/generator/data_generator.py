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
        "level": 1
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
    event_types = ['attack', 'kill', 'rest']
    
    # Поведение зависит от уровня
    if state["level"] < 3:
        weights = [0.7, 0.2, 0.1]  # чаще атакует слабых
    else:
        weights = [0.5, 0.4, 0.1]  # больше убийств
    
    event_type = random.choices(event_types, weights=weights)[0]

    enemy_type = random.choice(['Goblin', 'Orc', 'Wolf', 'Skeleton'])
    ability = random.choice(['Slash', 'Fireball', 'Arrow', 'Heal', 'None'])

    if event_type == 'attack':
        damage = random.randint(10, 30)
        exp = random.randint(5, 15)
        duration = 0
        state["current_enemy"] = enemy_type
    elif event_type == 'kill':
        damage = random.randint(20, 40)
        exp = random.randint(20, 50)
        duration = random.randint(60, 180)
        state["current_enemy"] = None
        # Шанс повысить уровень
        if random.random() < 0.3:
            state["level"] += 1
    else:  # rest
        damage = 0
        exp = 0
        duration = random.randint(30, 120)
        state["current_enemy"] = None

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