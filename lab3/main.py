import redis
from src import config, Chat
from src.scenes.GreetingScene import GreetingScene
from neo4j import GraphDatabase


def main():
    r = redis.Redis(host=config.redis_config['host'], port=config.redis_config['port'], db=config.redis_config['db'],
                    charset="utf-8", decode_responses=True)
    driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "crash-robert-profile-green-finance-6499"))
    session = {
        'chat': Chat(r, driver)
    }
    GreetingScene(session, r, driver).enter()


if __name__ == "__main__":
    main()
