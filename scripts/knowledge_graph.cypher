// MycoMind Knowledge Graph - Generated Cypher Statements
// Generated on: 2025-06-02T21:51:39.583714
// Schema: HyphalTips MycoMind Schema

// Uncomment to clear existing data (use with caution)
// MATCH (n) DETACH DELETE n;

// Create index for HyphalTip entities
CREATE INDEX ON :HyphalTip(iri);
// Create index for Project entities
CREATE INDEX ON :Project(iri);
// Create index for RegenerativePerson entities
CREATE INDEX ON :RegenerativePerson(iri);

// Create entities
CREATE (:RegenerativePerson {iri: "http://mycomind.org/kg/resource/RegenerativePerson/Shawn", name: "Shawn", type: "RegenerativePerson", bio: "A brilliant developer with a background in semantic web technologies, working on problems in the context of bioregional mapping and community resilience.", created: "2025-06-02T20:50:33.191531", currentRole: "Developer", extraction_confidence: 0.95, extraction_date: "2025-06-02T20:50:33.190727", location: "Portland", organization: "Small consultancy focused on helping communities build their own knowledge commons using open source tools", source_file: "examples/sample_data/mycomind_project.txt"});
CREATE (:Project {iri: "http://mycomind.org/kg/resource/Project/unnamed_entity", name: "unnamed_entity", type: "Project", created: "2025-06-02T20:50:33.192180", endDate: "Not specified", extraction_confidence: 0.85, extraction_date: "2025-06-02T20:50:33.190727", source_file: "examples/sample_data/mycomind_project.txt", startDate: "Not specified", status: "in-progress"});
CREATE (:HyphalTip {iri: "http://mycomind.org/kg/resource/HyphalTip/MycoMind_Personal_Knowledge_Management_System", name: "MycoMind: Personal Knowledge Management System", type: "HyphalTip", activityStatus: "alive", created: "2025-06-02T20:50:33.190734", description: "A project to build a personal knowledge management system that uses AI and knowledge graphs to create a living, breathing representation of everything one knows and learns.", extraction_confidence: 1.0, extraction_date: "2025-06-02T20:50:33.190727", source_file: "examples/sample_data/mycomind_project.txt"});

// Create placeholder nodes for referenced entities that don't exist yet
CREATE (:Entity {iri: "http://mycomind.org/kg/resource/Small_consultancy_focused_on_helping_communities_build_their_own_knowledge_commons_using_open_source_tools", name: "Small consultancy focused on helping communities build their own knowledge commons using open source tools", type: "Entity"});
CREATE (:Entity {iri: "http://mycomind.org/kg/resource/Transition_Towns_movement", name: "Transition Towns movement", type: "Entity"});

// Create relationships
MATCH (a), (b) WHERE a.iri = "http://mycomind.org/kg/resource/RegenerativePerson/Shawn" AND b.iri = "http://mycomind.org/kg/resource/MycoMind_Personal_Knowledge_Management_System" CREATE (a)-[:COLLABORATESWITH]->(b);
MATCH (a), (b) WHERE a.iri = "http://mycomind.org/kg/resource/RegenerativePerson/Shawn" AND b.iri = "http://mycomind.org/kg/resource/Transition_Towns_movement" CREATE (a)-[:MEMBEROF]->(b);
MATCH (a), (b) WHERE a.iri = "http://mycomind.org/kg/resource/RegenerativePerson/Shawn" AND b.iri = "http://mycomind.org/kg/resource/Small_consultancy_focused_on_helping_communities_build_their_own_knowledge_commons_using_open_source_tools" CREATE (a)-[:WORKSFOR]->(b);
MATCH (a), (b) WHERE a.iri = "http://mycomind.org/kg/resource/HyphalTip/MycoMind_Personal_Knowledge_Management_System" AND b.iri = "http://mycomind.org/kg/resource/RegenerativePerson/Shawn" CREATE (a)-[:COLLABORATOR]->(b);
MATCH (a), (b) WHERE a.iri = "http://mycomind.org/kg/resource/HyphalTip/MycoMind_Personal_Knowledge_Management_System" AND b.iri = "http://mycomind.org/kg/resource/HyphalTip/MycoMind_Personal_Knowledge_Management_System" CREATE (a)-[:HASNOTE]->(b);