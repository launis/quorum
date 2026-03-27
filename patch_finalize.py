import re

def main():
    path = r"c:\src\quorum\client_app_v2\lib\features\studio\views\workflow_builder_view.dart"
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Fix the end of build()
    # It currently is:
    #               }),
    #         ],
    #       ),
    #     );
    #   }
    #
    #   Widget _buildInputCard(
    
    # We want it to be:
    #               }),
    #             ],
    #           ),
    #         ),
    #       ),
    #     ],
    #   ),
    # );
    # }
    
    end_pattern = """              }),
        ],
      ),
    );
  }

  Widget _buildInputCard("""
  
    replacement = """              }),
            ],
          ),
        ),
      ),
    ],
  ),
);
}

Widget _buildInputCard("""

    if end_pattern in content:
        content = content.replace(end_pattern, replacement)
    else:
        print("Warning: Couldn't find exact end_pattern, trying alternative")
        alt_pattern = """              }),
        ],
      ),
    );
  }"""
        alt_replacement = """              }),
            ],
          ),
        ),
      ),
    ],
  ),
);
}"""
        if alt_pattern in content:
            content = content.replace(alt_pattern, alt_replacement)

    # 2. Fix _addStep()
    # From: 'id': 'step_${steps.length + 1}',
    # To:   'id': 'step_${DateTime.now().millisecondsSinceEpoch}',
    content = content.replace(
        "'id': 'step_${steps.length + 1}',",
        "'id': 'step_${DateTime.now().millisecondsSinceEpoch}',"
    )
    
    # 3. Fix _buildStepCard ID field
    # From:
    # Expanded(
    #   child: Focus(
    #     onFocusChange: (f) {
    #       if (!f) stepDef['id'] = stepIdController.text;
    #     },
    #     child: TextField(
    #       controller: stepIdController,
    #       decoration: const InputDecoration(
    #         labelText: 'Node ID (e.g. step_1)',
    #       ),
    #     ),
    #   ),
    # ),
    
    old_text_field = """                Expanded(
                  child: Focus(
                    onFocusChange: (f) {
                      if (!f) stepDef['id'] = stepIdController.text;
                    },
                    child: TextField(
                      controller: stepIdController,
                      decoration: const InputDecoration(
                        labelText: 'Node ID (e.g. step_1)',
                      ),
                    ),
                  ),
                ),"""
                
    new_text_field = """                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        'Node ID (Opaque Stripe Pattern)',
                        style: TextStyle(fontSize: 12, color: Colors.grey),
                      ),
                      const SizedBox(height: 4),
                      SelectableText(
                        stepIdController.text,
                        style: const TextStyle(fontFamily: 'monospace', fontWeight: FontWeight.bold),
                      ),
                    ],
                  ),
                ),"""
                
    content = content.replace(old_text_field, new_text_field)
    
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
        
    print("Finalized patch")

if __name__ == "__main__":
    main()
