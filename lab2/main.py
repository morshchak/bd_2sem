import redis
from src import config, Chat
from src.scenes.GreetingScene import GreetingScene

def main():
    r = redis.Redis(host=config.redis_config['host'], port=config.redis_config['port'], db=config.redis_config['db'],
                    charset="utf-8", decode_responses=True)
    session = {
        'chat': Chat(r)
    }
    GreetingScene(session, r).enter()


if __name__ == '__main__':
    main()
