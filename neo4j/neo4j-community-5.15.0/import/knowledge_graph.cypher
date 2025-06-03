// MycoMind Knowledge Graph - Generated Cypher Statements
// Generated on: 2025-06-02T20:40:56.604776
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
CREATE (:RegenerativePerson {iri: "http://mycomind.org/kg/resource/RegenerativePerson/Shawn", name: "Shawn", type: "RegenerativePerson", bio: "A brilliant developer with a background in semantic web technologies, working on problems in the context of bioregional mapping and community resilience. Involved with the Transition Towns movement.", created: "2025-06-02T18:29:57.849340", currentRole: "Developer", extraction_confidence: 0.95, extraction_date: "2025-06-02T18:29:57.845911", location: "Portland", organization: "Small consultancy focused on helping communities build their own knowledge commons using open source tools", source_file: "examples/sample_data/mycomind_project.txt"});
CREATE (:Project {iri: "http://mycomind.org/kg/resource/Project/MycoMind", name: "MycoMind", type: "Project", created: "2025-06-02T18:29:57.851452", description: "A project to build a personal knowledge management system that uses AI and knowledge graphs to create a living, breathing representation of everything one knows and learns.", extraction_confidence: 1.0, extraction_date: "2025-06-02T18:29:57.845911", source_file: "examples/sample_data/mycomind_project.txt", status: "in-progress"});
CREATE (:HyphalTip {iri: "http://mycomind.org/kg/resource/HyphalTip/MycoMind_Personal_Knowledge_Management_System", name: "MycoMind: Personal Knowledge Management System", type: "HyphalTip", activityStatus: "alive", created: "2025-06-02T18:29:57.845957", description: "A project to build a personal knowledge management system that uses AI and knowledge graphs to create a living, breathing representation of everything one knows and learns.", extraction_confidence: 1.0, extraction_date: "2025-06-02T18:29:57.845911", source_file: "examples/sample_data/mycomind_project.txt"});

// Create placeholder nodes for referenced entities that don't exist yet
CREATE (:Entity {iri: "http://mycomind.org/kg/resource/Next_steps_for_MycoMind", name: "Next steps for MycoMind", type: "Entity"});
CREATE (:Entity {iri: "http://mycomind.org/kg/resource/MycoMind_technical_architecture", name: "MycoMind technical architecture", type: "Entity"});
CREATE (:Entity {iri: "http://mycomind.org/kg/resource/Entity_linking_challenge", name: "Entity linking challenge", type: "Entity"});
CREATE (:Entity {iri: "http://mycomind.org/kg/resource/Transition_Towns_movement", name: "Transition Towns movement", type: "Entity"});

// Create relationships
MATCH (a), (b) WHERE a.iri = "http://mycomind.org/kg/resource/RegenerativePerson/Shawn" AND b.iri = "http://mycomind.org/kg/resource/MycoMind_Personal_Knowledge_Management_System" CREATE (a)-[:COLLABORATESWITH]->(b);
MATCH (a), (b) WHERE a.iri = "http://mycomind.org/kg/resource/RegenerativePerson/Shawn" AND b.iri = "http://mycomind.org/kg/resource/Transition_Towns_movement" CREATE (a)-[:MEMBEROF]->(b);
MATCH (a), (b) WHERE a.iri = "http://mycomind.org/kg/resource/HyphalTip/MycoMind_Personal_Knowledge_Management_System" AND b.iri = "http://mycomind.org/kg/resource/RegenerativePerson/Shawn" CREATE (a)-[:COLLABORATOR]->(b);
MATCH (a), (b) WHERE a.iri = "http://mycomind.org/kg/resource/HyphalTip/MycoMind_Personal_Knowledge_Management_System" AND b.iri = "http://mycomind.org/kg/resource/MycoMind_technical_architecture" CREATE (a)-[:HASNOTE]->(b);
MATCH (a), (b) WHERE a.iri = "http://mycomind.org/kg/resource/HyphalTip/MycoMind_Personal_Knowledge_Management_System" AND b.iri = "http://mycomind.org/kg/resource/Entity_linking_challenge" CREATE (a)-[:HASNOTE]->(b);
MATCH (a), (b) WHERE a.iri = "http://mycomind.org/kg/resource/HyphalTip/MycoMind_Personal_Knowledge_Management_System" AND b.iri = "http://mycomind.org/kg/resource/Next_steps_for_MycoMind" CREATE (a)-[:HASNOTE]->(b);