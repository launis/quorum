import sys

def main():
    path = r"c:\src\quorum\client_app_v2\lib\features\studio\views\workflow_builder_view.dart"
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. ADD TAB BAR TO APPBAR
    appbar_actions_end = content.find("          const SizedBox(width: 16),\n        ],\n      ),\n      body: SingleChildScrollView(")
    if appbar_actions_end == -1:
        print("Cannot find AppBar end")
        return
        
    s = content[:appbar_actions_end]
    tail = content[appbar_actions_end:]
    
    # Replace the body start
    tail = tail.replace(
        "        ],\n      ),\n      body: SingleChildScrollView(\n        child: Padding(\n          padding: const EdgeInsets.all(16.0),\n          child: Column(\n            crossAxisAlignment: CrossAxisAlignment.stretch,\n            children: [",
        """        ],\n        bottom: const TabBar(\n          tabs: [\n            Tab(icon: Icon(Icons.settings), text: '1. Yleiset & Tulosteet'),\n            Tab(icon: Icon(Icons.input), text: '2. Syötteet'),\n            Tab(icon: Icon(Icons.account_tree), text: '3. Stepit & Riippuvuudet'),\n          ],\n        ),\n      ),\n      body: TabBarView(\n        children: ["""
    )
    
    content = s + tail

    # 2. Add DefaultTabController wrapping Scaffold
    content = content.replace("    return Scaffold(", "    return DefaultTabController(\n      length: 3,\n      child: Scaffold(")
    # Need to close the DefaultTabController at the end of the build method
    # It ends with: "        ), // Padding\n      ), // SingleChildScrollView\n    );\n  }\n\n  Widget _buildInputCard"
    
    end_pattern = "            ],\n          ),\n        ),\n      ),\n    );\n  }"
    if end_pattern in content:
        content = content.replace(end_pattern, "        ],\n      ),\n    );\n  }")
    else:
        # Fallback approach: just search for the end of the build method.
        # Let's be smart and slice.
        pass

    # Actually, I need to WRAP the 3 sections into SingleChildScrollViews.
    # SECTION 1: Metadata -> ends at line 640 (Output Profiles end)
    # The split is at: "              const SizedBox(height: 24),\n\n              // Expected Inputs"
    
    split_1 = "              const SizedBox(height: 24),\n\n              // Expected Inputs"
    if split_1 not in content:
        print("Cannot find split 1")
    
    content = content.replace(split_1, """              const SizedBox(height: 24),
            ],
          ),
        ),
      ),
      
      // TAB 2: Expected Inputs
      SingleChildScrollView(
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              // Expected Inputs""")
              
    # SECTION 2: Expected Inputs -> ends before "              // Restored Legacy V1 Step List UI"
    split_2 = "              // Restored Legacy V1 Step List UI"
    if split_2 not in content:
        print("Cannot find split 2")
        
    content = content.replace(split_2, """            ],
          ),
        ),
      ),
      
      // TAB 3: Steps & Dependencies
      SingleChildScrollView(
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              // Restored Legacy V1 Step List UI""")
              
    # Re-insert the first Tab wrapper at the very beginning of the children list
    tab_view_start = "      body: TabBarView(\n        children: ["
    content = content.replace(tab_view_start, tab_view_start + """
          // TAB 1: Yleiset & Tulosteet
          SingleChildScrollView(
            child: Padding(
              padding: const EdgeInsets.all(16.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [""")
                
    # Close DefaultTabController at end of build()
    content = content.replace("            ],\n          ),\n        ),\n      ),\n    );\n  }\n\n  Widget _buildInputCard", "            ],\n          ),\n        ),\n      ),\n        ],\n      ),\n    ),\n    );\n  }\n\n  Widget _buildInputCard")

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
        
    print("Successfully patched Tab Layout!")

if __name__ == "__main__":
    main()
