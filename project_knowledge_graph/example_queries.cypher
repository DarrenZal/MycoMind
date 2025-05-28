// MycoMind Project Knowledge Graph - Example Queries
// This file contains example Cypher queries to explore the MycoMind project structure

// =============================================================================
// BASIC EXPLORATION QUERIES
// =============================================================================

// 1. Overview of the project structure
MATCH (n)
RETURN labels(n)[0] as NodeType, count(n) as Count
ORDER BY Count DESC;

// 2. List all Python modules and their purposes
MATCH (m:PythonModule)
RETURN m.name as Module, m.docstring as Purpose, m.line_count as Lines
ORDER BY m.name;

// 3. Show all system components and their responsibilities
MATCH (c:Component)
RETURN c.name as Component, c.type as Type, c.responsibility as Responsibility
ORDER BY c.type, c.name;

// =============================================================================
// CODE STRUCTURE ANALYSIS
// =============================================================================

// 4. Find all functions in a specific module
MATCH (m:PythonModule {name: "main_etl.py"})-[:CONTAINS|DEFINES*]->(f:PythonFunction)
RETURN f.name as Function, f.signature as Signature, f.complexity as Complexity
ORDER BY f.name;

// 5. Show class hierarchy and methods
MATCH (c:PythonClass)-[:HAS_METHOD]->(f:PythonFunction)
RETURN c.name as Class, collect(f.name) as Methods
ORDER BY c.name;

// 6. Find module dependencies (import relationships)
MATCH (m1:PythonModule)-[:IMPORTS]->(m2:PythonModule)
RETURN m1.name as ImportingModule, m2.name as ImportedModule
ORDER BY m1.name;

// 7. Identify the most connected functions (high fan-in)
MATCH (f:PythonFunction)<-[:CALLS]-(caller:PythonFunction)
WITH f, count(caller) as callers
WHERE callers > 1
RETURN f.name as Function, f.signature as Signature, callers as CalledBy
ORDER BY callers DESC;

// 8. Find functions with high complexity
MATCH (f:PythonFunction)
WHERE f.complexity IN ['high', 'very_high']
RETURN f.name as Function, f.complexity as Complexity, f.signature as Signature
ORDER BY f.complexity DESC, f.name;

// =============================================================================
// FEATURE AND COMPONENT ANALYSIS
// =============================================================================

// 9. Map features to their implementations
MATCH (feature:Feature)-[:IMPLEMENTED_BY]->(impl)
RETURN feature.name as Feature, 
       feature.status as Status,
       labels(impl)[0] as ImplementationType,
       impl.name as Implementation
ORDER BY feature.name;

// 10. Show component dependencies
MATCH (c1:Component)-[:DEPENDS_ON]->(c2:Component)
RETURN c1.name as Component, c2.name as DependsOn
ORDER BY c1.name;

// 11. Find features by development status
MATCH (f:Feature)
WHERE f.status = 'implemented'
RETURN f.name as Feature, f.priority as Priority, f.complexity as Complexity
ORDER BY f.priority DESC, f.name;

// 12. Identify critical features and their implementations
MATCH (f:Feature {priority: 'critical'})-[:IMPLEMENTED_BY]->(impl)
RETURN f.name as CriticalFeature, 
       f.description as Description,
       labels(impl)[0] as ImplementedBy,
       impl.name as Implementation;

// =============================================================================
// DOCUMENTATION ANALYSIS
// =============================================================================

// 13. Show documentation structure
MATCH (doc:DocFile)-[:CONTAINS]->(section:DocSection)
RETURN doc.name as Document, 
       collect(section.name) as Sections,
       doc.word_count as TotalWords
ORDER BY doc.name;

// 14. Find documentation for specific features
MATCH (feature:Feature {name: "Semantic Linking"})<-[:DESCRIBES]-(section:DocSection)
RETURN section.name as Section, 
       section.section_type as Type,
       section.word_count as Words;

// 15. Cross-reference documentation and code
MATCH (section:DocSection)-[:REFERENCES]->(func:PythonFunction)
RETURN section.name as DocumentationSection, 
       func.name as ReferencedFunction,
       func.signature as FunctionSignature
ORDER BY section.name;

// 16. Find undocumented functions
MATCH (f:PythonFunction)
WHERE NOT EXISTS((f)<-[:REFERENCES]-(:DocSection))
RETURN f.name as UndocumentedFunction, 
       f.signature as Signature,
       f.complexity as Complexity
ORDER BY f.complexity DESC, f.name;

// =============================================================================
// CONFIGURATION ANALYSIS
// =============================================================================

// 17. Show configuration impact on components
MATCH (config:Configuration)-[:AFFECTS]->(component:Component)
RETURN config.name as ConfigOption,
       config.type as Type,
       config.required as Required,
       component.name as AffectedComponent
ORDER BY config.name;

// 18. Find required vs optional configurations
MATCH (c:Configuration)
RETURN c.required as Required, 
       count(c) as Count,
       collect(c.name) as Configurations
ORDER BY Required DESC;

// =============================================================================
// CONCEPT AND KNOWLEDGE ANALYSIS
// =============================================================================

// 19. Explore concept relationships
MATCH (c1:Concept)-[:RELATED_TO]-(c2:Concept)
RETURN c1.name as Concept1, c2.name as Concept2, c1.importance as Importance
ORDER BY c1.importance DESC;

// 20. Find concepts by domain
MATCH (c:Concept)
RETURN c.domain as Domain, 
       collect(c.name) as Concepts,
       count(c) as ConceptCount
ORDER BY ConceptCount DESC;

// 21. Map concepts to their implementations
MATCH (concept:Concept)-[:IMPLEMENTED_BY]->(impl)
RETURN concept.name as Concept,
       concept.definition as Definition,
       labels(impl)[0] as ImplementationType,
       impl.name as Implementation
ORDER BY concept.importance DESC;

// =============================================================================
// ADVANCED ANALYSIS QUERIES
// =============================================================================

// 22. Find potential refactoring opportunities
MATCH (f:PythonFunction)<-[:CALLS]-(caller)
WITH f, count(caller) as usage
WHERE usage > 2 AND f.complexity IN ['high', 'very_high']
RETURN f.name as Function,
       f.signature as Signature,
       usage as UsageCount,
       f.complexity as Complexity
ORDER BY usage DESC, f.complexity DESC;

// 23. Analyze feature dependencies and complexity
MATCH path = (f1:Feature)-[:DEPENDS_ON*1..3]->(f2:Feature)
RETURN f1.name as Feature,
       f2.name as DependsOn,
       length(path) as DependencyDepth,
       f1.complexity as FeatureComplexity
ORDER BY DependencyDepth DESC, FeatureComplexity DESC;

// 24. Find documentation coverage gaps
MATCH (component:Component)
OPTIONAL MATCH (component)<-[:DESCRIBES]-(section:DocSection)
WITH component, count(section) as docSections
WHERE docSections = 0
RETURN component.name as UndocumentedComponent,
       component.type as ComponentType,
       component.responsibility as Responsibility;

// 25. Trace feature implementation paths
MATCH path = (feature:Feature)-[:IMPLEMENTED_BY*1..2]->(code)
WHERE feature.name = "Ontology-Driven Extraction"
RETURN feature.name as Feature,
       [node in nodes(path) | node.name] as ImplementationPath,
       [rel in relationships(path) | type(rel)] as RelationshipTypes;

// =============================================================================
// KNOWLEDGE DISCOVERY QUERIES
// =============================================================================

// 26. Find related concepts and their implementations
MATCH (concept1:Concept)-[:RELATED_TO]-(concept2:Concept)
OPTIONAL MATCH (concept1)-[:IMPLEMENTED_BY]->(impl1)
OPTIONAL MATCH (concept2)-[:IMPLEMENTED_BY]->(impl2)
RETURN concept1.name as Concept1,
       concept2.name as RelatedConcept,
       impl1.name as Implementation1,
       impl2.name as Implementation2
ORDER BY concept1.importance DESC;

// 27. Analyze system complexity by component
MATCH (component:Component)<-[:IMPLEMENTED_BY]-(module:PythonModule)
OPTIONAL MATCH (module)-[:CONTAINS]->(cls:PythonClass)-[:HAS_METHOD]->(func:PythonFunction)
WITH component, module, count(func) as functionCount, avg(toInteger(
  CASE func.complexity 
    WHEN 'low' THEN 1 
    WHEN 'medium' THEN 2 
    WHEN 'high' THEN 3 
    WHEN 'very_high' THEN 4 
    ELSE 1 
  END
)) as avgComplexity
RETURN component.name as Component,
       functionCount as Functions,
       round(avgComplexity * 100) / 100 as AverageComplexity
ORDER BY avgComplexity DESC;

// 28. Find learning paths through concepts
MATCH path = (start:Concept)-[:PREREQUISITE_FOR*1..3]->(end:Concept)
WHERE start.importance = 'fundamental'
RETURN start.name as StartingConcept,
       end.name as AdvancedConcept,
       length(path) as LearningSteps,
       [node in nodes(path) | node.name] as LearningPath
ORDER BY LearningSteps, start.name;

// =============================================================================
// VISUALIZATION QUERIES
// =============================================================================

// 29. Component dependency graph (for visualization)
MATCH (c:Component)-[r:DEPENDS_ON]->(dep:Component)
RETURN c, r, dep
LIMIT 20;

// 30. Feature implementation network
MATCH (f:Feature)-[r:IMPLEMENTED_BY]->(impl)
RETURN f, r, impl
LIMIT 25;

// 31. Documentation structure visualization
MATCH (doc:DocFile)-[:CONTAINS]->(section:DocSection)-[:DESCRIBES]->(component:Component)
RETURN doc, section, component
LIMIT 15;

// =============================================================================
// MAINTENANCE AND QUALITY QUERIES
// =============================================================================

// 32. Find orphaned nodes (nodes with no relationships)
MATCH (n)
WHERE NOT (n)--()
RETURN labels(n)[0] as NodeType, n.name as Name
ORDER BY NodeType, Name;

// 33. Identify nodes with the most relationships
MATCH (n)
WITH n, size((n)--()) as relationshipCount
WHERE relationshipCount > 0
RETURN labels(n)[0] as NodeType, 
       n.name as Name, 
       relationshipCount as Relationships
ORDER BY relationshipCount DESC
LIMIT 10;

// 34. Find duplicate or similar names across different node types
MATCH (n1), (n2)
WHERE id(n1) < id(n2) 
  AND n1.name = n2.name 
  AND labels(n1) <> labels(n2)
RETURN n1.name as Name, 
       labels(n1)[0] as Type1, 
       labels(n2)[0] as Type2;

// =============================================================================
// EXPORT QUERIES
// =============================================================================

// 35. Export function call graph for external analysis
MATCH (f1:PythonFunction)-[:CALLS]->(f2:PythonFunction)
RETURN f1.name as Caller, 
       f2.name as Called,
       f1.complexity as CallerComplexity,
       f2.complexity as CalledComplexity;

// 36. Export component architecture for documentation
MATCH (c:Component)
OPTIONAL MATCH (c)-[:DEPENDS_ON]->(dep:Component)
OPTIONAL MATCH (c)<-[:IMPLEMENTED_BY]-(impl:PythonModule)
RETURN c.name as Component,
       c.type as Type,
       c.responsibility as Responsibility,
       collect(DISTINCT dep.name) as Dependencies,
       collect(DISTINCT impl.name) as Implementations;
