-- current_location
    MATCH (p:Player {id: 'player_no1'})-[:IST_IN]->(place:Location)
    RETURN place.id, place.name, place.description

-- location_connections
    MATCH (l:Location {id: $current_location})-[:ERREICHT]->(target:Location)
    RETURN target.id, target.name, target.description

-- current_inventory
    MATCH (p:Player {id: 'player_no1'})-[:TRÄGT]->(i:Item)
    RETURN i.name

-- move_player
    MATCH (p:Player {id: 'player_no1'})-[old:IST_IN]->(current:Location)
    MATCH (current)-[:ERREICHT]->(target:Location {id: $target_location})
    DELETE old
    CREATE (p)-[:IST_IN]->(target)
    RETURN target.id, target.name, target.description

-- take_item
    MATCH (p:Player {id: 'player_no1'})-[:IST_IN]->(loc:Location)
    MATCH (i:Item {id: $item})-[old:IST_IN]->(loc)
    DELETE old
    CREATE (p)-[:TRÄGT]->(item)
    RETURN i.name, loc.name

-- use_item

