# Workflow 2.0 Full Audit: Step Verification

## Step: step_node_1 (Blueprint: step_input_processing)
**Dependencies:** []
**Input Mappings:** {'inputs': '$inputs'}
**Prompts (in order):**
  1. matrix_input_processing

## Step: step_node_2 (Blueprint: step_guard)
**Dependencies:** ['step_node_1']
**Input Mappings:** {'step_node_1': '$step_node_1.output', 'inputs': '$inputs'}
**Prompts (in order):**
  1. block_globalcontext
  2. block_headermandates
  3. block_mandate5
  4. block_headerrules
  5. block_rule1
  6. block_rule2
  7. block_oprule2
  8. block_headerprotocols
  9. block_protocol2
  10. block_instructionanon
  11. block_instructionnodataleak
  12. block_instructionlanguagefi
  13. block_headerinstructions
  14. matrix_guard
  15. block_taskguard

## Step: step_node_3 (Blueprint: step_retrieval_agent)
**Dependencies:** ['step_node_2']
**Input Mappings:** {'step_node_2': '$step_node_2.output', 'inputs': '$inputs'}
**Prompts (in order):**
  1. block_globalcontext
  2. block_instructionragopt
  3. block_instructionbiblicalgrounding
  4. block_instructionlanguagefi
  5. matrix_retrieval_agent
  6. block_taskretrieval

## Step: step_node_4 (Blueprint: step_analyst)
**Dependencies:** ['step_node_3']
**Input Mappings:** {'step_node_3': '$step_node_3.output', 'inputs': '$inputs'}
**Prompts (in order):**
  1. block_globalcontext
  2. block_headermandates
  3. block_headerrules
  4. block_rule1
  5. block_rule2
  6. block_oprule3
  7. block_headerprotocols
  8. block_protocol3
  9. block_instructionragopt
  10. block_instructionbiblicalgrounding
  11. block_instructionnohallucination
  12. block_instructioncitationobligation
  13. block_instructionlanguagefi
  14. block_headerinstructions
  15. block_taskanalyst
  16. matrix_analyst

## Step: step_node_5 (Blueprint: step_interaction_analyst)
**Dependencies:** ['step_node_4']
**Input Mappings:** {'step_node_4': '$step_node_4.output', 'inputs': '$inputs'}
**Prompts (in order):**
  1. block_globalcontext
  2. block_headermandates
  3. block_mandate5
  4. block_headerrules
  5. block_rule4
  6. block_oprule4
  7. block_headerprotocols
  8. block_protocol1
  9. block_instructionnohallucination
  10. block_instructionlanguagefi
  11. block_headerinstructions
  12. block_taskinteraction
  13. matrix_interaction_analyst

## Step: step_node_6 (Blueprint: step_profiler)
**Dependencies:** ['step_node_5']
**Input Mappings:** {'step_node_5': '$step_node_5.output', 'inputs': '$inputs'}
**Prompts (in order):**
  1. block_globalcontext
  2. block_headermandates
  3. block_mandate2
  4. block_mandate5
  5. block_headerrules
  6. block_rule5
  7. block_heuristic2
  8. block_instructionbiblicalgrounding
  9. block_instructionnohallucination
  10. block_instructionlanguagefi
  11. block_headerinstructions
  12. matrix_kahneman
  13. block_taskprofiler
  14. matrix_profiler

## Step: step_node_7 (Blueprint: step_logician)
**Dependencies:** ['step_node_6']
**Input Mappings:** {'step_node_6': '$step_node_6.output', 'inputs': '$inputs'}
**Prompts (in order):**
  1. block_globalcontext
  2. block_headermandates
  3. block_mandate5
  4. block_headerrules
  5. block_rule3
  6. matrix_toulmin
  7. matrix_bloom
  8. block_instructionbiblicalgrounding
  9. block_instructionnohallucination
  10. block_instructioncitationobligation
  11. block_instructionlanguagefi
  12. block_headerinstructions
  13. block_tasklogician
  14. matrix_logician
  15. block_instructionstrictscale

## Step: step_node_8 (Blueprint: step_falsifier)
**Dependencies:** ['step_node_7']
**Input Mappings:** {'step_node_7': '$step_node_7.output', 'inputs': '$inputs'}
**Prompts (in order):**
  1. block_globalcontext
  2. block_headermandates
  3. block_mandate5
  4. block_headerrules
  5. block_rule5
  6. block_instructionbiblicalgrounding
  7. block_instructionnohallucination
  8. block_instructionlanguagefi
  9. block_headerinstructions
  10. block_taskfalsifier
  11. matrix_falsifier

## Step: step_node_9 (Blueprint: step_causal_analyst)
**Dependencies:** ['step_node_8']
**Input Mappings:** {'step_node_8': '$step_node_8.output', 'inputs': '$inputs'}
**Prompts (in order):**
  1. block_globalcontext
  2. block_headermandates
  3. block_mandate5
  4. block_headerrules
  5. block_rule5
  6. block_instructionbiblicalgrounding
  7. block_instructionnohallucination
  8. block_instructionlanguagefi
  9. block_headerinstructions
  10. block_taskcausal
  11. matrix_causal_analyst

## Step: step_node_10 (Blueprint: step_performativity_detector)
**Dependencies:** ['step_node_9']
**Input Mappings:** {'step_node_9': '$step_node_9.output', 'inputs': '$inputs'}
**Prompts (in order):**
  1. block_globalcontext
  2. block_headermandates
  3. block_mandate5
  4. block_headerrules
  5. block_rule5
  6. block_instructionbiblicalgrounding
  7. block_instructionnohallucination
  8. block_instructionlanguagefi
  9. block_headerinstructions
  10. block_taskperformativity
  11. matrix_goodhart

## Step: step_node_11 (Blueprint: step_overseer)
**Dependencies:** ['step_node_10']
**Input Mappings:** {'step_node_10': '$step_node_10.output', 'inputs': '$inputs'}
**Prompts (in order):**
  1. block_globalcontext
  2. block_headermandates
  3. block_mandate2
  4. block_mandate3
  5. block_mandate5
  6. block_headerrules
  7. block_rule1
  8. block_rule2
  9. block_rule3
  10. block_rule4
  11. block_rule5
  12. block_rule6
  13. block_oprule1
  14. block_oprule2
  15. block_oprule3
  16. block_principle1
  17. block_requirement1
  18. block_heuristic1
  19. block_heuristic2
  20. block_heuristic3
  21. block_protocol4
  22. block_instructionbiblicalgrounding
  23. block_instructionnohallucination
  24. block_instructionlanguagefi
  25. block_headerinstructions
  26. block_taskoverseer
  27. matrix_overseer

## Step: step_node_12 (Blueprint: step_archivist)
**Dependencies:** ['step_node_11']
**Input Mappings:** {'step_node_11': '$step_node_11.output', 'inputs': '$inputs'}
**Prompts (in order):**
  1. block_globalcontext
  2. block_headermandates
  3. block_mandate5
  4. block_headerrules
  5. block_rule5
  6. block_instructionnohallucination
  7. block_instructionlanguagefi
  8. block_headerinstructions
  9. block_taskarchivist
  10. matrix_archivist

## Step: step_node_13 (Blueprint: step_judge)
**Dependencies:** ['step_node_12']
**Input Mappings:** {'step_node_12': '$step_node_12.output', 'inputs': '$inputs'}
**Prompts (in order):**
  1. block_globalcontext
  2. block_headermandates
  3. block_mandate2
  4. block_mandate3
  5. block_mandate5
  6. block_headerrules
  7. block_rule1
  8. block_rule2
  9. block_rule3
  10. block_rule4
  11. block_rule5
  12. block_rule6
  13. block_oprule1
  14. block_oprule2
  15. block_oprule3
  16. block_principle1
  17. block_requirement1
  18. block_heuristic1
  19. block_heuristic2
  20. block_heuristic3
  21. block_instructionlanguagefi
  22. block_instructionstrictscale
  23. block_headerinstructions
  24. block_taskjudge
  25. matrix_judge

## Step: step_node_14 (Blueprint: step_coach)
**Dependencies:** ['step_node_13']
**Input Mappings:** {'step_node_13': '$step_node_13.output', 'inputs': '$inputs'}
**Prompts (in order):**
  1. block_globalcontext
  2. block_headermandates
  3. block_mandate2
  4. block_mandate3
  5. block_mandate5
  6. block_headerrules
  7. block_rule1
  8. block_rule2
  9. block_rule3
  10. block_rule4
  11. block_rule5
  12. block_rule6
  13. block_oprule1
  14. block_oprule2
  15. block_oprule3
  16. block_principle1
  17. block_requirement1
  18. block_heuristic1
  19. block_heuristic2
  20. block_heuristic3
  21. block_instructionlanguagefi
  22. block_instructionstrictscale
  23. block_headerinstructions
  24. block_taskcoach
  25. block_instructioncoachcitation
  26. matrix_coach

## Step: step_node_15 (Blueprint: step_xai_reporter)
**Dependencies:** ['step_node_14']
**Input Mappings:** {'step_node_14': '$step_node_14.output', 'inputs': '$inputs'}
**Prompts (in order):**
  1. block_globalcontext
  2. block_headermandates
  3. block_mandate2
  4. block_mandate3
  5. block_headerrules
  6. block_rule1
  7. block_rule2
  8. block_rule3
  9. block_rule4
  10. block_rule5
  11. block_rule6
  12. block_oprule1
  13. block_oprule2
  14. block_oprule3
  15. block_principle1
  16. block_requirement1
  17. block_heuristic1
  18. block_heuristic2
  19. block_heuristic3
  20. block_instructionlanguagefi
  21. block_headerinstructions
  22. block_taskxai
  23. matrix_xai_reporter

