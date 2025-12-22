AI-Based YAML Consistency Validation

Objective
Use AI reasoning abilities (not script generation) to validate that YAML file(s) in notion/2-documentation/1-specifications/1-databases/5-yaml-configuration/output/ follow all optimization rules specified in yaml-mapping-reference.yaml.

Important: AI-Based Analysis Only
DO NOT generate validation scripts
DO use AI's semantic understanding to analyze the YAML structure
DO use pattern recognition to identify inconsistencies
DO provide human-readable analysis and recommendations
Why AI Validation is Preferable
Semantic Understanding: AI can understand context and intent, not just syntax
Pattern Recognition: Can identify subtle inconsistencies that rule-based scripts might miss
Nuanced Analysis: Can distinguish between intentional omissions (e.g., "none" units) and actual errors
Comprehensive Reporting: Can provide detailed explanations and recommendations
Analysis Approach
1. File Discovery
Dynamic Discovery: Find all .yaml files in the output folder using list_dir or glob_file_search
No Hardcoding: Do not hardcode specific filenames (they change over time)
Read Files: Use read_file to load both the reference spec and generated YAML(s)
2. Structural Validation (AI Analysis)
Verify top-level structure: version, provider, mappings
Check all mapping entries have required fields
Validate YAML syntax and formatting
AI Insight: Identify structural patterns and anomalies
3. Optimization Rules Verification (8 Rules)
Rule 1: Top-level type field
AI Check: Verify all mappings have type field at top level
Expected Values: direct, prioritized, calculated, transformed, io_mapped
AI Analysis: Identify any missing or invalid type values
Rule 2: Source-level type field omission
AI Check: Direct provider sources should NOT have type: direct (it's the default)
Expected: Only calculated sources in prioritized mappings should have type: calculated
AI Analysis: Use pattern recognition to find violations
Rule 3: Source-level provider field omission
AI Check: Sources should NOT have provider field when it matches top-level provider
Expected: Only include provider when source uses different provider
AI Analysis: Compare source providers with top-level provider
Rule 4: Source-level priority field omission
AI Check: Single-source mappings should NOT have priority field
Expected: Only multiple-source (prioritized) mappings should have priority
AI Analysis: Count sources per mapping and verify priority usage
Rule 5: Description field omission
AI Check: No description fields should exist (use comments instead)
Expected: Field Path and Computation Approach should be in comments only
AI Analysis: Search for description fields vs. comment usage
Rule 6: Dependencies field omission
AI Check: dependencies should be omitted when redundant with parameters.fleeti
Expected: Calculated mappings should only have parameters.fleeti, not dependencies
AI Analysis: Check calculated mappings for redundant dependencies
Rule 7: Source_type field omission
AI Check: source_type field should NOT exist (inferred from context)
Expected: No source_type fields anywhere
AI Analysis: Search entire file for source_type occurrences
Rule 8: Unit field inclusion
AI Check: Units should be at both source level (provider field unit) and top level (Fleeti field unit)
Expected: Include units unless unit is "none" or unitless (boolean, count)
AI Analysis: 
Identify missing units in direct/prioritized mappings
Distinguish between intentional omissions (unitless fields) and errors
Cross-reference with data types to determine if unit omission is correct
4. Mapping Type-Specific Validation (AI Pattern Recognition)
Direct Mappings
AI Pattern: type: direct → single source → no priority → units present
Check: Structure correctness, field presence, optimization compliance
Prioritized Mappings
AI Pattern: type: prioritized → multiple sources → priorities present → units at both levels
Check: Priority ordering, mixed source types, unit consistency
Calculated Mappings
AI Pattern: type: calculated → function reference → parameters.fleeti → no dependencies
Check: Function structure, parameter completeness, unit at top level only
5. Comment Format Validation (AI Text Analysis)
AI Check: Field Path comments present: # Field Path: ...
AI Check: Computation Approach comments present: # Computation Approach: ...
AI Check: Multi-line Computation Approach formatted correctly with # prefix
AI Analysis: Verify comment consistency and formatting
6. Data Type and Error Handling (AI Completeness Check)
AI Check: All mappings have data_type field
AI Check: All mappings have error_handling field
AI Analysis: Identify missing required fields
AI Analysis Methodology
Read Files: Load reference spec and generated YAML(s) into memory
Pattern Matching: Use AI's pattern recognition to identify structures
Semantic Analysis: Understand context and intent (e.g., when unit omission is correct)
Cross-Reference: Compare against reference specification examples
Generate Report: Provide human-readable findings with:
✅ Rules correctly applied (with examples)
⚠️ Potential issues requiring verification (with context)
❌ Actual inconsistencies (with specific line references and fixes)
💡 Recommendations for improvements
Output Format
Provide a comprehensive AI-generated report that includes:

Executive Summary: Overall consistency assessment
Rule-by-Rule Analysis: Detailed findings for each of the 8 rules
Mapping Type Analysis: Validation results by mapping type
Specific Examples: Cite actual field names and line numbers
Recommendations: Actionable fixes for any issues found
Key Advantages of AI Validation
Contextual Understanding: Can determine if missing units are intentional (unitless fields) vs. errors
Pattern Recognition: Identifies subtle inconsistencies across the entire file
Semantic Analysis: Understands the relationship between fields and their meanings
Comprehensive Reporting: Provides detailed explanations, not just pass/fail results