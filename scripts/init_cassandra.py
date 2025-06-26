#!/usr/bin/env python3
"""
Script d'initialisation de Cassandra pour SoGood
"""

import logging
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
from cassandra.cqlengine import connection
from cassandra.cqlengine.management import sync_table
from backend.config import settings
from backend.models.product import Product

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_cassandra():
    """Initialise Cassandra et crée les tables"""
    try:
        logger.info("🚀 Initialisation de Cassandra...")
        
        # Configuration de l'authentification
        auth_provider = PlainTextAuthProvider(
            username=settings.CASSANDRA_USERNAME,
            password=settings.CASSANDRA_PASSWORD
        )
        
        # Connexion au cluster
        cluster = Cluster(
            contact_points=settings.CASSANDRA_HOSTS,
            port=settings.CASSANDRA_PORT,
            auth_provider=auth_provider,
            protocol_version=4
        )
        
        session = cluster.connect()
        logger.info("✅ Connexion à Cassandra établie")
        
        # Créer le keyspace
        session.execute(f"""
            CREATE KEYSPACE IF NOT EXISTS {settings.CASSANDRA_KEYSPACE}
            WITH replication = {{
                'class': 'SimpleStrategy',
                'replication_factor': 1
            }}
        """)
        logger.info(f"✅ Keyspace '{settings.CASSANDRA_KEYSPACE}' créé")
        
        # Utiliser le keyspace
        session.set_keyspace(settings.CASSANDRA_KEYSPACE)
        
        # Configuration de cqlengine
        connection.setup(
            hosts=settings.CASSANDRA_HOSTS,
            default_keyspace=settings.CASSANDRA_KEYSPACE,
            protocol_version=4,
            auth_provider=auth_provider
        )
        
        # Synchroniser les tables
        sync_table(Product)
        logger.info("✅ Tables synchronisées")
        
        # Vérifier la création
        result = session.execute("SELECT table_name FROM system_schema.tables WHERE keyspace_name = %s", 
                               [settings.CASSANDRA_KEYSPACE])
        tables = [row.table_name for row in result]
        logger.info(f"📊 Tables créées: {tables}")
        
        session.shutdown()
        cluster.shutdown()
        
        logger.info("🎉 Initialisation Cassandra terminée avec succès!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erreur initialisation Cassandra: {e}")
        logger.exception("Détails de l'exception:")
        return False

if __name__ == "__main__":
    success = init_cassandra()
    exit(0 if success else 1) 