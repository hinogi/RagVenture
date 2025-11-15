# Image herunterladen (wie "apt-get install")
docker pull neo4j:latest

# Container starten (Image wird automatisch gepullt, falls nicht da)
docker run -d \                    # -d = detached (läuft im Hintergrund)
    --name textadventure-neo4j \   # Name für den Container
    -p 7474:7474 \                 # Port-Mapping (Host:Container)
    -p 7687:7687 \                 # Bolt-Port für Python
    -e NEO4J_AUTH=neo4j/password \ # Environment Variable (Login)
    neo4j:latest                   # Image-Name

**Container 1: Entwicklungs-DB**
docker run -d \
    --name textadv-dev \
    -p 7474:7474 \
    -p 7687:7687 \
    -e NEO4J_AUTH=neo4j/devpass \
    neo4j:latest

**Container 2: Test-DB (andere Ports!)**
docker run -d \
    --name textadv-test \
    -p 7475:7474 \
    -p 7688:7687 \
    -e NEO4J_AUTH=neo4j/testpass \
    neo4j:latest

**Container 3: Backup/Experimentierdatenbank**
docker run -d \
    --name textadv-backup \
    -p 7476:7474 \
    -p 7689:7687 \
    -e NEO4J_AUTH=neo4j/backup \
    neo4j:latest

# Was läuft gerade?
docker ps

# Container stoppen
docker stop mein-neo4j

# Container starten (nach Stopp)
docker start mein-neo4j

# Container löschen
docker rm mein-neo4j

# Logs ansehen (bei Problemen)
docker logs mein-neo4j