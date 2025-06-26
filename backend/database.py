from cassandra.cluster import Cluster, Session
from cassandra.auth import PlainTextAuthProvider
from cassandra.cqlengine import connection
from cassandra.cqlengine.management import sync_table, create_keyspace_simple
from contextlib import contextmanager
import logging
from backend.config import settings

# Configuration de la connexion Cassandra
def get_cassandra_cluster():
    """Crée et retourne un cluster Cassandra"""
    auth_provider = PlainTextAuthProvider(
        username=settings.CASSANDRA_USERNAME,
        password=settings.CASSANDRA_PASSWORD
    )
    
    # Diviser les hosts si plusieurs sont spécifiés
    contact_points = settings.CASSANDRA_HOSTS.split(",") if settings.CASSANDRA_HOSTS else ["localhost"]
    
    cluster = Cluster(
        contact_points=contact_points,
        port=settings.CASSANDRA_PORT,
        auth_provider=auth_provider,
        protocol_version=4
    )
    
    return cluster

def get_cassandra_session() -> Session:
    """Retourne une session Cassandra"""
    cluster = get_cassandra_cluster()
    session = cluster.connect()
    
    # Créer le keyspace s'il n'existe pas
    session.execute(f"""
        CREATE KEYSPACE IF NOT EXISTS {settings.CASSANDRA_KEYSPACE}
        WITH replication = {{
            'class': 'SimpleStrategy',
            'replication_factor': 1
        }}
    """)
    
    # Utiliser le keyspace
    session.set_keyspace(settings.CASSANDRA_KEYSPACE)
    return session

def setup_cassandra_connection():
    """Configure la connexion Cassandra pour cqlengine"""
    try:
        # Diviser les hosts si plusieurs sont spécifiés
        hosts = settings.CASSANDRA_HOSTS.split(",") if settings.CASSANDRA_HOSTS else ["localhost"]
        
        # Configuration de la connexion pour cqlengine
        connection.setup(
            hosts=hosts,
            default_keyspace=settings.CASSANDRA_KEYSPACE,
            protocol_version=4,
            auth_provider=PlainTextAuthProvider(
                username=settings.CASSANDRA_USERNAME,
                password=settings.CASSANDRA_PASSWORD
            )
        )
        
        # Créer le keyspace s'il n'existe pas
        cluster = get_cassandra_cluster()
        session = cluster.connect()
        session.execute(f"""
            CREATE KEYSPACE IF NOT EXISTS {settings.CASSANDRA_KEYSPACE}
            WITH replication = {{
                'class': 'SimpleStrategy',
                'replication_factor': 1
            }}
        """)
        session.shutdown()
        cluster.shutdown()
        
        logging.info("✅ Connexion Cassandra configurée avec succès")
    except Exception as e:
        logging.error(f"❌ Erreur configuration Cassandra: {e}")
        raise

@contextmanager
def get_cassandra_session_context():
    """Context manager pour les sessions Cassandra"""
    cluster = get_cassandra_cluster()
    session = cluster.connect(settings.CASSANDRA_KEYSPACE)
    try:
        yield session
    except Exception as e:
        logging.error(f"Erreur session Cassandra: {e}")
        raise
    finally:
        session.shutdown()
        cluster.shutdown()

def create_tables():
    """Crée toutes les tables dans Cassandra"""
    try:
        from backend.models.product import Product
        
        # Synchroniser les tables
        sync_table(Product)
        logging.info("✅ Tables Cassandra créées avec succès")
    except Exception as e:
        logging.error(f"❌ Erreur création des tables: {e}")
        raise

def check_database_connection() -> bool:
    """Vérifie la connexion à Cassandra"""
    try:
        with get_cassandra_session_context() as session:
            session.execute("SELECT release_version FROM system.local")
        logging.info("✅ Connexion à Cassandra réussie")
        return True
    except Exception as e:
        logging.error(f"❌ Erreur connexion Cassandra: {e}")
        return False

# Initialiser la connexion au démarrage
setup_cassandra_connection() 